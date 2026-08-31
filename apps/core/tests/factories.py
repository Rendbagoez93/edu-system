"""Test factories for core models."""

from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.core.models import AcademicYear, AuditAction, AuditLog, School, User, UserRole


class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School

    npsn = factory.Sequence(lambda n: f"{n:08d}")
    name = factory.Sequence(lambda n: f"Sekolah {n}")
    address = "Jl. Testing No. 1"
    level = "SMA"
    kepala_sekolah = "Budi Santoso"
    phone = None
    email = None
    logo = None


class AcademicYearFactory(DjangoModelFactory):
    class Meta:
        model = AcademicYear

    label = factory.Sequence(lambda n: f"{2025 + (n // 2)}/{2026 + (n // 2)}")
    semester = factory.Sequence(lambda n: "GANJIL" if n % 2 == 0 else "GENAP")
    is_active = False


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@school.local")
    password = factory.django.Password("testpassword123")
    role = UserRole.ADMIN
    first_name = "Admin"
    last_name = "User"
    is_active = True


class HeadmasterFactory(UserFactory):
    role = UserRole.HEADMASTER
    first_name = "Kepala"
    last_name = "Sekolah"


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    user = None
    action = AuditAction.CREATE
    content_object = factory.SubFactory(SchoolFactory)
    changes = None
