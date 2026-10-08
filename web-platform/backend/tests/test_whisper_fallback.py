import json

import pytest

from app.services import real_processing


@pytest.mark.unit
def test_whisper_falls_back_to_local_cli(monkeypatch, tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"audio-fixture")
    transcript_dir = tmp_path / "whisper"
    transcript_dir.mkdir()

    monkeypatch.setattr(real_processing.settings, "whisper_remote_enabled", True)
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_worker_url", "https://whisper.example.test")
    monkeypatch.setattr(real_processing.settings, "cloudflare_whisper_shared_secret", "secret")
    monkeypatch.setattr(real_processing.settings, "whisper_remote_timeout_seconds", 5.0)
    monkeypatch.setattr(real_processing.settings, "whisper_command", "whisper")

    class Response:
        def raise_for_status(self):
            raise RuntimeError("remote unavailable")

        def json(self):
            return {}

    monkeypatch.setattr(real_processing.requests, "post", lambda **kwargs: Response())

    def fake_run(command, *, timeout):
        output = transcript_dir / f"{source.stem}.json"
        output.write_text(json.dumps({"text": "fallback"}), encoding="utf-8")
        return None

    monkeypatch.setattr(real_processing, "_run", fake_run)
    result = real_processing._transcribe_with_fallback(source, transcript_dir)
    assert result.is_file()
    assert json.loads(result.read_text(encoding="utf-8"))["text"] == "fallback"
