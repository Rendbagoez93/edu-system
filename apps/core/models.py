"""Core domain models — school identity, academic year, users, audit log."""

from __future__ import annotations

import re

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from apps.shared.models import SoftDeleteMixin, TimestampMixin

# ---------------------------------------------------------------------------
# TextChoices enums
# ---------------------------------------------------------------------------


class SchoolLevel(models.TextChoices):
    SD = "SD", "Sekolah Dasar"
    SMP = "SMP", "Sekolah Menengah Pertama"
    SMA = "SMA", "Sekolah Menengah Atas"
    SMK = "SMK", "Sekolah Menengah Kejuruan"


class SemesterType(models.TextChoices):
    GANJIL = "GANJIL", "Ganjil"
    GENAP = "GENAP", "Genap"


class UserRole(models.TextChoices):
    HEADMASTER = "HEADMASTER", "Kepala Sekolah"
    ADMIN = "ADMIN", "Administrator"
    TEACHER = "TEACHER", "Guru"


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Created"
    UPDATE = "UPDATE", "Updated"
    DELETE = "DELETE", "Deleted"


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def validate_npsn(value: str) -> None:
    if not re.fullmatch(r"\d{8}", value):
        raise ValidationError("NPSN must be exactly 8 digits.")


def validate_academic_year_label(value: str) -> None:
    if not re.fullmatch(r"\d{4}/\d{4}", value):
        raise ValidationError("Label must be in the format 'YYYY/YYYY' (e.g. 2025/2026).")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class School(TimestampMixin, SoftDeleteMixin, models.Model):
    npsn = models.CharField(
        max_length=8,
        unique=True,
        validators=[validate_npsn],
    )
    nss = models.CharField(max_length=12, blank=True, null=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    level = models.CharField(max_length=4, choices=SchoolLevel.choices)
    kepala_sekolah = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to="school_logos/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "schools"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AcademicYear(TimestampMixin, SoftDeleteMixin, models.Model):
    label = models.CharField(
        max_length=9,
        validators=[validate_academic_year_label],
    )
    semester = models.CharField(max_length=6, choices=SemesterType.choices)
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["label", "semester"],
                name="unique_label_semester",
            ),
        ]
        ordering = ["-label", "-semester"]

    def __str__(self) -> str:
        return f"{self.label} ({self.semester})"

    def clean(self) -> None:
        super().clean()
        if self.is_active:
            existing = AcademicYear.objects.filter(is_active=True)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one academic year can be active at a time.")


class User(TimestampMixin, AbstractUser):
    """Email-based user — no username field."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.ADMIN)
    teacher = models.OneToOneField(
        "teachers.Teacher",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="user_teacher",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email


class AuditLog(models.Model):
    """Immutable event log — no soft delete, no update."""

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=10, choices=AuditAction.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    changes = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.content_type} {self.object_id} by {self.user}"
