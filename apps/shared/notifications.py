from __future__ import annotations

from dataclasses import dataclass, field

from django.core.mail import send_mail

from apps.shared.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class EmailNotification:
    """An email notification payload."""

    subject: str
    message: str
    recipient_list: list[str] = field(default_factory=list)
    from_email: str | None = None
    fail_silently: bool = True


def send_email_notification(notification: EmailNotification) -> int:
    logger.info(
        "notification_dispatch",
        channel="email",
        recipient_count=len(notification.recipient_list),
    )
    return send_mail(
        subject=notification.subject,
        message=notification.message,
        from_email=notification.from_email,
        recipient_list=notification.recipient_list,
        fail_silently=notification.fail_silently,
    )
