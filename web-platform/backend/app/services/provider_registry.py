from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    capability: str
    operation: Callable[..., Any]
    priority: int = 100
    enabled: bool = True


class ProviderRegistry:
    """Small dependency-free registry used by production services to choose adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, list[ProviderSpec]] = {}

    def register(self, spec: ProviderSpec) -> None:
        self._providers.setdefault(spec.capability, []).append(spec)
        self._providers[spec.capability].sort(key=lambda item: item.priority)

    def candidates(self, capability: str) -> list[ProviderSpec]:
        return [item for item in self._providers.get(capability, []) if item.enabled]

    def require(self, capability: str) -> list[ProviderSpec]:
        candidates = self.candidates(capability)
        if not candidates:
            raise LookupError(f"No enabled provider for capability: {capability}")
        return candidates


DEFAULT_CAPABILITIES = {
    "script": ("groq", "agnes"),
    "video": ("agnes", "kling", "magic_hour"),
    "transcription": ("cloudflare_whisper", "local_whisper"),
    "voice": ("edge_tts",),
    "thumbnail": ("image_generator",),
}
