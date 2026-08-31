"""Core business logic services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.contenttypes.models import ContentType

from apps.core.models import AcademicYear, AuditLog, School, User, UserRole

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Academic Year services
# ---------------------------------------------------------------------------


def activate_academic_year(year: AcademicYear) -> AcademicYear:
    """Activate an academic year, deactivating all others.

    Enforces the invariant: exactly one is_active=True per school.
    """
    AcademicYear.objects.filter(is_active=True).update(is_active=False)
    year.is_active = True
    year.save(update_fields=["is_active", "updated_at"])
    return year


def deactivate_academic_year(year: AcademicYear) -> AcademicYear:
    """Deactivate an academic year."""
    year.is_active = False
    year.save(update_fields=["is_active", "updated_at"])
    return year


def create_academic_year(
    label: str,
    semester: str,
    is_active: bool = False,
) -> AcademicYear:
    """Create a new academic year. Deactivates others if is_active=True."""
    year = AcademicYear.objects.create(label=label, semester=semester, is_active=is_active)
    if is_active:
        activate_academic_year(year)
    return year


# ---------------------------------------------------------------------------
# School services
# ---------------------------------------------------------------------------


def create_school(
    npsn: str,
    name: str,
    address: str,
    level: str,
    kepala_sekolah: str,
    *,
    nss: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> School:
    """Create a new school."""
    return School.objects.create(
        npsn=npsn,
        name=name,
        address=address,
        level=level,
        kepala_sekolah=kepala_sekolah,
        nss=nss,
        phone=phone,
        email=email,
    )


def update_school(school: School, **fields: Any) -> School:
    """Update school fields."""
    for key, value in fields.items():
        setattr(school, key, value)
    school.save()
    return school


# ---------------------------------------------------------------------------
# User services
# ---------------------------------------------------------------------------


def create_user(
    email: str,
    password: str,
    role: str,
    *,
    first_name: str = "",
    last_name: str = "",
    is_active: bool = True,
) -> User:
    """Create an admin/headmaster user account."""
    user = User(
        email=email,
        role=role,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )
    user.set_password(password)
    user.save()
    return user


def provision_teacher_login(
    teacher: Any,
    password: str,
) -> User:
    """Provision a User account for a teacher.

    Args:
        teacher: A Teacher model instance (from apps.teachers).
        password: Plain-text password (will be hashed).

    Returns:
        The created User instance linked to the teacher.
    """
    email = teacher.email or f"teacher-{teacher.nuptk or teacher.pk}@school.local"
    user = User(
        email=email,
        role=UserRole.TEACHER,
        first_name=teacher.name.split()[0] if teacher.name else "",
        last_name=" ".join(teacher.name.split()[1:]) if teacher.name else "",
        teacher=teacher,
    )
    user.set_password(password)
    user.save()
    return user


def set_user_password(user: User, password: str) -> None:
    """Set or reset a user's password."""
    user.set_password(password)
    user.save(update_fields=["password", "updated_at"])


# ---------------------------------------------------------------------------
# Audit log services
# ---------------------------------------------------------------------------


def log_audit(
    action: str,
    instance: Any,
    *,
    user: User | None = None,
    changes: dict[str, list[Any, Any]] | None = None,
) -> AuditLog:
    """Create an immutable audit log entry.

    Args:
        action: CREATE | UPDATE | DELETE
        instance: The model instance being audited.
        user: The actor (nullable for system-initiated events).
        changes: Dict of {field: [old_value, new_value]}. None for DELETE.

    Note:
        Never log Score.value, Student.nisn, guardian_contact, date_of_birth,
        or Teacher.nuptk fields.
    """
    content_type = ContentType.objects.get_for_model(instance)
    return AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=str(instance.pk),
        changes=changes,
    )
