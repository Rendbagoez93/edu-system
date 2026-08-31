"""Unit tests for core model methods and constraints."""

from __future__ import annotations

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from apps.core.models import AcademicYear, AuditAction, AuditLog, School, User, UserRole
from apps.core.tests.factories import AcademicYearFactory, AuditLogFactory, SchoolFactory, UserFactory


@pytest.mark.unit
@pytest.mark.django_db
class TestSchoolModel:
    def test_str_returns_name(self) -> None:
        school = SchoolFactory(name="SMA Nusantara")
        assert str(school) == "SMA Nusantara"

    def test_npsn_must_be_8_digits(self) -> None:
        school = SchoolFactory.build(npsn="123")
        with pytest.raises(ValidationError):
            school.full_clean()

    def test_npsn_accepts_8_digits(self) -> None:
        school = SchoolFactory.build(npsn="12345678")
        school.full_clean()

    def test_npsn_must_be_unique(self) -> None:
        SchoolFactory(npsn="12345678")
        school2 = SchoolFactory.build(npsn="12345678")
        with pytest.raises(ValidationError):
            school2.full_clean()


@pytest.mark.unit
@pytest.mark.django_db
class TestAcademicYearModel:
    def test_str_returns_label_semester(self) -> None:
        year = AcademicYearFactory(label="2025/2026", semester="GANJIL")
        assert str(year) == "2025/2026 (GANJIL)"

    def test_unique_constraint_label_semester(self) -> None:
        AcademicYearFactory(label="2025/2026", semester="GANJIL")
        year2 = AcademicYearFactory.build(label="2025/2026", semester="GANJIL")
        with pytest.raises(ValidationError):
            year2.full_clean()

    def test_clean_deactivates_existing_when_is_active_true(self) -> None:
        AcademicYearFactory(is_active=True)
        year2 = AcademicYearFactory.build(is_active=True)
        year2.pk = None
        with pytest.raises(ValidationError) as exc_info:
            year2.full_clean()
        assert "active" in str(exc_info.value).lower()

    def test_ordering_is_descending_by_label(self) -> None:
        AcademicYearFactory(label="2023/2024")
        AcademicYearFactory(label="2025/2026")
        AcademicYearFactory(label="2024/2025")
        labels = list(AcademicYear.objects.values_list("label", flat=True))
        assert labels == ["2025/2026", "2024/2025", "2023/2024"]


@pytest.mark.unit
@pytest.mark.django_db
class TestUserModel:
    def test_str_returns_email(self) -> None:
        user = UserFactory(email="admin@school.local")
        assert str(user) == "admin@school.local"

    def test_email_is_unique(self) -> None:
        UserFactory(email="unique@school.local")
        user2 = UserFactory.build(email="unique@school.local")
        with pytest.raises(ValidationError):
            user2.full_clean()

    def test_username_is_none(self) -> None:
        user = UserFactory()
        assert user.username is None

    def test_default_role_is_admin(self) -> None:
        user = UserFactory.build()
        assert user.role == UserRole.ADMIN

    def test_email_is_used_as_username_field(self) -> None:
        user = UserFactory(email="login@school.local")
        assert user.USERNAME_FIELD == "email"

    def test_required_fields_is_empty(self) -> None:
        user = UserFactory.build()
        assert user.REQUIRED_FIELDS == []


@pytest.mark.unit
@pytest.mark.django_db
class TestAuditLogModel:
    def test_str_format(self) -> None:
        school = SchoolFactory()
        user = UserFactory()
        ct = ContentType.objects.get_for_model(School)
        log = AuditLog.objects.create(
            user=user,
            action=AuditAction.UPDATE,
            content_type=ct,
            object_id=str(school.pk),
            changes={"name": ["Old", "New"]},
        )
        assert log.action == AuditAction.UPDATE
        assert log.object_id == str(school.pk)

    def test_ordering_is_descending_by_timestamp(self) -> None:
        school = SchoolFactory()
        ContentType.objects.get_for_model(School)
        AuditLogFactory(content_object=school)
        AuditLogFactory(content_object=school)
        ids = list(AuditLog.objects.values_list("pk", flat=True))
        assert ids == sorted(ids, reverse=True)
