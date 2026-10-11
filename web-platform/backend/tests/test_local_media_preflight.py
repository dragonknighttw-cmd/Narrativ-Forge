from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "local_media_preflight.py"
SPEC = importlib.util.spec_from_file_location("local_media_preflight", SCRIPT_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


def test_redact_url_removes_credentials_and_preserves_target():
    assert (
        preflight.redact_url("redis://user:secret@localhost:6379/0?password=query-secret")
        == "redis://localhost:6379/0"
    )


def test_model_check_is_warning_until_offline_model_is_required(tmp_path):
    optional = preflight.whisper_model_check("small", tmp_path, required=False)
    required = preflight.whisper_model_check("small", tmp_path, required=True)

    assert optional.status == "warn"
    assert required.status == "fail"


def test_model_check_accepts_nonempty_cached_model(tmp_path):
    (tmp_path / "tiny.pt").write_bytes(b"model")

    result = preflight.whisper_model_check("tiny", tmp_path, required=True)

    assert result.status == "pass"


def test_redact_url_handles_invalid_authority():
    assert preflight.redact_url("redis://[invalid") == "<invalid REDIS_URL>"


def test_redis_check_reports_connection_failure_without_credentials(monkeypatch):
    from types import SimpleNamespace

    class RedisError(Exception):
        pass

    class Client:
        def ping(self):
            raise RedisError("connection failed")

    fake_redis = SimpleNamespace(
        Redis=SimpleNamespace(from_url=lambda *args, **kwargs: Client()),
        exceptions=SimpleNamespace(RedisError=RedisError),
    )
    monkeypatch.setitem(sys.modules, "redis", fake_redis)

    result = preflight.redis_check("redis://user:private-token@localhost:6379/0")

    assert result.status == "fail"
    assert "localhost:6379/0" in result.detail
    assert "private-token" not in result.detail
