from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx

from ..core.config import settings
from .provider_fallback import is_retryable_provider_error
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
    return normalized in FREE_OPENROUTER_CHAT_MODELS


def _is_safe_openrouter_base_url(base_url: str) -> bool:
    """Prevent sending the OpenRouter credential to an arbitrary compatible endpoint."""
    parsed = urlparse(base_url.strip())
    return (
        parsed.scheme == "https"
        and parsed.hostname == "openrouter.ai"
        and parsed.port in (None, 443)
        and parsed.path.rstrip("/") == "/api/v1"
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )


def _provider_family(name: str) -> str:
    if name.startswith("openrouter-"):
        return "openrouter"
    return name.split("-", 1)[0].lower()


def _is_safe_compatible_base_url(provider_name: str, base_url: str) -> bool:
    """Never send a provider key to a non-canonical HTTPS endpoint."""
    family = _provider_family(provider_name)
    expected = {
        "groq": ("api.groq.com", "/openai/v1"),
        "gemini": ("generativelanguage.googleapis.com", "/v1beta/openai"),
        "mistral": ("api.mistral.ai", "/v1"),
        "cohere": ("api.cohere.ai", "/compatibility/v1"),
        "nvidia": ("integrate.api.nvidia.com", "/v1"),
    }
    if family == "openrouter":
        return _is_safe_openrouter_base_url(base_url)
    if family not in expected:
        # Unknown adapter names must fail closed to avoid sending credentials
        # to an endpoint that has not been explicitly approved.
        return False
    parsed = urlparse(base_url.strip())
    host, path = expected[family]
    return (
        parsed.scheme == "https"
        and parsed.hostname == host
        and parsed.port in (None, 443)
        and parsed.path.rstrip("/") == path
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )


def _http_status(exc: BaseException) -> int | None:
    response = getattr(exc, "response", None)
    raw = getattr(exc, "status_code", None) or getattr(exc, "status", None) or getattr(response, "status_code", None)
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


class OpenAICompatibleAdapter:
    """Adapter for OpenAI-compatible chat-completions APIs.

    OpenRouter calls are guarded at the last possible point so a bad environment
    value cannot silently route traffic to a paid model.
    """
    def __init__(self, provider: ChatProvider) -> None:
        self.provider = provider

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        if self.provider.name.startswith("openrouter"):
            if not _is_free_openrouter_model(self.provider.model):
                raise ValueError("OpenRouter free-only policy blocked a non-free model")
            if not _is_safe_openrouter_base_url(self.provider.base_url):
                raise ValueError("OpenRouter free-only policy requires HTTPS https://openrouter.ai/api/v1")
        elif not _is_safe_compatible_base_url(self.provider.name, self.provider.base_url):
            raise ValueError("Provider endpoint is not the canonical HTTPS API host")
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


class CloudflareWorkersAIAdapter:
    """Native Workers AI chat adapter; separate from the project's Whisper Worker."""
    def __init__(self, provider: ChatProvider) -> None:
        self.provider = provider

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        parsed = urlparse(self.provider.base_url.strip())
        account_path = parsed.path.rstrip("/")
        if (
            parsed.scheme != "https"
            or parsed.hostname != "api.cloudflare.com"
            or parsed.port not in (None, 443)
            or parsed.query
            or parsed.fragment
            or parsed.username
            or parsed.password
            or not re.fullmatch(r"/client/v4/accounts/[a-fA-F0-9]{32}/ai/run", account_path)
            or not re.fullmatch(r"@cf/[A-Za-z0-9._/-]+", self.provider.model)
        ):
            raise ValueError("Cloudflare Workers AI requires a canonical HTTPS account endpoint and @cf model")

        prompt = (
            "Create a Burmese short-form video content plan. Return ONLY valid JSON with keys "
            "hook, script, scenes. scenes must contain scene_number, purpose, description, dialogue, "
            "duration_seconds. Target about 180 seconds. Idea: " + idea.strip()
            + "\nCategory: " + (category or "general")
        )
        response = httpx.post(
            self.provider.base_url.rstrip("/") + "/" + self.provider.model,
            headers={"Authorization": f"Bearer {self.provider.api_key}", "Content-Type": "application/json"},
            json={"messages": [
                {"role": "system", "content": "You are a Burmese short-form video production planner. Output JSON only."},
                {"role": "user", "content": prompt},
            ], "max_tokens": 1400},
            timeout=settings.ai_provider_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Cloudflare Workers AI returned a non-object response")
        if payload.get("success") is False:
            raise ValueError("Cloudflare Workers AI reported an unsuccessful inference")
        result = payload.get("result")
        content = result.get("response") if isinstance(result, dict) else None
        if not isinstance(content, str):
            raise ValueError("Cloudflare Workers AI returned no text content")
        return _normalize_plan(_extract_json(content), idea)


class RoutedAIAdapter:
    """Choose a configured provider by capability/priority and fail over safely."""
    def __init__(self, providers: list[ChatProvider], fallback: AIAdapter | None = None) -> None:
        self.providers = providers
        self.fallback = fallback or MockAIAdapter()

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        registry = ProviderRegistry()
        for provider in self.providers:
            adapter = (
                CloudflareWorkersAIAdapter(provider)
                if provider.name == "cloudflare-ai"
                else OpenAICompatibleAdapter(provider)
            )
            registry.register(ProviderSpec(
                name=provider.name,
                capability="script",
                operation=adapter.create_content_plan,
                priority=provider.priority,
            ))
        candidates = registry.candidates("script")
        if not candidates:
            return self.fallback.create_content_plan(idea=idea, category=category)

        attempts: list[str] = []
        index = 0
        while index < len(candidates):
            spec = candidates[index]
            try:
                value = spec.operation(idea=idea, category=category)
                attempts.append(spec.name + ":ok")
                logger.info("AI content plan generated", extra={"provider": spec.name, "attempts": attempts})
                return value
            except Exception as exc:
                status = _http_status(exc)
                attempts.append(f"{spec.name}:failed:{status or type(exc).__name__}")
                family = _provider_family(spec.name)

                # Authentication failures and 429s usually apply to the whole key/account.
                # Skip other models on that provider before trying the next provider.
                if status in {401, 403, 429}:
                    logger.warning(
                        "AI provider family unavailable; moving to next provider",
                        extra={"provider_family": family, "http_status": status},
                    )
                    index += 1
                    while index < len(candidates) and _provider_family(candidates[index].name) == family:
                        index += 1
                    continue

                retryable_statuses = {400, 404, 408, 409, 422, 425, 500, 502, 503, 504}
                if isinstance(exc, ValueError) or status in retryable_statuses or is_retryable_provider_error(exc):
                    logger.warning(
                        "AI model attempt failed; trying next configured candidate",
                        extra={"provider": spec.name, "http_status": status, "error_type": type(exc).__name__},
                    )
                    index += 1
                    continue

                logger.error(
                    "AI provider failed with a non-retryable error",
                    extra={"provider": spec.name, "error_type": type(exc).__name__},
                )
                break

        logger.error("All configured AI providers failed; using deterministic fallback", extra={"attempts": attempts})
        return self.fallback.create_content_plan(idea=idea, category=category)


def _configured_chat_providers() -> list[ChatProvider]:
    """Build a free-first chain, opting in to non-OpenRouter account tiers explicitly."""
    providers: list[ChatProvider] = []
    priority = 1

    if settings.openrouter_api_key:
        models = [item.strip() for item in settings.openrouter_models.split(",") if item.strip()]
        for model in models:
            if not _is_free_openrouter_model(model):
                logger.warning(
                    "Skipping non-allowlisted OpenRouter model due to free-only policy",
                    extra={"model": model},
                )
                continue
            providers.append(ChatProvider(
                name=f"openrouter-{priority}",
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                model=model,
                priority=priority,
            ))
            priority += 1

    # Groq follows OpenRouter. It is enabled only after the owner confirms the free tier.
    if settings.groq_api_key and settings.groq_free_tier_enabled:
        providers.append(ChatProvider(
            name="groq",
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            model=settings.groq_model,
            priority=priority,
        ))
        priority += 1

    # Workers AI chat needs its own account ID/API token; the Whisper shared secret is unrelated.
    if (
        settings.cloudflare_account_id
        and settings.cloudflare_api_token
        and settings.cloudflare_ai_free_tier_enabled
    ):
        providers.append(ChatProvider(
            name="cloudflare-ai",
            api_key=settings.cloudflare_api_token,
            base_url=f"https://api.cloudflare.com/client/v4/accounts/{settings.cloudflare_account_id}/ai/run",
            model=settings.cloudflare_ai_model,
            priority=priority,
        ))
        priority += 1

    # These APIs can have account-specific trial/free quotas. Do not call them just
    # because a key exists: the owner must explicitly confirm the intended free tier.
    configured = [
        ("gemini", settings.gemini_api_key, settings.gemini_base_url, settings.gemini_model, settings.gemini_free_tier_enabled),
        ("mistral", settings.mistral_api_key, settings.mistral_base_url, settings.mistral_model, settings.mistral_free_tier_enabled),
        ("cohere", settings.cohere_api_key, settings.cohere_base_url, settings.cohere_model, settings.cohere_free_tier_enabled),
        ("nvidia", settings.nvidia_api_key, settings.nvidia_base_url, settings.nvidia_model, settings.nvidia_free_tier_enabled),
    ]
    for name, api_key, base_url, model, free_tier_enabled in configured:
        if not api_key or not free_tier_enabled:
            continue
        providers.append(ChatProvider(
            name=name,
            api_key=api_key,
            base_url=base_url,
            model=model,
            priority=priority,
        ))
        priority += 1

    return providers


def get_ai_adapter() -> AIAdapter:
    providers = _configured_chat_providers()
    return RoutedAIAdapter(providers) if providers else MockAIAdapter()
