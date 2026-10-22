from __future__ import annotations

import logging
from typing import Any
import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


def is_telegram_configured() -> bool:
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else ""
    return bool(token and settings.telegram_chat_id and settings.telegram_enabled)


async def send_telegram_message(
    text: str,
    *,
    topic_id: int | None = None,
    parse_mode: str = "HTML",
    inline_keyboard: list[list[dict[str, str]]] | None = None,
    disable_web_page_preview: bool = False,
) -> dict[str, Any] | None:
    """Send an asynchronous message to Telegram group/topic."""
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else ""
    chat_id = settings.telegram_chat_id
    effective_topic = topic_id if topic_id is not None else settings.telegram_topic_id

    if not token or not chat_id:
        logger.info("[Telegram:Narrativ-Forge:DryRun] %s", text.replace("\n", " "))
        return None

    if not settings.telegram_enabled:
        logger.debug("[Telegram:Narrativ-Forge:Disabled] %s", text.replace("\n", " "))
        return None

    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    if effective_topic:
        payload["message_thread_id"] = int(effective_topic)

    if inline_keyboard:
        payload["reply_markup"] = {"inline_keyboard": inline_keyboard}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error("Telegram API error (%s): %s", response.status_code, response.text)
                return None
            return response.json()
    except Exception as exc:
        logger.warning("Failed to send Telegram message: %s", exc)
        return None


async def answer_telegram_callback(
    callback_query_id: str,
    text: str = "",
    *,
    show_alert: bool = False,
) -> dict[str, Any] | None:
    """Acknowledge a Telegram inline-button click so the client stops showing a spinner."""
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else ""
    if not token:
        logger.warning("Cannot acknowledge Telegram callback: bot token is not configured")
        return None
    url = f"{TELEGRAM_API_BASE}/bot{token}/answerCallbackQuery"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={
                    "callback_query_id": callback_query_id,
                    "text": text[:200],
                    "show_alert": show_alert,
                },
            )
            if response.status_code != 200:
                logger.error("Telegram callback acknowledgement failed (%s)", response.status_code)
                return None
            return response.json()
    except Exception:
        logger.warning("Failed to acknowledge Telegram callback", exc_info=True)
        return None


async def send_notification(
    title: str,
    details: str,
    *,
    status: str = "INFO",
    topic_id: int | None = None,
    actions: list[tuple[str, str]] | None = None,
) -> dict[str, Any] | None:
    """Send a standardized notification card to the Narrativ-Forge topic."""
    icon_map = {
        "SUCCESS": "✅",
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "🚨",
    }
    status_icon = icon_map.get(status.upper(), "📌")

    lines = [
        f"🎬 <b>[Narrativ-Forge]</b> {status_icon} <b>{title}</b>",
        "",
        details,
    ]
    text = "\n".join(lines)

    inline_keyboard = None
    if actions:
        row: list[dict[str, str]] = []
        for label, callback_or_url in actions:
            if callback_or_url.startswith("http://") or callback_or_url.startswith("https://"):
                row.append({"text": label, "url": callback_or_url})
            else:
                row.append({"text": label, "callback_data": callback_or_url})
        inline_keyboard = [row]

    return await send_telegram_message(text, topic_id=topic_id, inline_keyboard=inline_keyboard)


# ==========================================
# Domain-specific Action Hooks
# ==========================================

async def notify_script_review(script_id: str, title: str, author: str | None = None) -> None:
    """Notify when a new script is ready for review/approval."""
    details = f"📝 <b>Script:</b> {title}\n"
    if author:
        details += f"👤 <b>Author:</b> {author}\n"
    details += f"🆔 <code>{script_id}</code>"

    actions = [
        ("✅ Approve Script", f"nf_script_appr:{script_id}"),
        ("❌ Reject", f"nf_script_rej:{script_id}"),
    ]
    await send_notification("Script Ready for Review", details, status="INFO", actions=actions)


async def notify_video_ready(video_id: str, title: str, preview_url: str | None = None) -> None:
    """Notify when video rendering completes."""
    details = f"🎞️ <b>Video:</b> {title}\n🆔 <code>{video_id}</code>"
    actions: list[tuple[str, str]] = [
        ("👍 Approve Video", f"nf_video_appr:{video_id}"),
        ("🔄 Re-render", f"nf_video_rerun:{video_id}"),
    ]
    if preview_url:
        actions.insert(0, ("▶️ Preview", preview_url))
    await send_notification("Video Render Finished", details, status="SUCCESS", actions=actions)


async def notify_export_complete(title: str, gdrive_url: str) -> None:
    """Notify when Google Drive export completes."""
    details = f"📁 <b>Asset:</b> {title}\n☁️ Google Drive export is complete."
    actions = [("🔗 Open Google Drive", gdrive_url)]
    await send_notification("Export Complete", details, status="SUCCESS", actions=actions)


async def notify_pipeline_error(stage: str, error_message: str, project_id: str | None = None) -> None:
    """Alert team on pipeline failures."""
    details = f"⚙️ <b>Stage:</b> {stage}\n❌ <b>Error:</b> {error_message}"
    if project_id:
        details += f"\n🆔 <code>{project_id}</code>"
    await send_notification("Pipeline Alert", details, status="ERROR")
