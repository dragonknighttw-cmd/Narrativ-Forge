from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Protocol


HOOK_TYPES = (
    "question",
    "curiosity_gap",
    "bold_claim",
    "story",
    "problem_solution",
    "number",
    "contrast",
    "challenge",
)


@dataclass(frozen=True)
class ProductionMetadata:
    title: str
    description: str
    hashtags: tuple[str, ...]
    thumbnail_text: str
    thumbnail_prompt: str
    sound_plan: dict
    platform_exports: dict


@dataclass(frozen=True)
class BatchItem:
    key: str
    scheduled_at: datetime
    platform: str
    status: str = "planned"


@dataclass(frozen=True)
class ABVariant:
    key: str
    hook: str
    thumbnail_text: str


def build_seo_metadata(title: str, topic: str, keywords: list[str] | None = None) -> dict:
    clean_title = " ".join(title.split()).strip()[:120] or "Narrativ Forge"
    clean_topic = " ".join(topic.split()).strip()[:300]
    terms = []
    for value in keywords or []:
        value = " ".join(str(value).split()).strip().lstrip("#")
        if value and value not in terms:
            terms.append(value[:80])
    hashtags = tuple(f"#{re.sub(r'[^0-9A-Za-z\u1000-\u109F]+', '', value)}" for value in terms[:8])
    hashtags = tuple(tag for tag in hashtags if tag != "#")
    return {
        "title": clean_title,
        "description": clean_topic,
        "hashtags": hashtags,
    }


def build_thumbnail_plan(title: str, hook: str) -> dict:
    text = " ".join((hook or title).split()).strip()
    text = text[:42] + ("…" if len(text) > 42 else "")
    return {
        "text": text,
        "aspect_ratio": "9:16",
        "safe_area": "center",
        "prompt": f"Vertical Burmese short-form thumbnail, high-contrast subject, clear Burmese headline: {text}",
    }


def build_sound_plan(category: str | None = None) -> dict:
    return {
        "category": category or "general",
        "voice": "primary",
        "bgm": "low",
        "ducking_db": -12,
        "avoid_clipping": True,
        "commercial_safe_required": True,
    }


PLATFORM_EXPORT_LIMITS = {
    "tiktok": {"aspect_ratio": "9:16", "max_duration_seconds": 600},
    "youtube_shorts": {"aspect_ratio": "9:16", "max_duration_seconds": 180},
    "facebook_reels": {"aspect_ratio": "9:16", "max_duration_seconds": 180},
}


def build_cross_platform_export_plan(duration_seconds: int = 180) -> dict:
    duration = max(1, int(duration_seconds))
    plan = {
        platform: {
            "aspect_ratio": spec["aspect_ratio"],
            "max_duration_seconds": min(duration, spec["max_duration_seconds"]),
            "source_duration_seconds": duration,
            "requires_trim": duration > spec["max_duration_seconds"],
        }
        for platform, spec in PLATFORM_EXPORT_LIMITS.items()
    }
    plan["master"] = {
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "duration_seconds": duration,
    }
    return plan


def validate_cross_platform_export_plan(plan: dict) -> list[str]:
    errors = []
    for platform, spec in PLATFORM_EXPORT_LIMITS.items():
        item = plan.get(platform)
        if not isinstance(item, dict):
            errors.append(f"missing:{platform}")
            continue
        if item.get("aspect_ratio") != spec["aspect_ratio"]:
            errors.append(f"{platform}:aspect_ratio")
        duration = int(item.get("max_duration_seconds") or 0)
        if duration < 1 or duration > spec["max_duration_seconds"]:
            errors.append(f"{platform}:duration")
    master = plan.get("master") or {}
    if master.get("aspect_ratio") != "9:16":
        errors.append("master:aspect_ratio")
    if master.get("resolution") != "1080x1920":
        errors.append("master:resolution")
    return errors


@dataclass(frozen=True)
class TrendSignal:
    topic: str
    score: float
    source: str
    observed_at: datetime
    expires_at: datetime | None = None


class TrendProvider(Protocol):
    def fetch(self, topic: str | None = None) -> list[TrendSignal]:
        ...


def rank_trend_signals(signals: list[TrendSignal], *, now: datetime | None = None, limit: int = 10) -> list[TrendSignal]:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    current = now or datetime.now(timezone.utc)
    eligible = [
        signal for signal in signals
        if signal.expires_at is None or signal.expires_at > current
    ]
    return sorted(eligible, key=lambda signal: (-signal.score, signal.topic.lower(), signal.source))[:limit]


def build_production_metadata(title: str, topic: str, hook: str, keywords: list[str] | None = None, category: str | None = None) -> ProductionMetadata:
    seo = build_seo_metadata(title, topic, keywords)
    thumbnail = build_thumbnail_plan(title, hook)
    return ProductionMetadata(
        title=seo["title"],
        description=seo["description"],
        hashtags=seo["hashtags"],
        thumbnail_text=thumbnail["text"],
        thumbnail_prompt=thumbnail["prompt"],
        sound_plan=build_sound_plan(category),
        platform_exports=build_cross_platform_export_plan(),
    )


def plan_batch(items: list[dict], *, platform: str = "youtube_shorts", start_at: datetime | None = None, interval_minutes: int = 60) -> list[BatchItem]:
    if interval_minutes < 1:
        raise ValueError("interval_minutes must be >= 1")
    cursor = start_at or datetime.now(timezone.utc)
    result = []
    for index, item in enumerate(items):
        key = str(item.get("key") or item.get("episode_id") or index)
        result.append(BatchItem(key=key, scheduled_at=cursor, platform=platform))
        from datetime import timedelta
        cursor = cursor + timedelta(minutes=interval_minutes)
    return result


def build_ab_variants(hooks: list[str], thumbnail_texts: list[str]) -> list[ABVariant]:
    count = min(len(hooks), len(thumbnail_texts))
    return [
        ABVariant(key=f"variant-{index + 1}", hook=hooks[index], thumbnail_text=thumbnail_texts[index])
        for index in range(count)
    ]


@dataclass(frozen=True)
class ProductionReadiness:
    quality_score: float
    quality_issues: tuple[str, ...]
    continuity_issues: tuple[str, ...]
    ready_for_review: bool


@dataclass(frozen=True)
class ABOutcome:
    variant_key: str
    impressions: int
    views: int
    completions: int
    shares: int = 0


def score_ab_outcome(outcome: ABOutcome) -> float:
    if outcome.impressions <= 0:
        return 0.0
    view_rate = outcome.views / outcome.impressions
    completion_rate = outcome.completions / max(outcome.views, 1)
    share_rate = outcome.shares / max(outcome.views, 1)
    return (view_rate * 0.45) + (completion_rate * 0.45) + (share_rate * 0.10)


def rank_ab_outcomes(outcomes: list[ABOutcome]) -> list[ABOutcome]:
    return sorted(outcomes, key=lambda item: (-score_ab_outcome(item), item.variant_key))


def assess_production_readiness(
    *,
    script: str,
    scene_durations: list[int | None],
    target_seconds: int = 180,
    continuity_issues: list[str] | None = None,
) -> ProductionReadiness:
    from .content_quality import assess_content

    quality = assess_content(script, scene_durations, target_seconds)
    continuity = tuple(continuity_issues or ())
    return ProductionReadiness(
        quality_score=quality.score,
        quality_issues=quality.issues,
        continuity_issues=continuity,
        ready_for_review=quality.score >= 80 and not continuity,
    )
