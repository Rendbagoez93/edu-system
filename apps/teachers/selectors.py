"""Teacher read-only selectors."""

from __future__ import annotations

from apps.core.models import School
from apps.teachers.models import Teacher


def get_teacher_profile(teacher_id: int) -> Teacher | None:
    """Return a teacher by ID, or None."""
    return Teacher.objects.filter(pk=teacher_id).first()


def list_teachers(
    *,
    school: School | None = None,
    employment_status: str | None = None,
) -> list[Teacher]:
    """List teachers with optional filters."""
    qs = Teacher.objects.all()
    if school:
        qs = qs.filter(school=school)
    if employment_status:
        qs = qs.filter(employment_status=employment_status)
    return list(qs)
