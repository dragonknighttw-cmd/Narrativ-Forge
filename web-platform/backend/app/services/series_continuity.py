from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesBible:
    title: str
    premise: str
    tone: str
    audience: str
    recurring_elements: tuple[str, ...]
    continuity_rules: tuple[str, ...]


@dataclass(frozen=True)
class ContinuityIssue:
    field: str
    message: str


def build_series_bible(
    title: str,
    premise: str,
    *,
    tone: str = "clear",
    audience: str = "general",
    recurring_elements: list[str] | None = None,
    continuity_rules: list[str] | None = None,
) -> SeriesBible:
    return SeriesBible(
        title=" ".join((title or "").split()).strip(),
        premise=" ".join((premise or "").split()).strip(),
        tone=" ".join((tone or "").split()).strip() or "clear",
        audience=" ".join((audience or "").split()).strip() or "general",
        recurring_elements=tuple(dict.fromkeys(x.strip() for x in (recurring_elements or []) if x.strip())),
        continuity_rules=tuple(dict.fromkeys(x.strip() for x in (continuity_rules or []) if x.strip())),
    )


def check_continuity(bible: SeriesBible, *, title: str, synopsis: str, required_terms: list[str] | None = None) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    safe_title = title or ""
    safe_synopsis = synopsis or ""
    if bible.title and bible.title.lower() not in safe_title.lower() and bible.title.lower() not in safe_synopsis.lower():
        issues.append(ContinuityIssue("series_title", "Episode content does not reference the series identity."))
    haystack = f"{safe_title} {safe_synopsis}".lower()
    for term in required_terms or bible.recurring_elements:
        if term and term.lower() not in haystack:
            issues.append(ContinuityIssue("recurring_element", f"Missing recurring element: {term}"))
    return issues
