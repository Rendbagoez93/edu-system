"""Tests for academic structure services."""

from __future__ import annotations

import pytest

from apps.academic_structure.services import (
    assign_homeroom_teacher,
    create_class_section,
    create_grade_level,
    create_major,
    create_subject,
    soft_delete_class_section,
    soft_delete_grade_level,
    soft_delete_major,
    soft_delete_subject,
    update_class_section,
    update_grade_level,
    update_major,
    update_subject,
)
from apps.academic_structure.tests.factories import (
    AcademicYearFactory,
    ClassSectionFactory,
    GradeLevelFactory,
    MajorFactory,
    SchoolFactory,
    SubjectFactory,
)
from apps.teachers.tests.factories import TeacherFactory

# ---------------------------------------------------------------------------
# GradeLevel
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCreateGradeLevel:
    def test_creates_grade_level(self, db):
        school = SchoolFactory()

        grade = create_grade_level(name="X", school=school)

        assert grade.pk is not None
        assert grade.name == "X"
        assert grade.school == school
        assert grade.is_deleted is False

    def test_creates_multiple_grade_levels_for_same_school(self, db):
        school = SchoolFactory()

        g1 = create_grade_level(name="X", school=school)
        g2 = create_grade_level(name="XI", school=school)
        g3 = create_grade_level(name="XII", school=school)

        assert g1.pk != g2.pk != g3.pk


@pytest.mark.integration
class TestUpdateGradeLevel:
    def test_updates_name(self, db):
        grade = GradeLevelFactory(name="X")

        updated = update_grade_level(grade, name="XI")

        assert updated.name == "XI"


@pytest.mark.integration
class TestSoftDeleteGradeLevel:
    def test_soft_deletes_grade_level(self, db):
        grade = GradeLevelFactory()

        soft_delete_grade_level(grade)

        grade.refresh_from_db()
        assert grade.is_deleted is True
        assert grade.deleted_at is not None


# ---------------------------------------------------------------------------
# Major
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCreateMajor:
    def test_creates_major(self, db):
        school = SchoolFactory()

        major = create_major(name="IPA", school=school)

        assert major.pk is not None
        assert major.name == "IPA"
        assert major.is_active is True

    def test_creates_inactive_major(self, db):
        school = SchoolFactory()

        major = create_major(name="IPS", school=school, is_active=False)

        assert major.is_active is False


@pytest.mark.integration
class TestUpdateMajor:
    def test_updates_name_and_is_active(self, db):
        major = MajorFactory(name="IPA")

        updated = update_major(major, name="IPS", is_active=False)

        assert updated.name == "IPS"
        assert updated.is_active is False


@pytest.mark.integration
class TestSoftDeleteMajor:
    def test_soft_deletes_major(self, db):
        major = MajorFactory()

        soft_delete_major(major)

        major.refresh_from_db()
        assert major.is_deleted is True


# ---------------------------------------------------------------------------
# Subject
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCreateSubject:
    def test_creates_subject(self, db):
        school = SchoolFactory()

        subject = create_subject(name="Matematika", code="MTK", school=school)

        assert subject.pk is not None
        assert subject.name == "Matematika"
        assert subject.code == "MTK"
        assert subject.is_active is True


@pytest.mark.integration
class TestUpdateSubject:
    def test_updates_name_and_code(self, db):
        subject = SubjectFactory(name="Matematika", code="MTK")

        updated = update_subject(subject, name="Matematika IPA", code="MTK-IPA")

        assert updated.name == "Matematika IPA"
        assert updated.code == "MTK-IPA"


@pytest.mark.integration
class TestSoftDeleteSubject:
    def test_soft_deletes_subject(self, db):
        subject = SubjectFactory()

        soft_delete_subject(subject)

        subject.refresh_from_db()
        assert subject.is_deleted is True


# ---------------------------------------------------------------------------
# ClassSection
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCreateClassSection:
    def test_creates_class_section(self, db):
        grade = GradeLevelFactory()
        year = AcademicYearFactory()

        section = create_class_section(
            name="X IPA 1",
            grade_level=grade,
            academic_year=year,
        )

        assert section.pk is not None
        assert section.name == "X IPA 1"
        assert section.grade_level == grade
        assert section.academic_year == year

    def test_creates_class_section_with_major(self, db):
        grade = GradeLevelFactory()
        major = MajorFactory()
        year = AcademicYearFactory()

        section = create_class_section(
            name="XI IPA 2",
            grade_level=grade,
            major=major,
            academic_year=year,
        )

        assert section.major == major


@pytest.mark.integration
class TestUpdateClassSection:
    def test_updates_name(self, db):
        section = ClassSectionFactory(name="X IPA 1")

        updated = update_class_section(section, name="X IPA 2")

        assert updated.name == "X IPA 2"


@pytest.mark.integration
class TestSoftDeleteClassSection:
    def test_soft_deletes_class_section(self, db):
        section = ClassSectionFactory()

        soft_delete_class_section(section)

        section.refresh_from_db()
        assert section.is_deleted is True


@pytest.mark.integration
class TestAssignHomeroomTeacher:
    def test_assigns_homeroom_teacher(self, db):
        section = ClassSectionFactory()
        teacher = TeacherFactory()

        updated = assign_homeroom_teacher(section, teacher)

        assert updated.homeroom_teacher == teacher

    def test_replaces_existing_homeroom_teacher(self, db):
        section = ClassSectionFactory()
        teacher1 = TeacherFactory()
        teacher2 = TeacherFactory()

        assign_homeroom_teacher(section, teacher1)
        updated = assign_homeroom_teacher(section, teacher2)

        assert updated.homeroom_teacher == teacher2
