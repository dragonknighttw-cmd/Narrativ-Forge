from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar


T = TypeVar("T")


class ProviderNonRetryableError(RuntimeError):
    """Provider rejected a request that should not be retried automatically."""


@dataclass(frozen=True)
class ProviderAttempt:
    provider: str
    ok: bool
    error: str | None = None


@dataclass(frozen=True)
class ProviderResult:
    value: object
    provider: str
    attempts: tuple[ProviderAttempt, ...]


def is_retryable_provider_error(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if status is not None:
        try:
            return int(status) in {408, 425, 429, 500, 502, 503, 504}
        except (TypeError, ValueError):
            pass
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    return any(token in name or token in message for token in (
        "timeout", "tempor", "rate limit", "too many", "connection", "unavailable", "502", "503", "504",
    ))


def run_with_fallback(
    providers: list[tuple[str, Callable[[], T]]],
    *,
    should_fallback: Callable[[BaseException], bool] = is_retryable_provider_error,
) -> tuple[T, str, tuple[ProviderAttempt, ...]]:
    if not providers:
        raise ValueError("At least one provider is required")

    attempts: list[ProviderAttempt] = []
    last_error: BaseException | None = None
    for name, operation in providers:
        try:
            value = operation()
            attempts.append(ProviderAttempt(provider=name, ok=True))
            return value, name, tuple(attempts)
        except Exception as exc:
            last_error = exc
            attempts.append(ProviderAttempt(provider=name, ok=False, error=str(exc)[:1000]))
            if not should_fallback(exc):
                raise ProviderNonRetryableError(f"Provider {name} failed without a safe fallback: {exc}") from exc

    raise RuntimeError(f"All providers failed: {[item.provider for item in attempts]}") from last_error
