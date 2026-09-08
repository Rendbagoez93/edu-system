"""Schedule domain models — time slots."""

from __future__ import annotations

from django.db import models

from apps.shared.models import SoftDeleteMixin, TimestampMixin


class DayType(models.TextChoices):
    SENIN = "SENIN", "Senin"
    SELASA = "SELASA", "Selasa"
    RABU = "RABU", "Rabu"
    KAMIS = "KAMIS", "Kamis"
    JUMAT = "JUMAT", "Jumat"
    SABTU = "SABTU", "Sabtu"


class TimeSlot(TimestampMixin, SoftDeleteMixin, models.Model):
    """A fixed period on a specific day of the week.

    Example: "Senin, period 3" — the third lesson period on Monday.
    The same period number can exist on every day of the week as a separate
    TimeSlot record; the unique constraint is on (day, period).
    """

    day = models.CharField(
        max_length=10,
        choices=DayType.choices,
    )
    period = models.PositiveSmallIntegerField(
        help_text="Lesson period number (e.g. 1–10).",
    )
    display_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Used for ordering slots in the UI; lower = earlier.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["day", "period"],
                name="unique_day_period",
            ),
        ]
        ordering = ["day", "period"]

    def __str__(self) -> str:
        return f"{self.day} period {self.period}"
