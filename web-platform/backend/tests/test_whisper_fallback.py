import json
from types import SimpleNamespace

import pytest

from app.services import real_processing


@pytest.mark.unit
def test_whisper_falls_back_to_local_cli(monkeypatch, tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"audio-fixture")
    transcript_dir = tmp_path / "whisper"
    transcript_dir.mkdir()
    episode = SimpleNamespace(id="episode-1", organization_id="org-1")

    monkeypatch.setattr(real_processing.settings, "whisper_remote_enabled", True)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_worker_url", "https://whisper.example.test")
    fallback_events = []
    monkeypatch.setattr(real_processing, "_transcribe_cloudflare", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("remote unavailable")))

    def fake_run(command, *, timeout):
        fallback_events.append("local")
        output = transcript_dir / f"{source.stem}.json"
        output.write_text(json.dumps({"text": "fallback"}), encoding="utf-8")
        return None

    monkeypatch.setattr(real_processing, "_run", fake_run)
    db = SimpleNamespace(rollback=lambda: fallback_events.append("rollback"))
    result = real_processing._transcribe_with_fallback(source, transcript_dir, episode, db)
    assert result.is_file()
    assert json.loads(result.read_text(encoding="utf-8"))["text"] == "fallback"
    assert fallback_events == ["rollback", "local"]


@pytest.mark.unit
def test_cloudflare_whisper_uses_signed_bearer_wav_contract(monkeypatch, tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video-fixture")
    transcript_dir = tmp_path / "whisper"
    transcript_dir.mkdir()
    episode = SimpleNamespace(id="episode-42", organization_id="org-42")
    calls = []

    class Query:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

        def all(self):
            return []

    class Db:
        def query(self, model):
            calls.append(("db_query", model))
            return Query()

        def execute(self, statement):
            calls.append(("db_lock", statement))
            return SimpleNamespace(first=lambda: None)

        def add(self, value):
            calls.append(("db_add", value))

        def commit(self):
            calls.append(("db_commit", None))

    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_worker_url", "https://whisper.example.test")
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_shared_secret", "test-secret")
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_token_ttl_seconds", 300)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_daily_neuron_budget", 10000)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_neurons_per_audio_minute", 41.14)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_fallback_threshold", 0.95)
    monkeypatch.setattr(real_processing.settings, "ffprobe_binary", "ffprobe")
    monkeypatch.setattr(real_processing.settings, "ffmpeg_binary", "ffmpeg")

    def fake_run(command, *, timeout):
        if command[0] == "ffprobe":
            return SimpleNamespace(stdout="3.2\n")
        if command[0] == "ffmpeg":
            Path(command[-1]).write_bytes(b"RIFF-WAV")
            return SimpleNamespace(stdout="", stderr="")
        raise AssertionError(command)

    from pathlib import Path
    monkeypatch.setattr(real_processing, "_run", fake_run)

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"text": "မင်္ဂလာပါ", "vtt": "WEBVTT\\n"}

    def fake_post(url, **kwargs):
        calls.append((url, {**kwargs, "body_bytes": kwargs["data"].read()}))
        return Response()

    monkeypatch.setattr(real_processing.requests, "post", fake_post)
    result = real_processing._transcribe_cloudflare(source, transcript_dir, episode, Db())
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["source"] == "cloudflare_whisper"
    assert payload["text"] == "မင်္ဂလာပါ"
    request = next(item for item in calls if item[0] == "https://whisper.example.test")
    lock_index = next(index for index, item in enumerate(calls) if item[0] == "db_lock")
    reservation_index = next(
        index for index, item in enumerate(calls)
        if item[0] == "db_add" and item[1].metric == "cloudflare_whisper_audio_seconds"
    )
    commit_index = next(
        index for index, item in enumerate(calls)
        if item[0] == "db_commit"
    )
    request_index = next(index for index, item in enumerate(calls) if item[0] == "https://whisper.example.test")
    reservation = calls[reservation_index][1]
    assert lock_index < reservation_index < commit_index < request_index
    assert reservation.quantity == 4
    assert reservation.idempotency_key.startswith("cloud-whisper-worker:")
    assert request[1]["headers"]["Content-Type"] == "audio/wav"
    assert request[1]["headers"]["X-Narrativ-Episode"] == "episode-42"
    assert request[1]["headers"]["Authorization"].startswith("Bearer ")
    assert request[1]["body_bytes"] == b"RIFF-WAV"


@pytest.mark.unit
def test_cloudflare_whisper_skips_remote_when_daily_quota_threshold_reached(monkeypatch, tmp_path):
    from pathlib import Path

    source = tmp_path / "source.mp4"
    source.write_bytes(b"video-fixture")
    transcript_dir = tmp_path / "whisper"
    transcript_dir.mkdir()
    episode = SimpleNamespace(id="episode-quota", organization_id="org-quota")
    db_calls = []

    class Query:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    class Db:
        def query(self, model):
            return Query()

        def execute(self, statement):
            db_calls.append(("lock", statement))
            return SimpleNamespace(first=lambda: None)

        def add(self, value):
            db_calls.append(("add", value))

        def commit(self):
            db_calls.append(("commit", None))

    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_worker_url", "https://whisper.example.test")
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_shared_secret", "test-secret")
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_daily_neuron_budget", 100)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_neurons_per_audio_minute", 60)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_fallback_threshold", 0.95)
    monkeypatch.setattr(real_processing.settings, "ffprobe_binary", "ffprobe")
    monkeypatch.setattr(real_processing.settings, "ffmpeg_binary", "ffmpeg")
    monkeypatch.setattr(real_processing, "_daily_whisper_usage_seconds", lambda db, org_id: 91)

    def fake_run(command, *, timeout):
        if command[0] == "ffprobe":
            return SimpleNamespace(stdout="3.2\n")
        if command[0] == "ffmpeg":
            Path(command[-1]).write_bytes(b"RIFF-WAV")
            return SimpleNamespace(stdout="", stderr="")
        raise AssertionError(command)

    monkeypatch.setattr(real_processing, "_run", fake_run)

    def unexpected_post(*args, **kwargs):
        raise AssertionError("remote inference must not run after quota threshold is reached")

    monkeypatch.setattr(real_processing.requests, "post", unexpected_post)

    with pytest.raises(RuntimeError, match="quota requires local fallback"):
        real_processing._transcribe_cloudflare(source, transcript_dir, episode, Db())

    assert any(item[0] == "lock" for item in db_calls)
    assert not any(item[0] == "add" for item in db_calls)
    assert not any(item[0] == "commit" for item in db_calls)
