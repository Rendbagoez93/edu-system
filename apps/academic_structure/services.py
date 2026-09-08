"""Academic structure business logic services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject

if TYPE_CHECKING:
    from apps.core.models import AcademicYear, School
    from apps.teachers.models import Teacher


# ---------------------------------------------------------------------------
# GradeLevel
# ---------------------------------------------------------------------------


def create_grade_level(
    name: str,
    school: School,
) -> GradeLevel:
    """Create a new grade level (Tingkat)."""
    return GradeLevel.objects.create(
        name=name,
        school=school,
    )


def update_grade_level(grade_level: GradeLevel, **fields: Any) -> GradeLevel:
    """Update grade level fields."""
    for key, value in fields.items():
        setattr(grade_level, key, value)
    grade_level.save()
    return grade_level


def soft_delete_grade_level(grade_level: GradeLevel) -> None:
    """Soft-delete a grade level."""
    grade_level.soft_delete()


# ---------------------------------------------------------------------------
# Major
# ---------------------------------------------------------------------------


def create_major(
    name: str,
    school: School,
    *,
    is_active: bool = True,
) -> Major:
    """Create a new major (Jurusan/Peminatan)."""
    return Major.objects.create(
        name=name,
        school=school,
        is_active=is_active,
    )


def update_major(major: Major, **fields: Any) -> Major:
    """Update major fields."""
    for key, value in fields.items():
        setattr(major, key, value)
    major.save()
    return major


def soft_delete_major(major: Major) -> None:
    """Soft-delete a major."""
    major.soft_delete()


# ---------------------------------------------------------------------------
# Subject
# ---------------------------------------------------------------------------


def create_subject(
    name: str,
    code: str,
    school: School,
    *,
    is_active: bool = True,
) -> Subject:
    """Create a new subject (Mata Pelajaran)."""
    return Subject.objects.create(
        name=name,
        code=code,
        school=school,
        is_active=is_active,
    )


def update_subject(subject: Subject, **fields: Any) -> Subject:
    """Update subject fields."""
    for key, value in fields.items():
        setattr(subject, key, value)
    subject.save()
    return subject


def soft_delete_subject(subject: Subject) -> None:
    """Soft-delete a subject."""
    subject.soft_delete()


# ---------------------------------------------------------------------------
# ClassSection
# ---------------------------------------------------------------------------


def create_class_section(
    name: str,
    grade_level: GradeLevel,
    academic_year: AcademicYear,
    *,
    major: Major | None = None,
    homeroom_teacher: Teacher | None = None,
) -> ClassSection:
    """Create a new class section (Kelas), e.g. 'X IPA 1'."""
    return ClassSection.objects.create(
        name=name,
        grade_level=grade_level,
        major=major,
        academic_year=academic_year,
        homeroom_teacher=homeroom_teacher,
    )


def update_class_section(class_section: ClassSection, **fields: Any) -> ClassSection:
    """Update class section fields."""
    for key, value in fields.items():
        setattr(class_section, key, value)
    class_section.save()
    return class_section


def soft_delete_class_section(class_section: ClassSection) -> None:
    """Soft-delete a class section."""
    class_section.soft_delete()


def assign_homeroom_teacher(
    class_section: ClassSection,
    teacher: Teacher,
) -> ClassSection:
    """Assign a homeroom teacher (Wali Kelas) to a class section."""
    class_section.homeroom_teacher = teacher
    class_section.save(update_fields=["homeroom_teacher", "updated_at"])
    return class_section
