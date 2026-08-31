"""Academic structure models — grade levels, majors, subjects, class sections."""

from __future__ import annotations

from django.db import models

from apps.core.models import AcademicYear, School
from apps.shared.models import SoftDeleteMixin, TimestampMixin


class GradeLevel(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=5)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="grade_levels",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_school_gradelevel",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Major(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="majors",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_school_major",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Subject(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "code"],
                name="unique_school_code",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ClassSection(TimestampMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=20)
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name="class_sections",
    )
    major = models.ForeignKey(
        Major,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="class_sections",
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="class_sections",
    )
    homeroom_teacher = models.ForeignKey(
        "teachers.Teacher",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="homeroom_sections",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["grade_level", "major", "academic_year", "name"],
                name="unique_grade_major_year_name",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
