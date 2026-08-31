"""Feature tests for core API endpoints."""

from __future__ import annotations

import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import AuditAction, AuditLog, School, User, UserRole
from apps.core.tests.factories import (
    AcademicYearFactory,
    AuditLogFactory,
    HeadmasterFactory,
    SchoolFactory,
    UserFactory,
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def admin_user(db: None) -> User:
    return UserFactory(role=UserRole.ADMIN)


@pytest.fixture
def headmaster_user(db: None) -> User:
    return HeadmasterFactory()


@pytest.mark.feature
@pytest.mark.django_db
class TestSchoolAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.admin = UserFactory(role=UserRole.ADMIN)
        self.client.force_authenticate(user=self.admin)
        self.school = SchoolFactory()

    def test_list_schools_returns_200(self) -> None:
        response = self.client.get("/api/v1/schools/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_school_returns_201(self) -> None:
        payload = {
            "npsn": "99999999",
            "name": "SMA Baru",
            "address": "Jl. Baru No. 1",
            "level": "SMA",
            "kepala_sekolah": "Kepala Baru",
        }
        response = self.client.post("/api/v1/schools/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "SMA Baru"

    def test_retrieve_school_returns_200(self) -> None:
        response = self.client.get(f"/api/v1/schools/{self.school.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["npsn"] == self.school.npsn

    def test_update_school_returns_200(self) -> None:
        response = self.client.patch(
            f"/api/v1/schools/{self.school.pk}/",
            {"name": "SMA Updated"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "SMA Updated"

    def test_current_school_returns_200(self) -> None:
        response = self.client.get("/api/v1/schools/current/")
        assert response.status_code == status.HTTP_200_OK

    def test_current_school_returns_404_when_empty(self, api_client: APIClient) -> None:
        # setup_method already created self.school; remove it so the view sees an empty store.
        self.school.delete()
        response = api_client.get("/api/v1/schools/current/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        response = api_client.get("/api/v1/schools/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_headmaster_can_access(self, headmaster_user: User) -> None:
        client = APIClient()
        client.force_authenticate(user=headmaster_user)
        response = client.get("/api/v1/schools/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.feature
@pytest.mark.django_db
class TestAcademicYearAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.admin = UserFactory(role=UserRole.ADMIN)
        self.client.force_authenticate(user=self.admin)
        self.year = AcademicYearFactory()

    def test_list_academic_years_returns_200(self) -> None:
        response = self.client.get("/api/v1/academic-years/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_academic_year_returns_201(self) -> None:
        payload = {
            "label": "2026/2027",
            "semester": "GANJIL",
            "is_active": False,
        }
        response = self.client.post("/api/v1/academic-years/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["label"] == "2026/2027"

    def test_duplicate_label_semester_returns_400(self) -> None:
        AcademicYearFactory(label="2025/2026", semester="GANJIL")
        payload = {
            "label": "2025/2026",
            "semester": "GANJIL",
            "is_active": False,
        }
        response = self.client.post("/api/v1/academic-years/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_academic_year_returns_200(self) -> None:
        year = AcademicYearFactory(is_active=False)
        response = self.client.post(f"/api/v1/academic-years/{year.pk}/activate/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] is True

    def test_activate_deactivates_other_years(self) -> None:
        year1 = AcademicYearFactory(is_active=True)
        year2 = AcademicYearFactory(is_active=True)
        response = self.client.post(f"/api/v1/academic-years/{year1.pk}/activate/")
        assert response.status_code == status.HTTP_200_OK
        year1.refresh_from_db()
        year2.refresh_from_db()
        assert year1.is_active is True
        assert year2.is_active is False

    def test_active_endpoint_returns_active_year(self) -> None:
        year = AcademicYearFactory(is_active=True)
        response = self.client.get("/api/v1/academic-years/active/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == year.pk

    def test_active_endpoint_returns_404_when_none(self) -> None:
        response = self.client.get("/api/v1/academic-years/active/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.feature
@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.admin = UserFactory(role=UserRole.ADMIN)
        self.client.force_authenticate(user=self.admin)

    def test_list_users_returns_200(self) -> None:
        response = self.client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_user_returns_201(self) -> None:
        payload = {
            "email": "newuser@school.local",
            "password": "securepassword123!",
            "role": "ADMIN",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post("/api/v1/users/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newuser@school.local"
        assert "password" not in response.data
        assert User.objects.filter(email="newuser@school.local").exists()

    def test_retrieve_user_returns_200(self) -> None:
        user = UserFactory()
        response = self.client.get(f"/api/v1/users/{user.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_password_not_in_response(self) -> None:
        user = UserFactory()
        response = self.client.get(f"/api/v1/users/{user.pk}/")
        assert "password" not in response.data

    def test_unauthenticated_returns_403(self, api_client: APIClient) -> None:
        response = api_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.feature
@pytest.mark.django_db
class TestAuditLogAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.admin = UserFactory(role=UserRole.ADMIN)
        self.client.force_authenticate(user=self.admin)
        self.school = SchoolFactory()
        self.log = AuditLogFactory(
            user=self.admin,
            content_type=ContentType.objects.get_for_model(School),
            object_id=str(self.school.pk),
        )

    def test_list_audit_logs_returns_200(self) -> None:
        response = self.client.get("/api/v1/audit-logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_audit_log_returns_200(self) -> None:
        response = self.client.get(f"/api/v1/audit-logs/{self.log.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["action"] == AuditAction.CREATE

    def test_audit_log_read_only_returns_405_on_post(self) -> None:
        response = self.client.post("/api/v1/audit-logs/", {"action": "CREATE"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
