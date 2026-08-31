"""Teacher domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import School
from apps.shared.models import SoftDeleteMixin, TimestampMixin


class EmploymentStatus(models.TextChoices):
    PNS = "PNS", "PNS"
    HONORER = "HONORER", "Honorer"
    GTY = "GTY", "Guru Tidak Tetap"


class Teacher(TimestampMixin, SoftDeleteMixin, models.Model):
    nuptk = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        unique=True,
    )
    name = models.CharField(max_length=255)
    employment_status = models.CharField(
        max_length=10,
        choices=EmploymentStatus.choices,
    )
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="teachers",
    )
    user_account = models.OneToOneField(
        "core.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="teacher_profile",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
