from __future__ import annotations

import html
import hmac

import httpx
import json
import logging
import os
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
from ...services.manga_engine import MangaEngine, LayoutType
from ...services.video_composer import VideoComposerService, VideoSourceProvider
from ...workers.tasks import enqueue_real_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])
REVIEW_CHECK_KEYS = ("video_watched", "audio_checked", "subtitle_timing_checked", "thumbnail_present")


def _dashboard_keyboard() -> list[list[dict[str, str]]] | None:
    """Return the one consistent dashboard button used by command replies."""
    url = settings.frontend_base_url.strip()
    if not url.startswith(("https://", "http://")):
        return None
    return [[{"text": "🎬 Open Flow Dashboard", "url": url}]]


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


def _narrativ_organization_id(db: Session) -> str:
    """Resolve the one organization owned by this dedicated Narrativ bot."""
    organization_id = (
        db.query(Organization.id)
        .filter(Organization.slug == settings.supabase_owner_organization_slug)
        .scalar()
    )
    if not organization_id:
        raise RuntimeError("Narrativ Forge organization is not configured")
    return str(organization_id)


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
            command_token = text.strip().split()[0]
            command, separator, addressed_username = command_token.partition("@")
            command = command.lower()
            configured_username = os.getenv("TELEGRAM_BOT_USERNAME", "NarrativForgeBot").lstrip("@").casefold()
            # Explicitly addressed commands belong only to the named bot.
            # Do not let Narrativ Forge answer another bot's command.
            if separator and addressed_username.casefold() != configured_username:
                return {"status": "ignored", "reason": "command_addressed_to_another_bot"}
            topic_id = incoming.get("message_thread_id")
            # One bot serves the shared forum, but only Narrativ Forge topic 6
            # is connected to this backend's project data and approval actions.
            # Other topics receive only isolated connection/status replies.
            project_by_topic = {
                6: "Narrativ Forge",
                2: "A Little World With Us",
                5: "Logixa Flow",
                18: "Doka",
                7: "Cognix",
                215: "AuraCraft Studio",
            }
            if str(chat.get("id")) != settings.telegram_chat_id or not isinstance(topic_id, int) or topic_id not in project_by_topic:
                return {"status": "ignored", "reason": "unrecognized_chat_or_topic"}
            if command in {"/start", "/help", "/commands", "/status", "/ai_status", "/ai_test", "/idea", "/drafts", "/ideas", "/episodes", "/pipeline", "/assets", "/reviews", "/metrics", "/manga", "/clip"}:
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
                # Telegram reports anonymous group-admin commands as the
                # synthetic GroupAnonymousBot user (1087968824), not the human
                # account. Never add that synthetic ID to the allowlist: it would
                # bypass per-user authorization. Explain the fix only in this
                # project's configured chat/topic.
                if (
                    user_id == 1087968824
                    and str(chat.get("id")) == settings.telegram_chat_id
                    and topic_id == settings.telegram_topic_id
                ):
                    await send_telegram_message(
                        "⚠️ Telegram က ဒီ command ကို သင့်ကိုယ်ပိုင် account ID နဲ့မပို့ဘဲ "
                        "anonymous admin (GroupAnonymousBot) အဖြစ်ပို့နေပါတယ်။ "
                        "ဒီ project bot ကို သုံးဖို့ group settings → Administrators → "
                        "သင့် account → Remain Anonymous ကို ခဏပိတ်ပြီး /start ကို ပြန်ပို့ပါ။ "
                        "သင့်ကိုယ်ပိုင် user ID ကို allowlist ထဲမှာပဲ ဆက်စစ်ထားမှာဖြစ်ပြီး "
                        "anonymous ID ကို ခွင့်မပြုပါ။",
                        chat_id=chat.get("id"),
                        topic_id=topic_id if isinstance(topic_id, int) else None,
                    )
                    return {"status": "rejected", "reason": "anonymous_admin"}
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
                    logger.warning(
                        "Telegram project topic not recognized: chat_id=%s topic_id=%s topic_type=%s command=%s",
                        chat.get("id"),
                        topic_id,
                        type(topic_id).__name__,
                        command,
                    )
                    detected_topic = (
                        str(topic_id) if isinstance(topic_id, int) else "မတွေ့ပါ (General topic သို့မဟုတ် topic metadata မပါ)"
                    )
                    reply = (
                        "⚠️ <b>Project topic ကို မသိရှိနိုင်ပါ။</b>\n"
                        f"Telegram က လက်ခံရရှိတဲ့ message_thread_id: <code>{html.escape(detected_topic)}</code>\n"
                        "ဒီ command ကို Narrativ Forge ရဲ့ topic ထဲမှာ ပို့ထားကြောင်း စစ်ပါ။ "
                        "မမှန်သေးရင် ဒီ ID ကို support အတွက် အသုံးပြုနိုင်ပါတယ်။\n"
                        "Configured topics: Narrativ Forge (6), A Little World With Us (2), "
                        "Logixa Flow (5), Doka (18), Cognix (7), AuraCraft Studio (215)."
                    )
                elif command in {"/start", "/help", "/commands"}:
                    if topic_id == 6:
                        reply = (
                            f"🤖 <b>{html.escape(project_name)} — connected to this topic.</b>\n\n"
                            "Commands:\n/start — connect to this project's topic\n"
                            "/commands — list available commands\n"
                            "/status or /ai_status — check configured AI providers\n"
                            "/ai_test — send a test request to OpenRouter\n"
                            "/idea <text> — save an idea to Narrativ Forge\n"
                            "/drafts — view active script drafts\n"
                            "/ideas — view recent ideas\n"
                            "/episodes — view recent episodes\n"
                            "/pipeline — view active processing jobs\n"
                            "/assets — view recent assets\n"
                            "/reviews — view recent reviews\n"
                            "/metrics — content production metrics\n"
                            "/manga and /clip — create storyboard/clip records\n"
                            "This command reply is scoped to the current topic."
                        )
                    else:
                        reply = (
                            f"🤖 <b>{html.escape(project_name)} — connected to this topic.</b>\n\n"
                            "Available commands: /start, /status, /ai_status.\n"
                            "This topic is isolated from Narrativ Forge project data; its own AI/workflow "
                            "integrations are not connected to this backend."
                        )
                elif command == "/ai_test":
                    if topic_id != 6:
                        reply = "⛔ /ai_test is available only in the Narrativ Forge topic (6)."
                    elif not settings.openrouter_api_key:
                        reply = "⚠️ OpenRouter API key is not configured on the backend."
                    else:
                        model = next((item.strip() for item in settings.openrouter_models.split(",") if item.strip()), "")
                        if not model:
                            reply = "⚠️ No OpenRouter model is configured."
                        else:
                            try:
                                async with httpx.AsyncClient(timeout=25.0) as client:
                                    response = await client.post(
                                        settings.openrouter_base_url.rstrip("/") + "/chat/completions",
                                        headers={
                                            "Authorization": "Bearer " + settings.openrouter_api_key,
                                            "Content-Type": "application/json",
                                            "HTTP-Referer": "https://narrativ-forge.onrender.com",
                                            "X-Title": "Narrativ Forge Telegram AI Test",
                                        },
                                        json={
                                            "model": model,
                                            "messages": [{"role": "user", "content": "Reply with exactly: Narrativ Forge AI connection OK"}],
                                            "max_tokens": 40,
                                        },
                                    )
                                if response.is_success:
                                    data = response.json()
                                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                                    safe_content = html.escape(str(content)[:500]) if content else "Provider returned an empty response."
                                    reply = f"✅ <b>OpenRouter test succeeded</b>\nModel: <code>{html.escape(model)}</code>\n{safe_content}"
                                else:
                                    logger.warning("OpenRouter Telegram test failed with HTTP %s", response.status_code)
                                    reply = f"⚠️ OpenRouter test failed (HTTP {response.status_code}). Check backend provider settings/logs."
                            except Exception:
                                logger.exception("OpenRouter Telegram test request failed")
                                reply = "⚠️ OpenRouter request failed. Check backend logs and provider connectivity."
                elif command == "/idea":
                    if topic_id != 6:
                        reply = "⛔ /idea is available only in the Narrativ Forge topic (6)."
                    else:
                        idea_text = text.strip().partition(" ")[2].strip()
                        if not idea_text:
                            reply = "💡 Usage: /idea <text>\nExample: /idea Create a short video about sustainable living"
                        elif len(idea_text) > 10000:
                            reply = "⚠️ Idea is too long. Please keep it under 10,000 characters."
                        else:
                            action_payload = TelegramActionPayload(
                                action="nf_idea_capture",
                                event_id=f"telegram-idea:{chat.get('id')}:{incoming.get('message_id')}:{user_id}",
                                chat_id=chat.get("id"),
                                topic_id=topic_id,
                                user_id=user_id,
                                username=(actor.get("username") if isinstance(actor.get("username"), str) else None),
                                raw_message=idea_text,
                            )
                            result = await handle_telegram_action(
                                action_payload,
                                x_telegram_gateway_secret=x_telegram_bot_api_secret_token,
                                db=db,
                            )
                            return {"status": "ok", "action": "idea_capture", "result": result.get("status")}
                elif command == "/drafts":
                    if topic_id != 6:
                        reply = "⛔ /drafts is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            scripts = (
                                db.query(Script)
                                .join(Episode, Script.episode_id == Episode.id)
                                .filter(Episode.organization_id == _narrativ_organization_id(db))
                                .filter(Script.status.in_(["draft", "pending_review", "needs_approval", "ready_for_review"]))
                                .filter(Script.is_current.is_(True))
                                .order_by(Script.updated_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not scripts:
                                reply = "📝 No active drafts found."
                            else:
                                lines = ["📝 <b>Active Drafts:</b>\n"]
                                for i, s in enumerate(scripts, 1):
                                    title = html.escape(str(s.title or s.id)[:60])
                                    st = html.escape(str(s.status))
                                    lines.append(f"{i}. <code>{title}</code> — {st}")
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /drafts failed")
                            reply = "⚠️ Could not fetch drafts. Database may be unavailable."

                elif command == "/ideas":
                    if topic_id != 6:
                        reply = "⛔ /ideas is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            ideas = (
                                db.query(Idea)
                                .filter(Idea.organization_id == _narrativ_organization_id(db))
                                .filter(Idea.status.in_(["idea", "developing", "approved"]))
                                .order_by(Idea.created_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not ideas:
                                reply = "💡 No ideas found."
                            else:
                                lines = ["💡 <b>Recent Ideas:</b>\n"]
                                for i, idea in enumerate(ideas, 1):
                                    title = html.escape(str(idea.title or "Untitled")[:60])
                                    st = html.escape(str(idea.status))
                                    lines.append(f"{i}. <code>{title}</code> — {st}")
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /ideas failed")
                            reply = "⚠️ Could not fetch ideas. Database may be unavailable."

                elif command == "/episodes":
                    if topic_id != 6:
                        reply = "⛔ /episodes is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            episodes = (
                                db.query(Episode)
                                .filter(Episode.organization_id == _narrativ_organization_id(db))
                                .order_by(Episode.updated_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not episodes:
                                reply = "🎬 No episodes found."
                            else:
                                lines = ["🎬 <b>Recent Episodes:</b>\n"]
                                for i, ep in enumerate(episodes, 1):
                                    title = html.escape(str(ep.title or ep.id)[:60])
                                    st = html.escape(str(ep.status or "unknown"))
                                    step = html.escape(str(ep.current_step or ""))
                                    lines.append(f"{i}. <code>{title}</code> — {st}" + (f" ({step})" if step else ""))
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /episodes failed")
                            reply = "⚠️ Could not fetch episodes. Database may be unavailable."

                elif command == "/pipeline":
                    if topic_id != 6:
                        reply = "⛔ /pipeline is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            jobs = (
                                db.query(ProcessingJob)
                                .join(Episode, ProcessingJob.episode_id == Episode.id)
                                .filter(Episode.organization_id == _narrativ_organization_id(db))
                                .filter(ProcessingJob.status.in_(["queued", "processing", "pending"]))
                                .order_by(ProcessingJob.created_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not jobs:
                                reply = "⚙️ No active pipeline jobs."
                            else:
                                lines = ["⚙️ <b>Active Pipeline Jobs:</b>\n"]
                                for i, j in enumerate(jobs, 1):
                                    jtype = html.escape(str(j.job_type or "unknown")[:30])
                                    st = html.escape(str(j.status))
                                    prog = f" ({j.progress}%)" if hasattr(j, 'progress') and j.progress else ""
                                    lines.append(f"{i}. <code>{jtype}</code> — {st}{prog}")
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /pipeline failed")
                            reply = "⚠️ Could not fetch pipeline jobs. Database may be unavailable."

                elif command == "/assets":
                    if topic_id != 6:
                        reply = "⛔ /assets is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            assets = (
                                db.query(Asset)
                                .join(Episode, Asset.episode_id == Episode.id)
                                .filter(Episode.organization_id == _narrativ_organization_id(db))
                                .order_by(Asset.created_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not assets:
                                reply = "📦 No assets found."
                            else:
                                lines = ["📦 <b>Recent Assets:</b>\n"]
                                for i, a in enumerate(assets, 1):
                                    atype = html.escape(str(a.asset_type or "unknown")[:20])
                                    st = html.escape(str(a.status or "unknown"))
                                    name = html.escape(str(a.original_filename or a.id)[:40])
                                    lines.append(f"{i}. [{atype}] <code>{name}</code> — {st}")
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /assets failed")
                            reply = "⚠️ Could not fetch assets. Database may be unavailable."

                elif command == "/reviews":
                    if topic_id != 6:
                        reply = "⛔ /reviews is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            reviews = (
                                db.query(ReviewRecord)
                                .join(Episode, ReviewRecord.episode_id == Episode.id)
                                .filter(Episode.organization_id == _narrativ_organization_id(db))
                                .order_by(ReviewRecord.created_at.desc())
                                .limit(10)
                                .all()
                            )
                            if not reviews:
                                reply = "📋 No reviews found."
                            else:
                                lines = ["📋 <b>Recent Reviews:</b>\n"]
                                for i, r in enumerate(reviews, 1):
                                    decision = html.escape(str(r.decision or "pending"))
                                    ep_id = html.escape(str(r.episode_id or "?")[:20])
                                    lines.append(f"{i}. Episode <code>{ep_id}</code> — {decision}")
                                reply = "\n".join(lines)
                        except Exception:
                            logger.exception("Telegram /reviews failed")
                            reply = "⚠️ Could not fetch reviews. Database may be unavailable."

                elif command == "/metrics":
                    if topic_id != 6:
                        reply = "⛔ /metrics is available only in the Narrativ Forge topic (6)."
                    else:
                        try:
                            from sqlalchemy import func as sa_func
                            organization_id = _narrativ_organization_id(db)
                            total_eps = db.query(sa_func.count(Episode.id)).filter(
                                Episode.organization_id == organization_id
                            ).scalar() or 0
                            total_scripts = db.query(sa_func.count(Script.id)).join(
                                Episode, Script.episode_id == Episode.id
                            ).filter(
                                Episode.organization_id == organization_id,
                                Script.is_current.is_(True),
                            ).scalar() or 0
                            total_ideas = db.query(sa_func.count(Idea.id)).filter(
                                Idea.organization_id == organization_id
                            ).scalar() or 0
                            total_assets = db.query(sa_func.count(Asset.id)).join(
                                Episode, Asset.episode_id == Episode.id
                            ).filter(Episode.organization_id == organization_id).scalar() or 0
                            active_jobs = db.query(sa_func.count(ProcessingJob.id)).join(
                                Episode, ProcessingJob.episode_id == Episode.id
                            ).filter(
                                Episode.organization_id == organization_id,
                                ProcessingJob.status.in_(["queued", "processing", "pending"]),
                            ).scalar() or 0
                            reply = (
                        "📊 <b>Narrativ Forge Metrics:</b>\n\n"
                        f"🎬 Episodes: <b>{total_eps}</b>\n"
                        f"📝 Scripts (current): <b>{total_scripts}</b>\n"
                        f"💡 Ideas: <b>{total_ideas}</b>\n"
                        f"📦 Assets: <b>{total_assets}</b>\n"
                                f"⚙️ Active Jobs: <b>{active_jobs}</b>"
                            )
                        except Exception:
                            logger.exception("Telegram /metrics failed")
                            reply = "⚠️ Could not fetch metrics. Database may be unavailable."
                elif command == "/manga":
                    if topic_id != 6:
                        reply = "⛔ /manga is available only in the Narrativ Forge topic (6)."
                    else:
                        manga_prompt = text.strip().partition(" ")[2].strip()
                        if not manga_prompt:
                            reply = "📖 <b>Manga Generator Usage:</b>\n/manga <story prompt>\nExample: <code>/manga Cyber Samurai awakens in ancient Bagan pagoda</code>"
                        else:
                            try:
                                page = MangaEngine.generate_manga_page(
                                    title=manga_prompt[:40],
                                    story_synopsis=manga_prompt,
                                    layout_type=LayoutType.YONKOMA_4KOMA,
                                )
                                panels = page.get("panels", [])
                                p_summary = "\n".join([f"• <b>Panel {p['panel_index']}:</b> {html.escape(p['title'])}" for p in panels[:4]])
                                reply = (
                                    f"📖 <b>Manga Storyboard Generated!</b>\n\n"
                                    f"🏷️ Page ID: <code>{page['page_id']}</code>\n"
                                    f"📐 Layout: <b>4-Koma Comic Strip</b>\n"
                                    f"⏱️ Video Duration: <b>{page['estimated_video_duration_seconds']}s</b>\n\n"
                                    f"{p_summary}\n\n"
                                    f"🎨 <i>Open <b>/manga-studio</b> in Narrativ Forge to view panels and export motion comic.</i>"
                                )
                            except Exception:
                                logger.exception("Telegram /manga failed")
                                reply = "⚠️ Could not generate manga layout. Check backend logs."

                elif command == "/clip":
                    if topic_id != 6:
                        reply = "⛔ /clip is available only in the Narrativ Forge topic (6)."
                    else:
                        clip_args = text.strip().partition(" ")[2].strip().split(" ", 1)
                        if len(clip_args) < 2 or not clip_args[0].startswith("http"):
                            reply = "🎬 <b>Clip Importer Usage:</b>\n/clip <url> <title>\nExample: <code>/clip https://example.com/clip.mp4 Runway Battle Scene</code>"
                        else:
                            try:
                                c_url = clip_args[0]
                                c_title = clip_args[1]
                                clip = VideoComposerService.register_external_clip(
                                    source_url=c_url,
                                    provider=VideoSourceProvider.CUSTOM_URL,
                                    title=c_title,
                                    duration_seconds=5.0,
                                )
                                reply = (
                                    f"🎞️ <b>AI Video Clip Registered!</b>\n\n"
                                    f"🆔 ID: <code>{clip['id']}</code>\n"
                                    f"🏷️ Title: <b>{html.escape(clip['title'])}</b>\n"
                                    f"⏱️ Duration: <b>{clip['duration_seconds']}s</b>\n\n"
                                    f"✂️ <i>Open <b>/video-composer</b> in Narrativ Forge to assemble timeline tracks.</i>"
                                )
                            except Exception:
                                logger.exception("Telegram /clip failed")
                                reply = "⚠️ Could not register video clip. Check backend logs."


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
                        "🩺 <b>Narrativ Forge status</b>\n"
                        f"Telegram notifications: {'enabled' if settings.telegram_enabled else 'disabled'}\n"
                        f"Telegram credentials: {'configured' if settings.telegram_bot_token.get_secret_value() else 'missing'}\n"
                        f"AI providers configured: {html.escape(ai_text)}"
                    )
                else:
                    reply = (
                        f"🩺 <b>{html.escape(project_name)} status</b>\n"
                        "Topic routing is recognized and isolated.\n"
                        "⚠️ Project-specific AI/service health is not connected to this Narrativ Forge backend, "
                        "so this bot cannot truthfully report that project's provider or workflow health yet."
                    )
                await send_telegram_message(
                    reply,
                    chat_id=chat.get("id"),
                    topic_id=topic_id if isinstance(topic_id, int) else None,
                    inline_keyboard=_dashboard_keyboard(),
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
    if str(payload.chat_id) != settings.telegram_chat_id or payload.topic_id != settings.telegram_topic_id:
        raise HTTPException(status_code=403, detail="Telegram action is outside the configured project topic")
    _authorize_gateway(x_telegram_gateway_secret, payload.user_id)
    event_pk = _event_pk(payload.event_id)
    previous = db.get(AuditEvent, event_pk)
    if previous:
        return {
            "status": "duplicate",
            "action": previous.action,
            "id": previous.resource_id,
        }

    organization = (
        db.query(Organization)
        .filter(Organization.slug == settings.supabase_owner_organization_slug)
        .first()
    )
    if not organization:
        raise HTTPException(status_code=503, detail="Narrativ Forge organization is not configured")

    action = payload.action
    target_id = ""
    target_type = ""
    action_name = ""
    organization_id: str | None = organization.id
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
                .filter(
                    Script.id == script_id,
                    Script.is_current.is_(True),
                    Episode.organization_id == organization.id,
                )
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
            asset = (
                db.query(Asset)
                .join(Episode, Asset.episode_id == Episode.id)
                .filter(Asset.id == asset_id, Episode.organization_id == organization.id)
                .first()
            )
            if not asset or asset.asset_type not in {"processed_video", "video"}:
                raise HTTPException(status_code=404, detail="Video asset not found")
            episode = db.query(Episode).filter(
                Episode.id == asset.episode_id,
                Episode.organization_id == organization.id,
            ).first()
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
            asset = (
                db.query(Asset)
                .join(Episode, Asset.episode_id == Episode.id)
                .filter(Asset.id == asset_id, Episode.organization_id == organization.id)
                .first()
            )
            if not asset or asset.asset_type not in {"processed_video", "video"}:
                raise HTTPException(status_code=404, detail="Video asset not found")
            episode = db.query(Episode).filter(
                Episode.id == asset.episode_id,
                Episode.organization_id == organization.id,
            ).first()
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
