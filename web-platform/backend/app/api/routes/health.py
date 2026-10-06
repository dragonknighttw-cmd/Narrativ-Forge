from __future__ import annotations

import hashlib
import hmac
import io
import json
import smtplib
import tempfile
import time
import uuid
import wave
from pathlib import Path

import httpx
from fastapi import APIRouter, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import SessionLocal
from ...models import GoogleDriveConnection
from ...services.storage import StorageError, get_storage
from ..routes.google_drive import access_token_for

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "narrativ-forge-api"}


def _ok(details: dict) -> dict:
    return {"status": "ok", **details}


def _check_storage(provider: str) -> dict:
    key = f"phase2/verify/{uuid.uuid4().hex}.bin"
    payload = b"Narrativ Forge Phase 2 real infrastructure verification"
    source = Path(tempfile.mkstemp(prefix="nf-phase2-")[1])
    source.write_bytes(payload)
    destination = source.with_name(source.name + ".download")
    try:
        storage = get_storage(provider)
        stored = storage.upload_file(source, key, "application/octet-stream")
        downloaded = storage.download_file(key, destination)
        if downloaded.checksum_sha256 != stored.checksum_sha256 or destination.read_bytes() != payload:
            raise StorageError("download checksum/content mismatch")
        storage.delete(key)
        if storage.exists(key):
            raise StorageError("object still exists after delete")
        return _ok({"provider": provider, "bytes": len(payload), "round_trip": True, "deleted": True})
    except Exception as exc:
        try:
            get_storage(provider).delete(key)
        except Exception:
            pass
        return {"status": "error", "provider": provider, "error": type(exc).__name__ + ": " + str(exc)[:300]}
    finally:
        source.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)


def _check_smtp() -> dict:
    if not settings.smtp_host or not settings.smtp_from_email:
        return {"status": "not_configured"}
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            if settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
        return _ok({"host": settings.smtp_host, "port": settings.smtp_port, "tls": settings.smtp_use_tls})
    except Exception as exc:
        return {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}


def _check_stripe() -> dict:
    if not settings.stripe_secret_key:
        return {"status": "not_configured"}
    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key
        account = stripe.Account.retrieve()
        return _ok({"account_id": account.get("id")})
    except Exception as exc:
        return {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}


def _check_sentry() -> dict:
    if not settings.sentry_dsn.get_secret_value():
        return {"status": "not_configured"}
    try:
        import sentry_sdk
        event_id = sentry_sdk.capture_message("Narrativ Forge Phase 2 verification probe", level="info")
        sentry_sdk.flush(timeout=5)
        return _ok({"event_id": event_id})
    except Exception as exc:
        return {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}


def _make_probe_wav() -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000)
    return stream.getvalue()


def _sign_processing_token(episode_id: str, max_audio_seconds: int) -> str:
    payload = {
        "sub": "phase2-verification",
        "episode_id": episode_id,
        "max_audio_seconds": max_audio_seconds,
        "exp": int(time.time()) + settings.cloudflare_whisper_token_ttl_seconds,
    }
    encoded = __import__("base64").urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    signature = hmac.new(
        settings.cloudflare_whisper_shared_secret.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).digest()
    signed = __import__("base64").urlsafe_b64encode(signature).decode().rstrip("=")
    return encoded + "." + signed


def _check_cloudflare_whisper() -> dict:
    if not settings.cloudflare_whisper_worker_url or not settings.cloudflare_whisper_shared_secret:
        return {"status": "not_configured"}
    episode_id = str(uuid.uuid4())
    try:
        token = _sign_processing_token(episode_id, 1)
        response = httpx.post(
            settings.cloudflare_whisper_worker_url,
            content=_make_probe_wav(),
            headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "audio/wav",
                "X-Narrativ-Episode": episode_id,
            },
            timeout=30,
        )
        if response.status_code >= 400:
            return {"status": "error", "http_status": response.status_code, "error": response.text[:300]}
        body = response.json()
        return _ok({
            "provider": body.get("provider"),
            "model": body.get("model"),
            "word_count": body.get("word_count"),
            "vtt_present": bool(body.get("vtt")),
        })
    except Exception as exc:
        return {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}


def _check_google_drive(db: Session) -> dict:
    item = db.query(GoogleDriveConnection).first()
    if item is None:
        return {"status": "not_connected"}
    try:
        token = access_token_for(item.user_email, item.organization_id, db)
        response = httpx.get(
            "https://www.googleapis.com/drive/v3/about",
            params={"fields": "user(emailAddress,displayName)"},
            headers={"Authorization": "Bearer " + token},
            timeout=20,
        )
        if response.status_code >= 400:
            return {"status": "error", "http_status": response.status_code, "error": response.text[:300]}
        return _ok({"connected_user": response.json().get("user", {}).get("emailAddress")})
    except Exception as exc:
        return {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}


@router.get("/health/phase2")
def phase2_verification(
    x_phase2_verify_token: str | None = Header(default=None, alias="X-Phase2-Verify-Token"),
    phase2_probe: str | None = Query(default=None),
):
    expected = settings.phase2_verify_token.get_secret_value()
    header_ok = bool(expected and x_phase2_verify_token and hmac.compare_digest(x_phase2_verify_token, expected))
    temporary_probe_ok = bool(expected and phase2_probe == hashlib.sha256(expected.encode()).hexdigest()[:24])
    if not header_ok and not temporary_probe_ok:
        raise HTTPException(status_code=404, detail="Not found")

    results: dict[str, dict] = {}
    db = SessionLocal()
    try:
        try:
            db.execute(text("SELECT 1"))
            results["postgres"] = _ok({"query": "SELECT 1"})
        except Exception as exc:
            results["postgres"] = {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300]}

        try:
            if not settings.redis_url:
                results["redis"] = {"status": "not_configured"}
            else:
                import redis
                client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=5, socket_timeout=5)
                results["redis"] = _ok({"ping": bool(client.ping())})
        except Exception as exc:
            results["redis"] = {"status": "error", "error": type(exc).__name__ + ": " + str(exc)[:300], "url_prefix": (settings.redis_url or "")[:12]}

        for provider in ("cloudinary", "supabase", "b2"):
            configured = {
                "cloudinary": bool(settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret),
                "supabase": bool(settings.supabase_url and settings.supabase_service_role_key and settings.supabase_storage_bucket),
                "b2": bool(settings.b2_application_key_id and settings.b2_application_key and settings.b2_bucket_name and settings.b2_region),
            }[provider]
            results[provider] = _check_storage(provider) if configured else {"status": "not_configured"}

        results["cloudflare_whisper"] = _check_cloudflare_whisper()
        results["google_drive"] = _check_google_drive(db)
        results["smtp"] = _check_smtp()
        results["stripe"] = _check_stripe()
        results["sentry"] = _check_sentry()
    finally:
        db.close()

    overall = "ok" if all(item.get("status") in {"ok", "not_connected"} for item in results.values()) else "error"
    return {"status": overall, "checks": results}
