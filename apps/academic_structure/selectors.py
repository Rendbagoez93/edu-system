"""Academic structure read-only selectors."""

from __future__ import annotations

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject
from apps.core.models import AcademicYear, School


def get_grade_level(grade_level_id: int) -> GradeLevel | None:
    """Return a grade level by ID, or None."""
    return GradeLevel.objects.filter(pk=grade_level_id).first()


def list_grade_levels(
    *,
    school: School | None = None,
) -> list[GradeLevel]:
    """List grade levels, optionally filtered by school."""
    qs = GradeLevel.objects.all()
    if school:
        qs = qs.filter(school=school)
    return list(qs)


def get_major(major_id: int) -> Major | None:
    """Return a major by ID, or None."""
    return Major.objects.filter(pk=major_id).first()


def list_majors(
    *,
    school: School | None = None,
    is_active: bool | None = None,
) -> list[Major]:
    """List majors, optionally filtered by school and active status."""
    qs = Major.objects.all()
    if school:
        qs = qs.filter(school=school)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs)


def get_subject(subject_id: int) -> Subject | None:
    """Return a subject by ID, or None."""
    return Subject.objects.filter(pk=subject_id).first()


def list_subjects(
    *,
    school: School | None = None,
    is_active: bool | None = None,
) -> list[Subject]:
    """List subjects, optionally filtered by school and active status."""
    qs = Subject.objects.all()
    if school:
        qs = qs.filter(school=school)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs)


def get_class_section(class_section_id: int) -> ClassSection | None:
    """Return a class section by ID, or None."""
    return ClassSection.objects.filter(pk=class_section_id).first()


def list_class_sections(
    *,
    grade_level: GradeLevel | None = None,
    academic_year: AcademicYear | None = None,
    major: Major | None = None,
) -> list[ClassSection]:
    """List class sections, optionally filtered by grade level, academic year, or major."""
    qs = ClassSection.objects.all()
    if grade_level:
        qs = qs.filter(grade_level=grade_level)
    if academic_year:
        qs = qs.filter(academic_year=academic_year)
    if major:
        qs = qs.filter(major=major)
    return list(qs)


def list_class_sections_for_year(academic_year: AcademicYear) -> list[ClassSection]:
    """List all class sections for a given academic year."""
    return list(
        ClassSection.objects.filter(academic_year=academic_year).select_related(
            "grade_level",
            "major",
            "homeroom_teacher",
        )
    )
