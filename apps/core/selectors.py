"""Core read-only selectors."""

from __future__ import annotations

from apps.core.models import AcademicYear, AuditLog, School


def get_active_academic_year() -> AcademicYear | None:
    """Return the currently active AcademicYear, or None."""
    return AcademicYear.objects.filter(is_active=True).first()


def list_academic_years() -> list[AcademicYear]:
    """List all academic years ordered by label descending."""
    return list(AcademicYear.objects.order_by("-label", "-semester"))


def get_school() -> School | None:
    """Return the single School instance for this deployment.

    This is a single-tenant system; there is exactly one school per deployment.
    """
    return School.objects.first()


def list_audit_logs(
    *,
    user_id: int | None = None,
    content_type_id: int | None = None,
    limit: int = 100,
) -> list[AuditLog]:
    """List audit logs with optional filters."""
    qs = AuditLog.objects.all()
    if user_id:
        qs = qs.filter(user_id=user_id)
    if content_type_id:
        qs = qs.filter(content_type_id=content_type_id)
    return list(qs[:limit])
