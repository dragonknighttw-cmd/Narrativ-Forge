from app.api.routes.production_intelligence import HOOK_TYPES, validate_publication_payload


def test_hook_library_supports_all_documented_hook_types():
    assert HOOK_TYPES == {
        "question",
        "shock",
        "mystery",
        "warning",
        "personal_story",
        "contrarian",
        "cliffhanger",
        "number",
    }


def test_publication_validation_rejects_invalid_platform():
    errors = validate_publication_payload("unknown", "caption", [])
    assert "Unsupported platform" in errors
