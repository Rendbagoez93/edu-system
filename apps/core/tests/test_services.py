"""Unit tests for core services."""

from __future__ import annotations

import pytest

from apps.core.models import AuditAction, AuditLog, User, UserRole
from apps.core.selectors import get_active_academic_year, get_school, list_academic_years
from apps.core.services import (
    activate_academic_year,
    create_academic_year,
    create_school,
    create_user,
    deactivate_academic_year,
    log_audit,
)
from apps.core.tests.factories import AcademicYearFactory, SchoolFactory, UserFactory


@pytest.mark.unit
def test_create_school_returns_school_with_correct_fields(db: None) -> None:
    school = create_school(
        npsn="12345678",
        name="SMA Testing",
        address="Jl. Testing No. 1",
        level="SMA",
        kepala_sekolah="Budi Santoso",
        phone="02112345678",
        email="sekolah@testing.sch.id",
    )
    assert school.npsn == "12345678"
    assert school.name == "SMA Testing"
    assert school.level == "SMA"
    assert school.kepala_sekolah == "Budi Santoso"


@pytest.mark.unit
def test_create_academic_year_returns_year(db: None) -> None:
    year = create_academic_year(label="2025/2026", semester="GANJIL", is_active=False)
    assert year.label == "2025/2026"
    assert year.semester == "GANJIL"
    assert year.is_active is False


@pytest.mark.unit
def test_create_academic_year_activates_others_deactivated(db: None) -> None:
    year1 = create_academic_year(label="2025/2026", semester="GANJIL", is_active=True)
    year2 = create_academic_year(label="2025/2026", semester="GENAP", is_active=True)
    year1.refresh_from_db()
    assert year1.is_active is False
    assert year2.is_active is True


@pytest.mark.unit
def test_activate_academic_year_deactivates_all_others(db: None) -> None:
    year1 = AcademicYearFactory(is_active=True)
    year2 = AcademicYearFactory(is_active=True)
    year1 = activate_academic_year(year1)
    year2.refresh_from_db()
    assert year1.is_active is True
    assert year2.is_active is False


@pytest.mark.unit
def test_deactivate_academic_year_sets_false(db: None) -> None:
    year = AcademicYearFactory(is_active=True)
    year = deactivate_academic_year(year)
    assert year.is_active is False


@pytest.mark.unit
def test_get_active_academic_year_returns_active(db: None) -> None:
    year = AcademicYearFactory(is_active=True)
    result = get_active_academic_year()
    assert result is not None
    assert result.pk == year.pk


@pytest.mark.unit
def test_get_active_academic_year_returns_none_when_empty(db: None) -> None:
    result = get_active_academic_year()
    assert result is None


@pytest.mark.unit
def test_list_academic_years_ordered_by_label_desc(db: None) -> None:
    AcademicYearFactory(label="2024/2025")
    AcademicYearFactory(label="2025/2026")
    AcademicYearFactory(label="2023/2024")
    years = list_academic_years()
    assert [y.label for y in years] == ["2025/2026", "2024/2025", "2023/2024"]


@pytest.mark.unit
def test_create_user_returns_user_with_correct_role(db: None) -> None:
    user = create_user(
        email="admin@school.local",
        password="rawpassword",
        role=UserRole.ADMIN,
        first_name="Admin",
        last_name="User",
    )
    assert user.email == "admin@school.local"
    assert user.role == UserRole.ADMIN
    assert user.check_password("rawpassword") is True
    assert user.is_active is True


@pytest.mark.unit
def test_create_user_headmaster_role(db: None) -> None:
    user = create_user(
        email="kepala@school.local",
        password="rawpassword",
        role=UserRole.HEADMASTER,
    )
    assert user.role == UserRole.HEADMASTER


@pytest.mark.unit
def test_create_user_default_role_is_admin(db: None) -> None:
    user = create_user(
        email="new@school.local",
        password="rawpassword",
        role=UserRole.ADMIN,
    )
    assert user.role == UserRole.ADMIN


@pytest.mark.unit
def test_log_audit_creates_entry(db: None) -> None:
    school = SchoolFactory()
    user = UserFactory()
    log = log_audit(
        action=AuditAction.CREATE,
        instance=school,
        user=user,
        changes={"name": [None, "SMA Testing"]},
    )
    assert log.action == AuditAction.CREATE
    assert log.user == user
    assert log.object_id == str(school.pk)
    assert log.changes == {"name": [None, "SMA Testing"]}


@pytest.mark.unit
def test_log_audit_system_event_no_user(db: None) -> None:
    school = SchoolFactory()
    log = log_audit(action=AuditAction.DELETE, instance=school, changes=None)
    assert log.user is None
    assert log.action == AuditAction.DELETE


@pytest.mark.unit
def test_get_school_returns_school(db: None) -> None:
    school = SchoolFactory()
    result = get_school()
    assert result is not None
    assert result.pk == school.pk


@pytest.mark.unit
def test_get_school_returns_none_when_empty(db: None) -> None:
    result = get_school()
    assert result is None
