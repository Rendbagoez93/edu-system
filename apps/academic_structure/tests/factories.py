"""Test factories for academic structure models."""

from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from apps.academic_structure.models import ClassSection, GradeLevel, Major, Subject
from apps.core.tests.factories import AcademicYearFactory, SchoolFactory


class GradeLevelFactory(DjangoModelFactory):
    class Meta:
        model = GradeLevel

    name = factory.Sequence(lambda n: str(n % 12 + 1))  # "1", "2", ... "12"
    school = factory.SubFactory(SchoolFactory)


class MajorFactory(DjangoModelFactory):
    class Meta:
        model = Major

    name = factory.Sequence(lambda n: f"Jurusan {n}")
    school = factory.SubFactory(SchoolFactory)
    is_active = True


class SubjectFactory(DjangoModelFactory):
    class Meta:
        model = Subject

    name = factory.Sequence(lambda n: f"Mata Pelajaran {n}")
    code = factory.Sequence(lambda n: f"MP{n:03d}")
    school = factory.SubFactory(SchoolFactory)
    is_active = True


class ClassSectionFactory(DjangoModelFactory):
    class Meta:
        model = ClassSection

    name = factory.Sequence(lambda n: f"Kelas {n}")
    grade_level = factory.SubFactory(GradeLevelFactory)
    major = None
    academic_year = factory.SubFactory(AcademicYearFactory)
    homeroom_teacher = None
