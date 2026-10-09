from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from ..core.config import settings
from .provider_fallback import is_retryable_provider_error, run_with_fallback
from .provider_registry import ProviderRegistry, ProviderSpec

logger = logging.getLogger(__name__)


@dataclass
class ContentPlan:
    hook: str
    script: str
    scenes: list[dict]


class AIAdapter(Protocol):
    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        ...


class MockAIAdapter:
    """Deterministic adapter for local development, CI and safe fallback."""
    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        hook = idea.strip()[:120]
        script = f"{idea.strip()}\n\nအဓိကအချက်တွေကို အတိုချုံးရှင်းပြပြီး လူကြည့်သူအတွက် အသုံးဝင်တဲ့အဆုံးသတ်တစ်ခု ပေးမယ်။"
        return ContentPlan(hook=hook, script=script, scenes=[
            {"scene_number": 1, "purpose": "hook", "description": hook, "dialogue": hook, "duration_seconds": 5},
            {"scene_number": 2, "purpose": "body", "description": "Main explanation", "dialogue": script, "duration_seconds": 20},
        ])


@dataclass(frozen=True)
class ChatProvider:
    name: str
    api_key: str
    base_url: str
    model: str
    priority: int


def _extract_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("AI response must be a JSON object")
    return value


def _normalize_plan(value: dict[str, Any], idea: str) -> ContentPlan:
    hook = str(value.get("hook") or idea.strip()[:120]).strip()[:120]
    script = str(value.get("script") or "").strip()
    if not script:
        raise ValueError("AI provider returned an empty script")
    scenes: list[dict] = []
    raw_scenes = value.get("scenes")
    if isinstance(raw_scenes, list):
        for index, item in enumerate(raw_scenes, start=1):
            if not isinstance(item, dict):
                continue
            scenes.append({
                "scene_number": int(item.get("scene_number") or index),
                "purpose": str(item.get("purpose") or ("hook" if index == 1 else "body")),
                "description": str(item.get("description") or item.get("dialogue") or ""),
                "dialogue": str(item.get("dialogue") or item.get("description") or ""),
                "duration_seconds": int(item.get("duration_seconds") or 10),
            })
    if not scenes:
        scenes = [{"scene_number": 1, "purpose": "body", "description": script[:500], "dialogue": script, "duration_seconds": 30}]
    return ContentPlan(hook=hook, script=script, scenes=scenes)


FREE_OPENROUTER_CHAT_MODELS = frozenset({
    "apodex/apodex-1.1-mini:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "poolside/laguna-s-2.1:free",
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    # dots-studio/dots-3-note-preview:free was sunset on 2026-09-30 and is excluded.
})


def _is_free_openrouter_model(model: str) -> bool:
    """Fail closed to vetted chat-capable IDs from the owner's list."""
    normalized = model.strip()
    return normalized == "openrouter/free" or normalized in FREE_OPENROUTER_CHAT_MODELS


class OpenAICompatibleAdapter:
    """Adapter for OpenAI-compatible chat-completions APIs.

    OpenRouter calls are guarded at the last possible point so a bad environment
    value cannot silently route traffic to a paid model.
    """
    def __init__(self, provider: ChatProvider) -> None:
        self.provider = provider

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        if self.provider.name.startswith("openrouter") and not _is_free_openrouter_model(self.provider.model):
            raise ValueError("OpenRouter free-only policy blocked a non-free model")
        prompt = ("Create a Burmese short-form video content plan. Return ONLY valid JSON with keys "
                  "hook, script, scenes. scenes must contain scene_number, purpose, description, dialogue, "
                  "duration_seconds. Target about 180 seconds. Idea: " + idea.strip() +
                  "\nCategory: " + (category or "general"))
        response = httpx.post(
            self.provider.base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {self.provider.api_key}", "Content-Type": "application/json"},
            json={"model": self.provider.model, "messages": [
                {"role": "system", "content": "You are a Burmese short-form video production planner. Output JSON only."},
                {"role": "user", "content": prompt},
            ], "temperature": 0.4},
            timeout=settings.ai_provider_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        content = ((choices[0] if choices else {}).get("message") or {}).get("content")
        if not isinstance(content, str):
            raise ValueError(f"{self.provider.name} returned no text content")
        return _normalize_plan(_extract_json(content), idea)


class RoutedAIAdapter:
    """Choose a configured provider by capability/priority and fail over safely."""
    def __init__(self, providers: list[ChatProvider], fallback: AIAdapter | None = None) -> None:
        self.providers = providers
        self.fallback = fallback or MockAIAdapter()

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        registry = ProviderRegistry()
        for provider in self.providers:
            adapter = OpenAICompatibleAdapter(provider)
            registry.register(ProviderSpec(name=provider.name, capability="script", operation=adapter.create_content_plan, priority=provider.priority))
        operations = [(spec.name, lambda spec=spec: spec.operation(idea=idea, category=category)) for spec in registry.candidates("script")]
        if not operations:
            return self.fallback.create_content_plan(idea=idea, category=category)
        def should_try_next_free_model(exc: BaseException) -> bool:
            # Model retirement / unsupported-model responses should not stop the free-only chain.
            response = getattr(exc, "response", None)
            status = (
                getattr(exc, "status_code", None)
                or getattr(exc, "status", None)
                or getattr(response, "status_code", None)
            )
            if status is not None:
                try:
                    if int(status) in {400, 404, 408, 409, 422, 425, 429, 500, 502, 503, 504}:
                        return True
                    if int(status) in {401, 403}:
                        return False
                except (TypeError, ValueError):
                    pass
            return is_retryable_provider_error(exc)

        try:
            value, provider, attempts = run_with_fallback(
                operations, should_fallback=should_try_next_free_model
            )
            logger.info("AI content plan generated", extra={"provider": provider, "attempts": [a.provider for a in attempts]})
            return value
        except Exception:
            logger.exception("Configured AI providers failed; using deterministic fallback")
            return self.fallback.create_content_plan(idea=idea, category=category)


def _configured_chat_providers() -> list[ChatProvider]:
    """Configure only explicitly free OpenRouter chat models.

    Groq/OpenAI credentials may remain configured for other experiments, but are
    intentionally never used by this production content-generation route.
    """
    if not settings.openrouter_api_key:
        return []

    providers: list[ChatProvider] = []
    models = [item.strip() for item in settings.openrouter_models.split(",") if item.strip()]
    for index, model in enumerate(models):
        if not _is_free_openrouter_model(model):
            logger.error("Skipping non-free OpenRouter model due to free-only policy", extra={"model": model})
            continue
        providers.append(ChatProvider(
            name=f"openrouter-{index + 1}",
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=model,
            priority=index + 1,
        ))
    return providers


def get_ai_adapter() -> AIAdapter:
    providers = _configured_chat_providers()
    return RoutedAIAdapter(providers) if providers else MockAIAdapter()
