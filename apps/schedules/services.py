"""Schedule business logic services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.schedules.models import DayType, TimeSlot

if TYPE_CHECKING:
    from apps.teachers.models import Teacher


def create_time_slot(
    day: str,
    period: int,
    *,
    display_order: int | None = None,
) -> TimeSlot:
    """Create a new time slot.

    Args:
        day: One of DayType values (e.g. "SENIN").
        period: Lesson period number (e.g. 1–10).
        display_order: Optional sort order for UI; defaults to period.
    """
    if day not in DayType.values:
        raise ValueError(f"Invalid day: {day!r}. Must be one of {DayType.values}.")
    if display_order is None:
        display_order = period
    return TimeSlot.objects.create(
        day=day,
        period=period,
        display_order=display_order,
    )


def update_time_slot(slot: TimeSlot, **fields: Any) -> TimeSlot:
    """Update time slot fields."""
    if "day" in fields and fields["day"] not in DayType.values:
        raise ValueError(f"Invalid day: {fields['day']!r}. Must be one of {DayType.values}.")
    for key, value in fields.items():
        setattr(slot, key, value)
    slot.save()
    return slot


def is_slot_available(
    teacher: Teacher,
    time_slot: TimeSlot,
) -> bool:
    """Return True if the teacher has no assignment at the given time slot.

    Checks for a GradeAssignment record that would conflict — one where
    the same teacher and time_slot pair already exists and is not soft-deleted.

    This function is called by grade_management before creating a GradeAssignment.
    """
    try:
        from apps.grade_management.models import GradeAssignment

        return not GradeAssignment.objects.filter(
            teacher=teacher,
            time_slot=time_slot,
            is_deleted=False,
        ).exists()
    except ImportError:
        return True
