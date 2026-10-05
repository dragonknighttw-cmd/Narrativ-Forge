import time

import pytest
from fastapi import HTTPException

from app.api.routes.cloud_processing import _sign, _verify_signed_payload
from app.core.config import settings


@pytest.mark.unit
def test_signed_whisper_usage_key_round_trips(monkeypatch):
    monkeypatch.setattr(settings, "cloudflare_whisper_shared_secret", "test-secret")
    token = _sign({
        "purpose": "usage",
        "sub": "user-1",
        "episode_id": "episode-1",
        "exp": int(time.time()) + 60,
        "jti": "usage-1",
        "max_audio_seconds": 120,
    })

    claims = _verify_signed_payload(token)

    assert claims["sub"] == "user-1"
    assert claims["episode_id"] == "episode-1"
    assert claims["max_audio_seconds"] == 120


@pytest.mark.unit
def test_unsigned_whisper_usage_key_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "cloudflare_whisper_shared_secret", "test-secret")

    with pytest.raises(HTTPException) as exc:
        _verify_signed_payload("not-a-signed-key")

    assert exc.value.status_code == 400
