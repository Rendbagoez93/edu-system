"""Student read-only selectors."""

from __future__ import annotations

from apps.academic_structure.models import ClassSection
from apps.core.models import AcademicYear
from apps.students.models import Enrollment, ImportBatch, Student


def get_student(student_id: int) -> Student | None:
    """Return a student by ID, or None."""
    return Student.objects.filter(pk=student_id).first()


def list_students(
    *,
    school_id: int | None = None,
    gender: str | None = None,
) -> list[Student]:
    """List students with optional filters."""
    qs = Student.objects.all()
    if school_id:
        qs = qs.filter(school_id=school_id)
    if gender:
        qs = qs.filter(gender=gender)
    return list(qs)


def get_roster(
    class_section: ClassSection,
    academic_year: AcademicYear | None = None,
) -> list[Student]:
    """Return all active students enrolled in a class section."""
    qs = Enrollment.objects.filter(
        class_section=class_section,
        status="ACTIVE",
    ).select_related("student")
    if academic_year:
        qs = qs.filter(academic_year=academic_year)
    return [e.student for e in qs]


def get_enrollment(student: Student, academic_year: AcademicYear) -> Enrollment | None:
    """Return a student's enrollment for a given academic year."""
    return Enrollment.objects.filter(
        student=student,
        academic_year=academic_year,
        status="ACTIVE",
    ).first()


def get_import_batch(batch_id: int) -> ImportBatch | None:
    """Return an import batch by ID."""
    return ImportBatch.objects.filter(pk=batch_id).first()
