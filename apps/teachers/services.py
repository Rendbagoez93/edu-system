"""Teacher business logic services."""

from __future__ import annotations

from typing import Any

from apps.core.models import School
from apps.teachers.models import Teacher


def create_teacher(
    name: str,
    employment_status: str,
    school: School,
    *,
    nuptk: str | None = None,
    contact_phone: str | None = None,
    address: str | None = None,
    email: str | None = None,
) -> Teacher:
    """Create a new teacher profile."""
    return Teacher.objects.create(
        nuptk=nuptk,
        name=name,
        employment_status=employment_status,
        contact_phone=contact_phone,
        address=address,
        email=email,
        school=school,
    )


def update_teacher(teacher: Teacher, **fields: Any) -> Teacher:
    """Update teacher profile fields."""
    for key, value in fields.items():
        setattr(teacher, key, value)
    teacher.save()
    return teacher
