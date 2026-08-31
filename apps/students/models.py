"""Student domain models."""

from __future__ import annotations

from django.db import models

from apps.academic_structure.models import ClassSection
from apps.core.models import AcademicYear, School, User
from apps.shared.models import SoftDeleteMixin, TimestampMixin


class GenderType(models.TextChoices):
    LAKI_LAKI = "LAKI_LAKI", "Laki-laki"
    PEREMPUAN = "PEREMPUAN", "Perempuan"


class EnrollmentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Aktif"
    TRANSFERRED = "TRANSFERRED", "Pindah"
    GRADUATED = "GRADUATED", "Lulus"
    DROPPED = "DROPPED", "Dropout"


class ImportBatchStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    VALIDATED = "VALIDATED", "Validated"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class Student(TimestampMixin, SoftDeleteMixin, models.Model):
    nisn = models.CharField(max_length=10, unique=True)
    nis = models.CharField(max_length=8)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderType.choices)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    guardian_name = models.CharField(max_length=255)
    guardian_contact = models.CharField(max_length=20)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    phone_same_as_guardian = models.BooleanField(default=False)
    address = models.TextField()
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="students",
    )
    user_account = models.OneToOneField(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="student_profile",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "nis"],
                name="unique_school_nis",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Enrollment(TimestampMixin, SoftDeleteMixin, models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "class_section", "academic_year"],
                name="unique_student_class_year",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student.name} in {self.class_section.name}"


class ImportBatch(TimestampMixin, models.Model):
    file_name = models.CharField(max_length=255)
    row_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=ImportBatchStatus.choices,
        default=ImportBatchStatus.PENDING,
    )
    imported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="import_batches",
    )

    def __str__(self) -> str:
        return f"{self.file_name} ({self.status})"
