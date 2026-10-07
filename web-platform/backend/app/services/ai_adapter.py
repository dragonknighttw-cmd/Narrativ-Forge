from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from ..core.config import settings
from .provider_fallback import run_with_fallback
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


class OpenAICompatibleAdapter:
    """Adapter for OpenAI-compatible chat-completions APIs such as OpenAI and Groq."""
    def __init__(self, provider: ChatProvider) -> None:
        self.provider = provider

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        prompt = ("Create a Burmese short-form video content plan. Return ONLY valid JSON with keys "
                  "hook, script, scenes. scenes must contain scene_number, purpose, description, dialogue, "
                  "duration_seconds. Target about 180 seconds. Idea: " + idea.strip() +
                  "\nCategory: " + (category or "general"))
        response = httpx.post(
            f"{self.provider.base_url.rstrip("/")}/chat/completions",
            headers={"Authorization": f"Bearer {self.provider.api_key}", "Content-Type": "application/json"},
            json={"model": self.provider.model, "messages": [
                {"role": "system", "content": "You are a Burmese short-form video production planner. Output JSON only."},
                {"role": "user", "content": prompt},
            ], "temperature": 0.4, "response_format": {"type": "json_object"}},
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
        try:
            value, provider, attempts = run_with_fallback(operations)
            logger.info("AI content plan generated", extra={"provider": provider, "attempts": [a.provider for a in attempts]})
            return value
        except Exception:
            logger.exception("Configured AI providers failed; using deterministic fallback")
            return self.fallback.create_content_plan(idea=idea, category=category)


def _configured_chat_providers() -> list[ChatProvider]:
    providers: list[ChatProvider] = []
    if settings.groq_api_key:
        providers.append(ChatProvider("groq", settings.groq_api_key, settings.groq_base_url, settings.groq_model, 10))
    if settings.openai_api_key:
        providers.append(ChatProvider("openai", settings.openai_api_key, settings.openai_base_url, settings.openai_model, 20))
    return providers


def get_ai_adapter() -> AIAdapter:
    providers = _configured_chat_providers()
    return RoutedAIAdapter(providers) if providers else MockAIAdapter()
