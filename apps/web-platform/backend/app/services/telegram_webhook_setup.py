from __future__ import annotations

import logging

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)

WEBHOOK_URL = "https://narrativ-forge.onrender.com/api/v1/telegram/webhook"


async def configure_telegram_webhook() -> None:
    """Keep Telegram's webhook URL and secret synchronized with backend settings."""
    if not settings.telegram_enabled:
        logger.info("Telegram webhook setup skipped: Telegram integration is disabled")
        return

    token = settings.telegram_bot_token.get_secret_value()
    secret = settings.telegram_gateway_secret
    if not token:
        logger.warning("Telegram webhook setup skipped: bot token is not configured")
        return
    if len(secret) < 32:
        logger.warning("Telegram webhook setup skipped: gateway secret must be at least 32 characters")
        return
    if not all(ch.isalnum() or ch in "_-" for ch in secret):
        logger.error("Telegram webhook setup skipped: secret contains characters Telegram does not accept")
        return

    url = f"https://api.telegram.org/bot{token}/setWebhook"
    payload = {
        "url": WEBHOOK_URL,
        "secret_token": secret,
        "allowed_updates": ["message", "edited_message", "callback_query"],
        "drop_pending_updates": False,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("ok") is True:
                logger.info("Telegram webhook configured successfully for the Narrativ Forge backend")
            else:
                # Never log the request URL or payload: both contain credentials.
                logger.error("Telegram webhook setup failed: Telegram API returned ok=false")
    except Exception as exc:
        # Exception strings can include request URLs, so log only the exception type.
        logger.error("Telegram webhook setup failed (%s)", type(exc).__name__)
