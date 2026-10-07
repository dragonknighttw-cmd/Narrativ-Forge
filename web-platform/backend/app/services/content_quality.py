from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityReport:
    score: float
    word_count: int
    scene_count: int
    duration_seconds: int
    pacing_ok: bool
    issues: tuple[str, ...]


def assess_content(script: str, scene_durations: list[int | None], target_seconds: int = 180) -> QualityReport:
    text = " ".join((script or "").split())
    durations = [int(value) for value in scene_durations if value is not None and int(value) > 0]
    total = sum(durations)
    issues: list[str] = []
    if not text:
        issues.append("empty_script")
    if len(text.split()) < 80:
        issues.append("script_too_short")
    if not durations:
        issues.append("no_scene_durations")
    elif total < max(30, target_seconds - 30) or total > target_seconds + 30:
        issues.append("duration_out_of_target")
    if durations and max(durations) > 45:
        issues.append("scene_too_long")
    score = max(0.0, min(100.0, 100.0 - len(issues) * 20.0))
    return QualityReport(
        score=score,
        word_count=len(text.split()),
        scene_count=len(durations),
        duration_seconds=total,
        pacing_ok=not any(issue in {"duration_out_of_target", "scene_too_long"} for issue in issues),
        issues=tuple(issues),
    )
