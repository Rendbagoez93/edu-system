"""Schedule read-only selectors."""

from __future__ import annotations

from apps.schedules.models import DayType, TimeSlot


def get_time_slot(slot_id: int) -> TimeSlot | None:
    """Return a time slot by ID, or None."""
    return TimeSlot.objects.filter(pk=slot_id).first()


def list_time_slots(
    *,
    day: str | None = None,
) -> list[TimeSlot]:
    """List time slots, optionally filtered by day.

    Args:
        day: Optional DayType value (e.g. "SENIN") to filter by day.
    """
    qs = TimeSlot.objects.all()
    if day:
        qs = qs.filter(day=day)
    return list(qs.order_by("day", "period"))


def list_days() -> list[str]:
    """Return all day values in school-week order."""
    return [choice.value for choice in DayType]


def list_slots_for_day(day: str) -> list[TimeSlot]:
    """Return all time slots for a given day, ordered by period."""
    return list(TimeSlot.objects.filter(day=day).order_by("period"))
