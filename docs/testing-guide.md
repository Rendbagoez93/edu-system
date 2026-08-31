# Testing Guide

This guide covers how tests are written for this project. It expands on CLAUDE.md's testing section with enough detail to get a new contributor writing tests correctly on their first day.

> **Prerequisite:** `config/settings/test.py` is referenced in `pyproject.toml` (`DJANGO_SETTINGS_MODULE = "config.settings.test"`) but does not yet exist. Create it before running tests. It should mirror `local.py` with SQLite, eager Celery, and `DEBUG=True`.

---

## 1. Directory Structure

Tests live alongside the code they test, not in a separate `tests/` monolith.

```
apps/
  core/
    models.py
    services.py
    views.py
    tests/
      __init__.py
      factories.py       ← one factory per model in this app
      test_services.py
      test_views.py     ← feature tests (APIClient)
      test_models.py    ← unit tests for model methods/constraints
  academic_structure/
    ...
```

- `__init__.py` in each `tests/` directory
- No `test_*.py` at the project root (root-level tests go in `tests/`)

---

## 2. Naming Conventions

| What | Pattern | Example |
|---|---|---|
| Test file | `test_{module}.py` | `test_services.py` |
| Test class | `Test{Model}{Behavior}` | `TestGradeAssignmentCreate`, `TestScoreValidation` |
| Test function | `test_{method}_{scenario}_{expected}` | `test_bulk_import_validates_nisn_uniqueness` |

A test name is a complete sentence. `test_bulk_import_rejects_duplicate_nisn` reads as "the bulk import rejects duplicate NISN."

---

## 3. pytest Configuration

From `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py", "tests.py", "_tests.py"]
python_classes = ["Test*", "*Test"]
python_functions = ["test_*", "*_test"]
addopts = [
    "--reuse-db",     # reuse the test DB between runs (faster)
    "-x",             # stop on first failure
    "--cov=config",
    "--cov=apps",
    "--cov-report=term-missing",
    "-n auto",        # parallel execution via pytest-xdist
    "--dist loadscope",
]
markers = [
    "unit: Unit test — single function/class, no DB or network I/O.",
    "integration: Integration test — multiple components, DB, services, or Celery tasks.",
    "feature: Feature test — full HTTP request/response cycle via DRF APIClient.",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

Run all tests:
```bash
pytest -n auto --cov
```

Run only unit tests:
```bash
pytest -m "unit" -n auto --cov
```

Run only feature tests:
```bash
pytest -m "feature" -n auto
```

Skip slow tests:
```bash
pytest -m "not slow" -n auto
```

---

## 4. conftest.py — Project-Wide Fixtures

Create `tests/conftest.py` at the project root (not inside any app):

```python
# tests/conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()
```

Each app can also have its own `tests/conftest.py` for app-specific fixtures, which pytest auto-loads from that directory.

---

## 5. Factories (factory-boy)

One factory per model, living in `<app>/tests/factories.py`.

```python
# apps/students/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from apps.students.models import Student
from apps.core.models import School


class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School

    name = factory.Sequence(lambda n: f"Sekolah {n}")
    npsn = factory.Sequence(lambda n: f"{n:08d}")  # zero-padded 8-digit
    level = "SMA"
    address = "Jl. Testing No. 1"


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    school = factory.SubFactory(SchoolFactory)
    nisn = factory.Sequence(lambda n: f"{1000000000 + n}")
    nis = factory.Sequence(lambda n: f"{n:08d}")
    name = factory.Faker("name")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=10, maximum_age=20)
    gender = factory.Faker("random_element", elements=["LAKI_LAKI", "PEREMPUAN"])
    guardian_name = factory.Faker("name")
    guardian_contact = factory.Sequence(lambda n: f"08{n % 10_000_000_000:010d}")
    address = factory.Faker("address")
```

Rules for factories:
- Always use `DjangoModelFactory` — it saves to the DB
- Use `factory.SubFactory` for FK relationships (creates the related object automatically)
- Use `factory.Sequence` for unique fields (NISN, NIS, etc.)
- Never hardcode specific values in a factory unless testing a specific constraint
- **Never generate real PII in factories** — use `factory.Faker` which uses locale-safe fake data by default

### Available fixtures from factories

After creating `SchoolFactory` and `StudentFactory`, tests get related objects auto-built:

```python
def test_student_enrollment(db, StudentFactory, ClassSectionFactory):
    student = StudentFactory()           # School auto-created via SubFactory
    section = ClassSectionFactory(grade_level__school=student.school)
    ...
```

---

## 6. Test Markers — When to Use Which

Apply markers to test classes or functions:

```python
@pytest.mark.unit
class TestScoreComputation:
    def test_semester_average_ignores_null_components(self):
        ...

@pytest.mark.integration
class TestBulkImport:
    @pytest.mark.slow
    def test_import_300_students(self):
        ...

@pytest.mark.feature
class TestScoreEntryAPI:
    def test_teacher_can_enter_score_for_assigned_subject(self, api_client, user):
        ...
```

**Decision guide:**
- `unit` — Pure function with no DB, model method, serializer validation, or service function
- `integration` — DB write/read, service + selector, Celery task, multi-model operation
- `feature` — HTTP request/response via `APIClient`, tests the view layer
- `slow` — Any test that takes > 5 seconds (large imports, file processing)

---

## 7. Unit Tests — Service and Selector Functions

Unit tests import the function directly and call it.

```python
# apps/students/tests/test_services.py
import pytest
from apps.students.services import validate_import_row, bulk_import_students
from apps.students.tests.factories import SchoolFactory, StudentFactory


@pytest.mark.unit
def test_validate_import_row_rejects_duplicate_nisn(db):
    school = SchoolFactory()
    StudentFactory(school=school, nisn="1234567890")

    row = {
        "nisn": "1234567890",
        "nis": "00000001",
        "name": "Budi",
        "date_of_birth": "2010-01-01",
        "gender": "LAKI_LAKI",
        "guardian_name": "Budi Sr.",
        "guardian_contact": "081234567890",
        "address": "Jl. Test",
    }

    errors = validate_import_row(row, school)
    assert len(errors) == 1
    assert errors[0]["field"] == "nisn"
```

Rules:
- Import the service function directly, not the view
- One behavior per test — one assertion of the expected outcome
- Use `db` fixture (from `pytest-django`) when the DB is needed
- For service functions that call other service/selector functions, mock the inner call with `pytest.mock.patch` if testing isolation is needed

---

## 8. Feature Tests — API via APIClient

Feature tests exercise the full HTTP stack: authentication, permissions, serialization, and the service layer together.

```python
# apps/assessment/tests/test_views.py
import pytest
from rest_framework.test import APIClient
from apps.core.tests.factories import UserFactory, SchoolFactory
from apps.teachers.tests.factories import TeacherFactory
from apps.academic_structure.tests.factories import (
    GradeLevelFactory, SubjectFactory, AcademicYearFactory, ClassSectionFactory,
)
from apps.grade_management.tests.factories import GradeAssignmentFactory
from apps.assessment.tests.factories import AssessmentComponentFactory, ScoreFactory


@pytest.mark.feature
@pytest.mark.django_db
class TestScoreEntry:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(role="HEADMASTER")
        self.client.force_authenticate(user=self.user)

        self.school = SchoolFactory()
        self.year = AcademicYearFactory(school=self.school, is_active=True)
        self.grade = GradeLevelFactory(school=self.school, name="X")
        self.subject = SubjectFactory(school=self.school)
        self.teacher = TeacherFactory(school=self.school)
        self.assignment = GradeAssignmentFactory(
            grade_level=self.grade,
            subject=self.subject,
            teacher=self.teacher,
            academic_year=self.year,
        )
        self.component = AssessmentComponentFactory(
            subject=self.subject,
            academic_year=self.year,
            component_type="UH",
        )

    def test_teacher_can_enter_score_for_assigned_subject(self):
        self.client.force_authenticate(user=self.teacher.user_account)
        response = self.client.post(
            "/api/v1/assessment/scores/",
            {
                "student": self.student.id,
                "subject": self.subject.id,
                "component": self.component.id,
                "semester": self.year.id,
                "value": "85.00",
            },
        )
        assert response.status_code == 201

    def test_teacher_cannot_score_subject_not_assigned(self):
        unassigned_subject = SubjectFactory(school=self.school)
        self.client.force_authenticate(user=self.teacher.user_account)
        response = self.client.post(
            "/api/v1/assessment/scores/",
            {
                "student": self.student.id,
                "subject": unassigned_subject.id,
                "component": self.component.id,
                "semester": self.year.id,
                "value": "90.00",
            },
        )
        assert response.status_code == 422
```

Rules:
- `setup_method` on the test class sets up shared fixtures (the `setup` pattern from xUnit)
- Use `client.force_authenticate(user=user)` — don't go through the login endpoint in every test
- Assert the response status code first, then the response body
- Check both the happy path and the error path for each endpoint

---

## 9. Testing with Dates (freezegun)

Use `freezegun` for anything that depends on the current date or `AcademicYear.is_active`.

```python
import pytest
from freezegun import freeze_time


@pytest.mark.integration
@freeze_time("2025-07-15")
def test_active_year_returns_correct_year(db):
    from apps.core.services import get_active_academic_year
    school = SchoolFactory()
    AcademicYearFactory(school=school, label="2025/2026", semester="GANJIL", is_active=True)

    year = get_active_academic_year(school)
    assert year.label == "2025/2026"
    assert year.semester == "GANJIL"
```

Decorator form (`@freeze_time`) is preferred over `with freeze_time(...)` for clarity.

---

## 10. Testing Celery Tasks

Use `CELERY_TASK_ALWAYS_EAGER = True` in test settings so tasks run synchronously without a broker.

```python
# apps/students/tests/test_tasks.py
import pytest
from apps.students.tasks import process_student_import


@pytest.mark.integration
@pytest.mark.django_db
def test_process_student_import_creates_students(db):
    from apps.students.tests.factories import ImportBatchFactory
    batch = ImportBatchFactory(status="VALIDATED")

    result = process_student_import(batch.id)

    assert result["created"] == 10
    assert result["errors"] == 0
    batch.refresh_from_db()
    assert batch.status == "COMPLETED"
```

For testing task retry behavior or async execution, use `pytest-celery` or `django-celery-results` — not needed until task retry logic exists.

---

## 11. What to Test

For every new service function, write:

- **Happy path** — the normal case works correctly
- **One meaningful edge case** — duplicate NISN, missing required field, unauthorized access

For every new API endpoint, write:

- **Happy path** — POST/GET succeeds with valid data
- **Auth required** — unauthenticated request returns 401
- **Permission denied** — wrong role returns 403
- **Validation error** — invalid data returns 422 with correct `errors` structure
- **Not found** — accessing non-existent ID returns 404

For every Celery task, write:

- **Success** — task produces the expected result
- **Failure with bad data** — task handles errors gracefully and updates batch status

---

## 12. What Not to Test

- **Don't test Django model internals** — save/get/delete cycles are tested by Django itself
- **Don't test third-party library behavior** — `djangorestframework-simplejwt` token generation is not this project's responsibility
- **Don't write tests for code that doesn't exist yet** — tests are written alongside the code they cover
- **Don't assert internal implementation details** — test behavior, not how the code achieves it (e.g., don't assert a queryset was constructed a certain way)
- **Don't mock what you're not responsible for** — if a service calls `GradeAssignment.objects.create`, don't mock that call in the test; let it hit the DB

---

## 13. Running Tests

```bash
# All tests, parallel, with coverage
pytest -n auto --cov

# Stop on first failure
pytest -x

# Watch mode (re-run on file change)
pytest --watch

# With verbose output
pytest -v -n auto

# Specific app
pytest apps/students/ -n auto

# Specific test file
pytest apps/students/tests/test_services.py -v
```

CI runs: `pytest -n auto --cov --cov-report=xml`
