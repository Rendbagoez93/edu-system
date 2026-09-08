"""Feature tests for academic structure API endpoints."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.academic_structure.tests.factories import (
    AcademicYearFactory,
    ClassSectionFactory,
    GradeLevelFactory,
    MajorFactory,
    SchoolFactory,
    SubjectFactory,
)
from apps.core.tests.factories import HeadmasterFactory, UserFactory


@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Admin user for authenticated requests."""
    return UserFactory(role="ADMIN")


@pytest.fixture
def headmaster_user(db):
    """Headmaster user for authenticated requests."""
    return HeadmasterFactory()


# ---------------------------------------------------------------------------
# GradeLevel
# ---------------------------------------------------------------------------


@pytest.mark.feature
@pytest.mark.django_db
class TestGradeLevelAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = HeadmasterFactory()
        self.client.force_authenticate(user=self.user)
        self.school = SchoolFactory()

    def test_admin_can_create_grade_level(self):
        response = self.client.post(
            "/api/v1/grade-levels/",
            {"name": "X", "school": self.school.id},
        )
        assert response.status_code == 201
        assert response.data["name"] == "X"

    def test_admin_can_list_grade_levels(self):
        GradeLevelFactory.create_batch(3, school=self.school)
        response = self.client.get("/api/v1/grade-levels/")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_admin_can_retrieve_grade_level(self):
        grade = GradeLevelFactory(school=self.school, name="XI")
        response = self.client.get(f"/api/v1/grade-levels/{grade.id}/")
        assert response.status_code == 200
        assert response.data["name"] == "XI"

    def test_admin_can_update_grade_level(self):
        grade = GradeLevelFactory(school=self.school, name="X")
        response = self.client.patch(
            f"/api/v1/grade-levels/{grade.id}/",
            {"name": "XI"},
        )
        assert response.status_code == 200
        assert response.data["name"] == "XI"

    def test_admin_can_soft_delete_grade_level(self):
        grade = GradeLevelFactory(school=self.school)
        response = self.client.delete(f"/api/v1/grade-levels/{grade.id}/")
        assert response.status_code == 204
        grade.refresh_from_db()
        assert grade.is_deleted is True

    def test_unauthenticated_request_returns_401(self, api_client):
        response = api_client.get("/api/v1/grade-levels/")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Major
# ---------------------------------------------------------------------------


@pytest.mark.feature
@pytest.mark.django_db
class TestMajorAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = HeadmasterFactory()
        self.client.force_authenticate(user=self.user)
        self.school = SchoolFactory()

    def test_admin_can_create_major(self):
        response = self.client.post(
            "/api/v1/majors/",
            {"name": "IPA", "school": self.school.id},
        )
        assert response.status_code == 201
        assert response.data["name"] == "IPA"
        assert response.data["is_active"] is True

    def test_admin_can_list_majors(self):
        MajorFactory.create_batch(2, school=self.school)
        response = self.client.get("/api/v1/majors/")
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_admin_can_filter_majors_by_is_active(self):
        MajorFactory(school=self.school, is_active=True)
        MajorFactory(school=self.school, is_active=False)
        response = self.client.get("/api/v1/majors/?is_active=true")
        assert response.status_code == 200
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Subject
# ---------------------------------------------------------------------------


@pytest.mark.feature
@pytest.mark.django_db
class TestSubjectAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = HeadmasterFactory()
        self.client.force_authenticate(user=self.user)
        self.school = SchoolFactory()

    def test_admin_can_create_subject(self):
        response = self.client.post(
            "/api/v1/subjects/",
            {"name": "Matematika", "code": "MTK", "school": self.school.id},
        )
        assert response.status_code == 201
        assert response.data["name"] == "Matematika"
        assert response.data["code"] == "MTK"

    def test_admin_can_list_subjects(self):
        SubjectFactory.create_batch(4, school=self.school)
        response = self.client.get("/api/v1/subjects/")
        assert response.status_code == 200
        assert response.data["count"] == 4

    def test_admin_can_search_subjects_by_name(self):
        import uuid

        unique = uuid.uuid4().hex[:8]
        SubjectFactory(school=self.school, name=f"UNIQUE_SUBJ_{unique}")
        response = self.client.get(f"/api/v1/subjects/?name_icontains={unique}")
        assert response.status_code == 200
        names = [r["name"] for r in response.data["results"]]
        assert any(f"UNIQUE_SUBJ_{unique}" in n for n in names)


# ---------------------------------------------------------------------------
# ClassSection
# ---------------------------------------------------------------------------


@pytest.mark.feature
@pytest.mark.django_db
class TestClassSectionAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = HeadmasterFactory()
        self.client.force_authenticate(user=self.user)
        self.school = SchoolFactory()
        self.year = AcademicYearFactory()
        self.grade = GradeLevelFactory(school=self.school)

    def test_admin_can_create_class_section(self):
        response = self.client.post(
            "/api/v1/class-sections/",
            {
                "name": "X IPA 1",
                "grade_level": self.grade.id,
                "academic_year": self.year.id,
            },
        )
        assert response.status_code == 201
        assert response.data["name"] == "X IPA 1"
        assert response.data["grade_level_name"] == self.grade.name

    def test_admin_can_create_class_section_with_major_and_teacher(self):
        major = MajorFactory(school=self.school)
        from apps.teachers.tests.factories import TeacherFactory

        teacher = TeacherFactory(school=self.school)
        response = self.client.post(
            "/api/v1/class-sections/",
            {
                "name": "XI IPA 1",
                "grade_level": self.grade.id,
                "major": major.id,
                "academic_year": self.year.id,
                "homeroom_teacher": teacher.id,
            },
        )
        assert response.status_code == 201
        assert response.data["major_name"] == major.name
        assert response.data["homeroom_teacher_name"] == teacher.name

    def test_admin_can_list_class_sections(self):
        ClassSectionFactory.create_batch(3, academic_year=self.year)
        response = self.client.get("/api/v1/class-sections/")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_admin_can_filter_class_sections_by_grade_level(self):
        grade_other = GradeLevelFactory(school=self.school)
        ClassSectionFactory(academic_year=self.year, grade_level=self.grade)
        ClassSectionFactory(academic_year=self.year, grade_level=grade_other)
        response = self.client.get(f"/api/v1/class-sections/?grade_level={self.grade.id}")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_admin_can_filter_class_sections_by_academic_year(self):
        year_other = AcademicYearFactory()
        ClassSectionFactory(academic_year=self.year)
        ClassSectionFactory(academic_year=year_other)
        response = self.client.get(f"/api/v1/class-sections/?academic_year={self.year.id}")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_admin_can_update_class_section(self):
        section = ClassSectionFactory(academic_year=self.year)
        response = self.client.patch(
            f"/api/v1/class-sections/{section.id}/",
            {"name": "X IPA 2"},
        )
        assert response.status_code == 200
        assert response.data["name"] == "X IPA 2"

    def test_admin_can_soft_delete_class_section(self):
        section = ClassSectionFactory(academic_year=self.year)
        response = self.client.delete(f"/api/v1/class-sections/{section.id}/")
        assert response.status_code == 204
        section.refresh_from_db()
        assert section.is_deleted is True
