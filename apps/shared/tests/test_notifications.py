"""Tests for the email notification dispatch helper."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import patch

import pytest

from apps.shared.notifications import EmailNotification, send_email_notification


@pytest.mark.unit
class TestSendEmailNotification:
    def test_delegates_to_django_send_mail(self):
        notification = EmailNotification(
            subject="Welcome",
            message="Hello, Budi.",
            recipient_list=["budi@example.com"],
        )
        with patch("apps.shared.notifications.send_mail", return_value=1) as mock_send:
            result = send_email_notification(notification)

        assert result == 1
        mock_send.assert_called_once_with(
            subject="Welcome",
            message="Hello, Budi.",
            from_email=None,
            recipient_list=["budi@example.com"],
            fail_silently=True,
        )

    def test_passes_through_from_email_and_fail_silently(self):
        notification = EmailNotification(
            subject="Rapor siap",
            message="Rapor Anda sudah tersedia.",
            recipient_list=["parent@example.com"],
            from_email="noreply@school.sch.id",
            fail_silently=False,
        )
        with patch("apps.shared.notifications.send_mail", return_value=1) as mock_send:
            send_email_notification(notification)

        kwargs = mock_send.call_args.kwargs
        assert kwargs["from_email"] == "noreply@school.sch.id"
        assert kwargs["fail_silently"] is False

    def test_returns_zero_when_nothing_sent(self):
        notification = EmailNotification(
            subject="x",
            message="y",
            recipient_list=[],
        )
        with patch("apps.shared.notifications.send_mail", return_value=0):
            assert send_email_notification(notification) == 0

    def test_email_notification_is_frozen(self):
        # frozen=True guards against accidental mutation after construction —
        # callers may pass instances across thread boundaries.
        notification = EmailNotification(subject="x", message="y", recipient_list=["a@b.c"])
        with pytest.raises(FrozenInstanceError):
            notification.subject = "changed"  # type: ignore[misc]
