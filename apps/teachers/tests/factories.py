"""Test factories for teacher models."""

from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.core.tests.factories import SchoolFactory
from apps.teachers.models import EmploymentStatus, Teacher


class TeacherFactory(DjangoModelFactory):
    class Meta:
        model = Teacher

    name = factory.Faker("name")
    employment_status = EmploymentStatus.HONORER
    school = factory.SubFactory(SchoolFactory)
    nuptk = None
    contact_phone = None
    address = None
    email = None
    user_account = None
