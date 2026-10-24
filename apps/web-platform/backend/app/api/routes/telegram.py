from __future__ import annotations

import html
import hmac
import json
import logging
import re
from uuid import NAMESPACE_URL, uuid5
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import (
    Asset,
    AuditEvent,
    Episode,
    Idea,
    Organization,
    ProcessingJob,
    ReviewRecord,
    Script,
    Subtitle,
)
from ...services.telegram import answer_telegram_callback, send_telegram_message
from ...workers.tasks import enqueue_real_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])
REVIEW_CHECK_KEYS = ("video_watched", "audio_checked", "subtitle_timing_checked", "thumbnail_present")


class TelegramActionPayload(BaseModel):
    action: str = Field(min_length=1, max_length=255)
    event_id: str = Field(min_length=1, max_length=255)
    chat_id: int | str | None = None
    topic_id: int | None = None
    user_id: int | None = None
    username: str | None = Field(default=None, max_length=255)
    raw_message: str | None = Field(default=None, max_length=10000)


def _authorize_gateway(provided_secret: str | None, user_id: int | None) -> None:
    expected = settings.telegram_gateway_secret
    # Accept common Render dashboard formatting (comma/semicolon/newline
    # separated IDs) while keeping the allowlist strict and fail-closed.
    allowed = {
        item.strip().strip("\\'\\\"[]{}()")
        for item in re.split(r"[,;\s]+", settings.telegram_allowed_user_ids)
        if item.strip().strip("\\'\\\"[]{}()")
    }
    if len(expected) < 32 or not allowed:
        raise HTTPException(
            status_code=503,
            detail="Telegram gateway authentication is not configured",
        )
    if not provided_secret or not hmac.compare_digest(provided_secret, expected):
        raise HTTPException(status_code=401, detail="Invalid gateway credentials")
    if user_id is None or str(user_id) not in allowed:
        raise HTTPException(status_code=403, detail="Telegram user is not allowed")


def _event_pk(event_id: str) -> str:
    # The deterministic primary key makes Telegram callback retries idempotent
    # without a separate migration or a best-effort in-memory replay cache.
    return str(uuid5(NAMESPACE_URL, "narrativ-forge:telegram:" + event_id))


def _record_event(
    db: Session,
    *,
    event_pk: str,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: str,
    organization_id: str | None,
    username: str | None,
) -> None:
    db.add(
        AuditEvent(
            id=event_pk,
            organization_id=organization_id,
            actor_email=f"telegram:{user_id}",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=json.dumps(
                {"event_id": event_pk, "username": username},
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        )
    )


@router.post("/webhook")
async def telegram_webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Receive Telegram Bot API updates and dispatch authorized inline-button callbacks."""
    expected = settings.telegram_gateway_secret
    if len(expected) < 32:
        raise HTTPException(status_code=503, detail="Telegram webhook authentication is not configured")
    if (
        not x_telegram_bot_api_secret_token
        or not hmac.compare_digest(x_telegram_bot_api_secret_token, expected)
    ):
        raise HTTPException(status_code=401, detail="Invalid Telegram webhook secret")

    # Route commands by Telegram forum topic. Never treat a command from one
    # project's topic as a command for another project.
    incoming = update.get("message") or update.get("edited_message")
    if isinstance(incoming, dict):
        text = incoming.get("text")
        actor = incoming.get("from") or {}
        chat = incoming.get("chat") or {}
        if isinstance(text, str) and text.strip().startswith("/") and isinstance(actor, dict) and isinstance(chat, dict):
            user_id = actor.get("id")
            command = text.strip().split()[0].split("@", 1)[0].lower()
            topic_id = incoming.get("message_thread_id")
            project_by_topic = {
                6: "Narrativ Forge",
                2: "A Little World With Us",
                5: "Logixa Flow",
                18: "Doka",
                7: "Cognix",
            }
            if command in {"/start", "/help", "/ai_status"}:
                # Diagnostic is deliberately scoped to Narrativ Forge's own
                # configured Telegram chat/topic; never log secrets or message text.
                if str(chat.get("id")) == settings.telegram_chat_id and topic_id == settings.telegram_topic_id:
                    allowed_ids = {
                        item.strip()
                        for item in settings.telegram_allowed_user_ids.replace(";", ",").replace("\\n", ",").split(",")
                        if item.strip()
                    }
                    logger.info(
                        "Narrativ Forge Telegram auth check: chat_match=%s topic_match=%s user_id=%s user_allowed=%s allowed_count=%s",
                        str(chat.get("id")) == settings.telegram_chat_id,
                        topic_id == settings.telegram_topic_id,
                        user_id if isinstance(user_id, int) else "missing",
                        isinstance(user_id, int) and str(user_id) in allowed_ids,
                        len(allowed_ids),
                    )
                try:
                    _authorize_gateway(x_telegram_bot_api_secret_token, user_id if isinstance(user_id, int) else None)
                except HTTPException as exc:
                    if exc.status_code == 403:
                        await send_telegram_message(
                            "⛔ This Telegram account is not authorized to use this project bot.",
                            chat_id=chat.get("id"),
                            topic_id=topic_id if isinstance(topic_id, int) else None,
                        )
                        return {"status": "rejected", "reason": 403}
                    raise

                project_name = project_by_topic.get(topic_id) if isinstance(topic_id, int) else None
                if project_name is None:
                    reply = (
                        "⚠️ <b>Project topic not recognized.</b>\\n"
                        "Please run this command inside one of the configured project topics: "
                        "Narrativ Forge (6), A Little World With Us (2), Logixa Flow (5), Doka (18), or Cognix (7)."
                    )
                elif command in {"/start", "/help"}:
                    reply = (
                        f"🤖 <b>{html.escape(project_name)} — connected to this topic.</b>\\n\\n"
                        "Commands:\\n/start — connect to this project's topic\\n"
                        "/ai_status — check this project's status\\n"
                        "This command reply is scoped to the current topic."
                    )
                elif topic_id == 6:
                    ai_providers = [
                        name for name, enabled in (
                            ("OpenRouter", bool(settings.openrouter_api_key)),
                            ("Groq", bool(settings.groq_api_key and settings.groq_free_tier_enabled)),
                            ("Gemini", bool(settings.gemini_api_key and settings.gemini_free_tier_enabled)),
                            ("Cloudflare Workers AI", bool(settings.cloudflare_account_id and settings.cloudflare_api_token and settings.cloudflare_ai_free_tier_enabled)),
                        ) if enabled
                    ]
                    ai_text = ", ".join(ai_providers) if ai_providers else "No AI provider key is configured as enabled."
                    reply = (
                        "🩺 <b>Narrativ Forge status</b>\\n"
                        f"Telegram notifications: {'enabled' if settings.telegram_enabled else 'disabled'}\\n"
                        f"Telegram credentials: {'configured' if settings.telegram_bot_token.get_secret_value() else 'missing'}\\n"
                        f"AI providers configured: {html.escape(ai_text)}"
                    )
                else:
                    reply = (
                        f"🩺 <b>{html.escape(project_name)} status</b>\\n"
                        "Topic routing is recognized and isolated.\\n"
                        "⚠️ Project-specific AI/service health is not connected to this Narrativ Forge backend, "
                        "so this bot cannot truthfully report that project's provider or workflow health yet."
                    )
                await send_telegram_message(
                    reply,
                    chat_id=chat.get("id"),
                    topic_id=topic_id if isinstance(topic_id, int) else None,
                )
                return {"status": "command_processed", "command": command, "project": project_name}
        return {"status": "ignored"}

    callback = update.get("callback_query")
    if not isinstance(callback, dict):
        # Ignore ordinary messages and update types this endpoint does not process.
        return {"status": "ignored"}

    callback_id = callback.get("id")
    actor = callback.get("from")
    action = callback.get("data")
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    if not isinstance(callback_id, str) or not callback_id or not isinstance(actor, dict):
        raise HTTPException(status_code=400, detail="Malformed Telegram callback")
    if not isinstance(action, str) or not action:
        raise HTTPException(status_code=400, detail="Telegram callback action is missing")
    user_id = actor.get("id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=400, detail="Telegram callback user is missing")

    message_thread_id = message.get("message_thread_id")
    payload = TelegramActionPayload(
        action=action,
        event_id=callback_id,
        chat_id=chat.get("id") if isinstance(chat, dict) else None,
        topic_id=message_thread_id if isinstance(message_thread_id, int) else None,
        user_id=user_id,
        username=actor.get("username") if isinstance(actor.get("username"), str) else None,
        raw_message=message.get("text") if isinstance(message.get("text"), str) else None,
    )
    try:
        result = await handle_telegram_action(
            payload,
            x_telegram_gateway_secret=x_telegram_bot_api_secret_token,
            db=db,
        )
    except HTTPException as exc:
        # Acknowledge user-facing rejections to avoid Telegram retrying a button
        # click indefinitely. Configuration/database failures remain retryable.
        if exc.status_code in {401, 403, 404, 409, 422}:
            await answer_telegram_callback(callback_id, "This action was rejected or is no longer available.", show_alert=True)
            return {"status": "rejected", "reason": exc.status_code}
        raise

    await answer_telegram_callback(callback_id, "Action processed.")
    return result


@router.post("/action")
async def handle_telegram_action(
    payload: TelegramActionPayload,
    x_telegram_gateway_secret: str | None = Header(default=None, alias="X-Telegram-Gateway-Secret"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Apply an authenticated, allowlisted, idempotent Telegram action."""
    _authorize_gateway(x_telegram_gateway_secret, payload.user_id)
    event_pk = _event_pk(payload.event_id)
    previous = db.get(AuditEvent, event_pk)
    if previous:
        return {
            "status": "duplicate",
            "action": previous.action,
            "id": previous.resource_id,
        }

    action = payload.action
    target_id = ""
    target_type = ""
    action_name = ""
    organization_id: str | None = None
    message = ""
    queue_job_id: str | None = None

    try:
        if action.startswith("nf_script_appr:") or action.startswith("nf_script_rej:"):
            approve = action.startswith("nf_script_appr:")
            script_id = action.split(":", 1)[1].strip()
            if not script_id:
                raise HTTPException(status_code=422, detail="Script ID is required")
            script = (
                db.query(Script)
                .join(Episode, Script.episode_id == Episode.id)
                .filter(Script.id == script_id, Script.is_current.is_(True))
                .first()
            )
            if not script:
                raise HTTPException(status_code=404, detail="Current script not found")
            organization_id = script.episode.organization_id
            if approve:
                if script.status not in {"draft", "pending_review", "needs_approval", "ready_for_review"}:
                    raise HTTPException(status_code=409, detail="Script is not awaiting approval")
                script.status = "approved"
                action_name = "telegram.script.approved"
                message = f"✅ <b>Script Approved:</b> <code>{html.escape(script_id)}</code>"
            else:
                if script.status == "approved":
                    raise HTTPException(status_code=409, detail="Approved script cannot be rejected")
                script.status = "revision_requested"
                action_name = "telegram.script.rejected"
                message = f"❌ <b>Script Rejected:</b> <code>{html.escape(script_id)}</code> — marked for revision"
            target_id, target_type = script.id, "script"

        elif action.startswith("nf_video_appr:"):
            asset_id = action.split(":", 1)[1].strip()
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset or asset.asset_type not in {"processed_video", "video"}:
                raise HTTPException(status_code=404, detail="Video asset not found")
            episode = db.query(Episode).filter(Episode.id == asset.episode_id).first()
            review = db.query(ReviewRecord).filter(ReviewRecord.episode_id == asset.episode_id).first()
            subtitle = (
                db.query(Subtitle)
                .filter(Subtitle.episode_id == asset.episode_id, Subtitle.is_current.is_(True))
                .order_by(Subtitle.version.desc())
                .first()
            )
            checklist = json.loads(review.checklist_json or "{}") if review else {}
            issues = json.loads(review.critical_issues_json or "[]") if review else ["missing review"]
            if (
                not episode
                or episode.status != "needs_approval"
                or not review
                or review.decision != "ready"
                or not all(checklist.get(key) is True for key in REVIEW_CHECK_KEYS)
                or issues
                or not subtitle
                or subtitle.status != "approved"
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Video approval blocked: episode review checklist and subtitle approval must pass",
                )
            organization_id = episode.organization_id
            asset.is_final = True
            asset.status = "final"
            episode.status = "approved"
            episode.current_step = "review"
            review.decision = "approved"
            from datetime import datetime, timezone
            review.reviewed_at = datetime.now(timezone.utc)
            action_name = "telegram.video.approved"
            target_id, target_type = asset.id, "asset"
            message = f"👍 <b>Video Approved:</b> <code>{html.escape(asset_id)}</code>"

        elif action.startswith("nf_video_rerun:"):
            asset_id = action.split(":", 1)[1].strip()
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset or asset.asset_type not in {"processed_video", "video"}:
                raise HTTPException(status_code=404, detail="Video asset not found")
            episode = db.query(Episode).filter(Episode.id == asset.episode_id).first()
            if not episode:
                raise HTTPException(status_code=404, detail="Episode not found")
            job = ProcessingJob(
                episode_id=episode.id,
                job_type="real_processing",
                status="queued",
                progress=0,
                input_asset_id=asset.id,
            )
            db.add(job)
            db.flush()
            queue_job_id = job.id
            organization_id = episode.organization_id
            target_id, target_type = job.id, "processing_job"
            action_name = "telegram.video.rerun_queued"
            message = f"🔄 <b>Video re-render queued:</b> <code>{html.escape(asset_id)}</code>"

        elif action == "nf_idea_capture":
            idea_text = (payload.raw_message or "").strip()
            if not idea_text:
                raise HTTPException(status_code=422, detail="Idea text is required")
            organization = (
                db.query(Organization)
                .filter(Organization.slug == settings.supabase_owner_organization_slug)
                .first()
            )
            if not organization:
                raise HTTPException(status_code=503, detail="Default organization is not configured")
            idea = Idea(
                organization_id=organization.id,
                title=idea_text[:255] or "Telegram idea",
                concept=idea_text,
                status="idea",
            )
            db.add(idea)
            db.flush()
            organization_id = organization.id
            target_id, target_type = idea.id, "idea"
            action_name = "telegram.idea.captured"
            message = f"💡 <b>Idea saved:</b> <i>{html.escape(idea_text[:120])}</i>"

        else:
            raise HTTPException(status_code=422, detail="Unsupported Telegram action")

        _record_event(
            db,
            event_pk=event_pk,
            user_id=payload.user_id,  # authorized above
            action=action_name,
            resource_type=target_type,
            resource_id=target_id,
            organization_id=organization_id,
            username=payload.username,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Telegram action failed")
        raise HTTPException(status_code=500, detail="Telegram action failed")

    # Queue only after the transaction is committed. If queueing fails, mark the
    # durable job failed rather than claiming that a render has started.
    if queue_job_id:
        try:
            enqueue_real_job(queue_job_id)
        except Exception:
            logger.exception("Failed to enqueue Telegram-triggered render job")
            job = db.query(ProcessingJob).filter(ProcessingJob.id == queue_job_id).first()
            if job:
                job.status = "failed"
                job.error_code = "QUEUE_UNAVAILABLE"
                job.error_message = "Unable to enqueue render job"
                job.last_error = job.error_message
                db.commit()
            raise HTTPException(status_code=503, detail="Render job was recorded but could not be queued")

    await send_telegram_message(message, topic_id=payload.topic_id)
    logger.info("Applied Telegram action %s for user %s", action_name, payload.user_id)
    return {"status": "ok", "action": action_name, "id": target_id}
