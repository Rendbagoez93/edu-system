"""Student business logic services."""

from __future__ import annotations

from typing import Any

from apps.academic_structure.models import ClassSection
from apps.core.models import AcademicYear, School
from apps.students.models import (
    Enrollment,
    EnrollmentStatus,
    GenderType,
    ImportBatch,
    Student,
)


def enroll_student(
    student: Student,
    class_section: ClassSection,
    academic_year: AcademicYear,
    *,
    status: str = EnrollmentStatus.ACTIVE,
) -> Enrollment:
    """Enroll a student into a class section for an academic year."""
    return Enrollment.objects.get_or_create(
        student=student,
        class_section=class_section,
        academic_year=academic_year,
        defaults={"status": status},
    )[0]


def create_student(
    school: School,
    nisn: str,
    nis: str,
    name: str,
    date_of_birth: str,
    gender: str,
    guardian_name: str,
    guardian_contact: str,
    address: str,
    *,
    phone: str | None = None,
    email: str | None = None,
    guardian_relation: str | None = None,
    phone_same_as_guardian: bool = False,
) -> Student:
    """Create a new student profile."""
    return Student.objects.create(
        nisn=nisn,
        nis=nis,
        name=name,
        date_of_birth=date_of_birth,
        gender=gender,
        phone=phone,
        email=email,
        guardian_name=guardian_name,
        guardian_contact=guardian_contact,
        guardian_relation=guardian_relation,
        phone_same_as_guardian=phone_same_as_guardian,
        address=address,
        school=school,
    )


def update_student(student: Student, **fields: Any) -> Student:
    """Update student profile fields."""
    for key, value in fields.items():
        setattr(student, key, value)
    student.save()
    return student


def validate_import_row(row: dict[str, Any]) -> list[str]:
    """Validate a single student import row.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    if not row.get("nisn"):
        errors.append("nisn is required")
    elif len(str(row["nisn"])) != 10:
        errors.append("nisn must be exactly 10 digits")

    if not row.get("nis"):
        errors.append("nis is required")

    if not row.get("name"):
        errors.append("name is required")

    if not row.get("date_of_birth"):
        errors.append("date_of_birth is required")

    if not row.get("gender"):
        errors.append("gender is required")
    elif row["gender"] not in GenderType.values:
        errors.append(f"gender must be one of: {', '.join(GenderType.values)}")

    if not row.get("guardian_name"):
        errors.append("guardian_name is required")

    if not row.get("guardian_contact"):
        errors.append("guardian_contact is required")

    if not row.get("address"):
        errors.append("address is required")

    return errors


def create_import_batch(
    file_name: str,
    imported_by: Any,
    row_count: int = 0,
) -> ImportBatch:
    """Create a new import batch record."""
    return ImportBatch.objects.create(
        file_name=file_name,
        row_count=row_count,
        imported_by=imported_by,
    )
