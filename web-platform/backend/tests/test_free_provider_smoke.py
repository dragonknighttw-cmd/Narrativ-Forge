import json
import sys
from pathlib import Path

import pytest

from app.services.ai_adapter import ChatProvider, ContentPlan


pytestmark = pytest.mark.unit
SCRIPT = Path(__file__).parents[1] / "scripts" / "free_provider_smoke.py"


def test_smoke_requires_explicit_free_tier_confirmation(monkeypatch, tmp_path, capsys):
    import runpy

    output = tmp_path / "evidence.json"
    monkeypatch.setenv("CONFIRM_FREE_TIER", "false")
    monkeypatch.setattr(sys, "argv", ["free_provider_smoke.py", "--provider", "gemini", "--output", str(output)])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert exc.value.code == 2
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["error_code"] == "free_tier_confirmation_required"
    assert result["request_sent"] is False
    assert "api_key" not in capsys.readouterr().out.lower()


def test_smoke_records_only_redacted_success_metadata(monkeypatch, tmp_path, capsys):
    import runpy
    from app.services import ai_adapter

    secret = "DO_NOT_PRINT_TEST_SECRET"
    private_response = "DO_NOT_PRINT_GENERATED_TEXT"
    output = tmp_path / "evidence.json"
    provider = ChatProvider("gemini", secret, "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-test-model", 1)

    class FakeAdapter:
        def __init__(self, selected):
            assert selected.api_key == secret

        def create_content_plan(self, **kwargs):
            return ContentPlan("synthetic hook", private_response, [{"scene_number": 1}])

    monkeypatch.setenv("CONFIRM_FREE_TIER", "true")
    monkeypatch.setattr(ai_adapter, "_configured_chat_providers", lambda: [provider])
    monkeypatch.setattr(ai_adapter, "OpenAICompatibleAdapter", FakeAdapter)
    monkeypatch.setattr(sys, "argv", ["free_provider_smoke.py", "--provider", "gemini", "--output", str(output)])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert exc.value.code == 0
    evidence = output.read_text(encoding="utf-8")
    stdout = capsys.readouterr().out
    assert json.loads(evidence)["success"] is True
    assert json.loads(evidence)["script_chars"] == len(private_response)
    assert secret not in evidence and secret not in stdout
    assert private_response not in evidence and private_response not in stdout
