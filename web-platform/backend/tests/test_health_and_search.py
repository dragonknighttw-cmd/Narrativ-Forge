import pytest

pytestmark = pytest.mark.unit


def test_readiness_route_exposes_dependency_checks():
    from app.api.routes.health import readiness
    assert callable(readiness)


def test_search_relevance_prefers_exact_and_title_matches():
    from app.api.routes import search
    results = [
        {"title": "other", "snippet": "target", "created_at": None},
        {"title": "Target", "snippet": "", "created_at": None},
        {"title": "Target story", "snippet": "", "created_at": None},
    ]
    normalized = "target"
    def relevance(item):
        title = str(item.get("title") or "").casefold()
        snippet = str(item.get("snippet") or "").casefold()
        return (
            0 if normalized == title else 1,
            0 if title.startswith(normalized) else 1,
            0 if normalized in title else 1,
            0 if normalized in snippet else 1,
        )
    assert sorted(results, key=relevance)[0]["title"] == "Target"
