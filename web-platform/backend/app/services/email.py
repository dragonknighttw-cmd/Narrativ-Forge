from __future__ import annotations

import smtplib
from email.message import EmailMessage

from ..core.config import settings


def send_email(*, recipient: str, subject: str, body: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("SMTP email delivery is not configured")

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            client.starttls()
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            client.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            client.send_message(message)
