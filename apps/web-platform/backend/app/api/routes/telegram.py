from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.telegram import send_telegram_message, is_telegram_configured

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramActionPayload(BaseModel):
    action: str
    chat_id: int | str | None = None
    topic_id: int | None = None
    user_id: int | None = None
    username: str | None = None
    raw_message: str | None = None


@router.post("/action")
async def handle_telegram_action(payload: TelegramActionPayload) -> dict[str, Any]:
    """Handle inbound Telegram action callback from the Cloud Gateway."""
    action = payload.action
    logger.info("Received Telegram action: %s from user: %s", action, payload.username)

    # 1. Script Approval
    if action.startswith("nf_script_appr:"):
        script_id = action.split(":", 1)[1]
        msg = f"✅ <b>Script Approved:</b> <code>{script_id}</code>\nProceeding to Scene Breakdown & Asset Generation."
        await send_telegram_message(msg, topic_id=payload.topic_id)
        return {"status": "ok", "action": "script_approved", "id": script_id}

    # 2. Script Rejection
    elif action.startswith("nf_script_rej:"):
        script_id = action.split(":", 1)[1]
        msg = f"❌ <b>Script Rejected:</b> <code>{script_id}</code>\nMarked for revision."
        await send_telegram_message(msg, topic_id=payload.topic_id)
        return {"status": "ok", "action": "script_rejected", "id": script_id}

    # 3. Video Approval
    elif action.startswith("nf_video_appr:"):
        video_id = action.split(":", 1)[1]
        msg = f"👍 <b>Video Approved:</b> <code>{video_id}</code>\nTriggering automated Google Drive export."
        await send_telegram_message(msg, topic_id=payload.topic_id)
        return {"status": "ok", "action": "video_approved", "id": video_id}

    # 4. Video Re-run
    elif action.startswith("nf_video_rerun:"):
        video_id = action.split(":", 1)[1]
        msg = f"🔄 <b>Video Re-run Queued:</b> <code>{video_id}</code>\nWorker has scheduled a fresh rendering job."
        await send_telegram_message(msg, topic_id=payload.topic_id)
        return {"status": "ok", "action": "video_rerun", "id": video_id}

    # 5. Quick Ingestion / Idea Capture
    elif action == "nf_idea_capture" and payload.raw_message:
        idea_text = payload.raw_message.strip()
        msg = f"💡 <b>New Video Idea Captured:</b>\n<i>\"{idea_text[:120]}\"</i>\nSaved into Script Studio drafts."
        await send_telegram_message(msg, topic_id=payload.topic_id)
        return {"status": "ok", "action": "idea_captured", "idea": idea_text}

    return {"status": "ignored", "action": action}
