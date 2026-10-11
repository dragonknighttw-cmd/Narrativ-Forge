import io
import json
import urllib.error
from email.message import Message

import pytest

from scripts import openrouter_free_model_smoke as smoke


MODEL = "google/gemma-4-31b-it:free"
VALID_CONTENT = json.dumps(
    {"hook": "မင်္ဂလာပါ", "script": "စမ်းသပ်စာသား", "scenes": [{"title": "boat"}]},
    ensure_ascii=False,
)


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


def _patch_urlopen(monkeypatch, response=None, error=None):
    def fake_urlopen(request, timeout):
        assert request.full_url == "https://openrouter.ai/api/v1/chat/completions"
        assert timeout == 45
        assert request.get_header("Authorization") == "Bearer unit-test-secret"
        if error:
            raise error
        return response

    monkeypatch.setattr(smoke.urllib.request, "urlopen", fake_urlopen)


@pytest.mark.unit
def test_smoke_records_valid_json_and_redacted_usage(monkeypatch):
    _patch_urlopen(
        monkeypatch,
        response=FakeResponse(
            {
                "choices": [{"finish_reason": "stop", "message": {"content": VALID_CONTENT}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 20, "total_tokens": 32},
            }
        ),
    )
    result = smoke.run(MODEL, "unit-test-secret")
    assert result["success"] is True
    assert result["validation"] == "content_plan_json_valid"
    assert result["finish_reason"] == "stop"
    assert result["response_chars"] == len(VALID_CONTENT)
    assert result["total_tokens"] == 32
    assert "content" not in result
    assert "unit-test-secret" not in json.dumps(result)


@pytest.mark.unit
def test_smoke_records_429_retry_after_and_safe_provider_codes(monkeypatch):
    headers = Message()
    headers["Retry-After"] = "37"
    body = json.dumps(
        {"error": {"code": 429, "type": "rate_limit_error", "message": "secret prompt or provider detail"}}
    ).encode()
    error = urllib.error.HTTPError(
        "https://openrouter.ai/api/v1/chat/completions",
        429,
        "Too Many Requests",
        headers,
        io.BytesIO(body),
    )
    _patch_urlopen(monkeypatch, error=error)
    result = smoke.run(MODEL, "unit-test-secret")
    assert result["http_status"] == 429
    assert result["error_code"] == "http_429"
    assert result["provider_error_code"] == "429"
    assert result["error_type"] == "rate_limit_error"
    assert result["retry_after_seconds"] == 37
    assert "message" not in result
    assert "secret prompt" not in json.dumps(result)
    assert "unit-test-secret" not in json.dumps(result)


@pytest.mark.unit
def test_smoke_marks_empty_response_without_saving_body(monkeypatch):
    _patch_urlopen(monkeypatch, response=FakeResponse({"choices": [{"message": {"content": ""}}]}))
    result = smoke.run(MODEL, "unit-test-secret")
    assert result["success"] is False
    assert result["validation"] == "empty_response"
    assert result["response_chars"] == 0


@pytest.mark.unit
def test_smoke_marks_truncated_or_invalid_json(monkeypatch):
    _patch_urlopen(
        monkeypatch,
        response=FakeResponse({"choices": [{"message": {"content": '{"hook":"unfinished"'}}]}),
    )
    result = smoke.run(MODEL, "unit-test-secret")
    assert result["success"] is False
    assert result["validation"] == "content_plan_json_invalid"
    assert result["error_code"] == "invalid_api_json"


@pytest.mark.unit
def test_smoke_rejects_non_allowlisted_model_before_network(monkeypatch):
    def unexpected(*_args, **_kwargs):
        raise AssertionError("network must not be called for a non-allowlisted model")

    monkeypatch.setattr(smoke.urllib.request, "urlopen", unexpected)
    with pytest.raises(ValueError, match="model_not_allowlisted"):
        smoke.run("some-paid-model", "unit-test-secret")


@pytest.mark.unit
def test_retry_after_date_is_parsed_and_capped():
    assert smoke._retry_after_seconds("120") == 120
    assert smoke._retry_after_seconds("not a date") is None
    assert smoke._retry_after_seconds("999999") == 86400



@pytest.mark.unit
def test_smoke_records_auth_failure_without_leaking_provider_message(monkeypatch):
    headers = Message()
    body = json.dumps(
        {"error": {"code": "invalid_api_key", "type": "authentication_error", "message": "do-not-log-this"}}
    ).encode()
    error = urllib.error.HTTPError(
        "https://openrouter.ai/api/v1/chat/completions",
        401,
        "Unauthorized",
        headers,
        io.BytesIO(body),
    )
    calls = []
    def fake_urlopen(request, timeout):
        calls.append(1)
        raise error
    monkeypatch.setattr(smoke.urllib.request, "urlopen", fake_urlopen)

    result = smoke.run(MODEL, "unit-test-secret")
    assert result["http_status"] == 401
    assert result["success"] is False
    assert result["error_code"] == "http_401"
    assert result["provider_error_code"] == "invalid_api_key"
    assert len(calls) == 1
    serialized = json.dumps(result)
    assert "do-not-log-this" not in serialized
    assert "unit-test-secret" not in serialized


@pytest.mark.unit
def test_extract_json_accepts_fenced_object_but_still_validates_required_fields():
    parsed = smoke.extract_json('\\x60\\x60\\x60json\\n{"hook":"h","script":"s","scenes":[{}]}\\n\\x60\\x60\\x60')
    assert parsed["hook"] == "h"
    with pytest.raises(ValueError, match="missing_script"):
        smoke.extract_json('{"hook":"h","scenes":[{}]}')


@pytest.mark.unit
def test_success_http_status_with_non_object_payload_is_not_success(monkeypatch):
    _patch_urlopen(monkeypatch, response=FakeResponse(["not", "an", "object"]))
    result = smoke.run(MODEL, "unit-test-secret")
    assert result["http_status"] == 200
    assert result["success"] is False
    assert result["error_code"] == "api_payload_not_object"
