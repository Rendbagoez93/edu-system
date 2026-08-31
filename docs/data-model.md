# Data Model — Field-Level Schema

This document is the **authoritative schema** for every model in the system. It complements the architecture doc's module-level summary with exact field names, types, and constraints. If a model in code diverges from this document, the model and this document are reconciled — this document is not updated silently.

> **Note:** `config/settings/test.py` is referenced in `pyproject.toml` (`DJANGO_SETTINGS_MODULE = "config.settings.test"`) but does not yet exist. Create it before running tests.

---

## apps/core/models.py

### School

Primary identity record. One per deployment.

```python
class School(TimestampMixin, SoftDeleteMixin, models.Model):
    npsn          = models.CharField(max_length=8, unique=True)
    nss           = models.CharField(max_length=12, blank=True, null=True)
    name          = models.CharField(max_length=255)
    address       = models.TextField()
    level         = models.CharField(max_length=4, choices=SchoolLevel.choices)
    kepala_sekolah = models.CharField(max_length=255)   # Headmaster name
    phone         = models.CharField(max_length=20, blank=True, null=True)
    email         = models.EmailField(blank=True, null=True)
    logo          = models.ImageField(upload_to="school_logos/", blank=True, null=True)
```

- **Level choices:** `SD`, `SMP`, `SMA`, `SMK` (TextChoices: `SchoolLevel`)
- `npsn` is 8 digits; validate with `^\d{8}$`
- `logo` upload path: `"school_logos/{school_npsn}/{filename}"`

### AcademicYear

```python
class AcademicYear(TimestampMixin, SoftDeleteMixin, models.Model):
    label     = models.CharField(max_length=9)   # "2025/2026"
    semester  = models.CharField(max_length=6, choices=SemesterType.choices)
    is_active = models.BooleanField(default=False)
```

- **Unique constraint:** `(label, semester)` — one GANJIL and one GENAP per calendar year
- **Invariant:** exactly one `is_active=True` per `School` at any time. Enforce in `services.py`, not at the DB level.
- `label` format: 4 digits `/` 4 digits. Validate: `^\d{4}/\d{4}$`

### User

Django auth `AbstractUser` subclass. **No `username` field.**

```python
class User(TimestampMixin, SoftDeleteMixin, models.Model):
    # Inherits: email, password, first_name, last_name, is_staff, is_active, date_joined
    role      = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.ADMIN)
    teacher   = models.OneToOneField("teachers.Teacher", blank=True, null=True,
                                     on_delete=models.SET_NULL, related_name="user_account")
```

- **Roles:** `HEADMASTER`, `ADMIN`
- `teacher` link is nullable — Admin accounts are not required to be linked to a Teacher
- Auth: `djangorestframework-simplejwt`; login is email + password

### AuditLog

Immutable event log. No soft delete, no update.

```python
class AuditLog(models.Model):
    timestamp    = models.DateTimeField(auto_now_add=True, db_index=True)
    user         = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    action       = models.CharField(max_length=10, choices=AuditAction.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id    = models.CharField(max_length=255)
    changes      = models.JSONField(blank=True, null=True)   # {"field": [old, new], ...}
```

- **Never log:** `Score.value`, `Student.nisn`, `Student.guardian_contact`, `Student.date_of_birth`, `Teacher.nuptk`
- `object_id` is `CharField` (supports UUID, int, and string PKs)
- `changes` is `None` for DELETE actions; `{"field": [null, "new_value"]}` for CREATE

### PersonnelProfile (Future — not yet implemented)

Non-domain personnel: Admin Staff, Nurse, Librarian, Security, etc. — roles that have no rich domain data beyond contact info and role type. One model in `core`, roles as `TextChoices`. Promote to a dedicated Django app only when the role develops genuine domain complexity (e.g., Nurse needs medical certificates → `health` app with `NurseProfile`; Librarian manages inventory → `library` app).

```python
class PersonnelProfile(TimestampMixin, SoftDeleteMixin, models.Model):
    class Role(TextChoices):
        ADMIN_STAFF = "ADMIN_STAFF", "Admin Staff"
        NURSE = "NURSE", "Nurse"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        SECURITY = "SECURITY", "Security"
        # extend as needed

    user = models.OneToOneField("core.User", on_delete=models.CASCADE,
                                related_name="personnel_profile")
    role = models.CharField(max_length=20, choices=Role.choices)
    department = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # role-specific data (license no., shift, etc.)
```

- **Unique constraint:** `(user)` — one profile per user account
- `notes` is intentionally free-form to absorb role-specific data that doesn't warrant a separate app yet
- Do **not** add fields here that belong in a dedicated domain app — if a role needs rich domain data, it gets its own app, not more columns on `PersonnelProfile`

---

## apps/academic_structure/models.py

### GradeLevel

Represents Tingkat (grade level: X, XI, XII for SMA; 1–6 for SD).

```python
class GradeLevel(TimestampMixin, SoftDeleteMixin, models.Model):
    name        = models.CharField(max_length=5)   # "X", "XI", "XII", "1", "6"
    school      = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_levels")
```

- **Unique constraint:** `(school, name)` — Tingkat X is unique per school
- Ordering: `name` ascending (numeric sort for 1–6; lexical for X/XI/XII)

### Major

Jurusan/Peminatan (academic stream). Optional — primary schools (SD) may have none.

```python
class Major(TimestampMixin, SoftDeleteMixin, models.Model):
    name    = models.CharField(max_length=100)   # "IPA", "IPS", "AKL", "DKV"
    school  = models.ForeignKey(School, on_delete=models.CASCADE, related_name="majors")
    is_active = models.BooleanField(default=True)
```

- **Unique constraint:** `(school, name)`

### Subject

Mata Pelajaran (subject).

```python
class Subject(TimestampMixin, SoftDeleteMixin, models.Model):
    name      = models.CharField(max_length=100)   # "Matematika", "Bahasa Indonesia"
    code      = models.CharField(max_length=10)   # "MTK", "BIN"
    school    = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    is_active = models.BooleanField(default=True)
```

- **Unique constraint:** `(school, code)` — code is unique per school

### ClassSection

Kelas (class section): the specific classroom, e.g. "X IPA 1".

```python
class ClassSection(TimestampMixin, SoftDeleteMixin, models.Model):
    name              = models.CharField(max_length=20)   # "X IPA 1", "XI IPS 2"
    grade_level       = models.ForeignKey(GradeLevel, on_delete=models.CASCADE,
                                         related_name="class_sections")
    major             = models.ForeignKey(Major, blank=True, null=True,
                                          on_delete=models.SET_NULL,
                                          related_name="class_sections")
    academic_year     = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                         related_name="class_sections")
    homeroom_teacher  = models.ForeignKey("teachers.Teacher", blank=True, null=True,
                                          on_delete=models.SET_NULL,
                                          related_name="homeroom_sections")
```

- **Unique constraint:** `(grade_level, major, academic_year, name)` — prevents duplicate "X IPA 1" in the same year
- `homeroom_teacher` is the **Wali Kelas**
- FK to `teachers.Teacher` (Layer 2 from Layer 1 — see architecture doc Section 3 cross-app rule: `academic_structure` is allowed to reference `Teacher` for the homeroom relationship)

---

## apps/teachers/models.py

### Teacher

```python
class Teacher(TimestampMixin, SoftDeleteMixin, models.Model):
    nuptk            = models.CharField(max_length=16, blank=True, null=True, unique=True)
    name             = models.CharField(max_length=255)
    employment_status = models.CharField(max_length=10, choices=EmploymentStatus.choices)
    contact_phone    = models.CharField(max_length=20, blank=True, null=True)
    address          = models.TextField(blank=True, null=True)
    email            = models.EmailField(blank=True, null=True)
    school           = models.ForeignKey(School, on_delete=models.CASCADE,
                                         related_name="teachers")
    user_account     = models.OneToOneField("core.User", blank=True, null=True,
                                            on_delete=models.SET_NULL,
                                            related_name="teacher_profile")
```

- `nuptk` is nullable — not all teachers have certification
- `user_account` links to DRF auth; nullable so a Teacher can exist before they get login credentials
- `employment_status` choices: `PNS`, `HONORER`, `GTY`

---

## apps/students/models.py

### Student

```python
class Student(TimestampMixin, SoftDeleteMixin, models.Model):
    nisn                 = models.CharField(max_length=10, unique=True)
    nis                 = models.CharField(max_length=8)
    name                = models.CharField(max_length=255)
    date_of_birth        = models.DateField()
    gender              = models.CharField(max_length=10, choices=GenderType.choices)
    phone               = models.CharField(max_length=20, blank=True, null=True)
    email               = models.EmailField(blank=True, null=True)
    guardian_name       = models.CharField(max_length=255)
    guardian_contact    = models.CharField(max_length=20)
    guardian_relation   = models.CharField(max_length=50, blank=True, null=True)
    phone_same_as_guardian = models.BooleanField(default=False)
    address             = models.TextField()
    school              = models.ForeignKey(School, on_delete=models.CASCADE,
                                            related_name="students")
    user_account        = models.OneToOneField("core.User", blank=True, null=True,
                                               on_delete=models.SET_NULL,
                                               related_name="student_profile")
```

- `nisn`: 10-digit string (preserve leading zeros as string, not int)
- `nis`: 8-digit string, unique per school
- **Unique constraint:** `(school, nis)` — NIS is school-local
- `guardian_contact` is required and never logged (PII)
- `phone_same_as_guardian`: if `True`, `phone` may be omitted even if `phone` is otherwise required

### Enrollment

```python
class Enrollment(TimestampMixin, SoftDeleteMixin, models.Model):
    student       = models.ForeignKey(Student, on_delete=models.CASCADE,
                                      related_name="enrollments")
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE,
                                     related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE,
                                     related_name="enrollments")
    status        = models.CharField(max_length=20, choices=EnrollmentStatus.choices,
                                    default=EnrollmentStatus.ACTIVE)
```

- **Unique constraint:** `(student, class_section, academic_year)` — a student enrolls in exactly one section per year
- `status` choices: `ACTIVE`, `TRANSFERRED`, `GRADUATED`, `DROPPED`
- Active enrollments = students visible in a grade's roster for grading purposes

### ImportBatch

```python
class ImportBatch(TimestampMixin, models.Model):
    file_name   = models.CharField(max_length=255)
    row_count   = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    errors      = models.JSONField(default=list)   # [{"row": int, "field": str, "message": str}]
    status      = models.CharField(max_length=20, choices=ImportBatchStatus.choices,
                                 default=ImportBatchStatus.PENDING)
    imported_by = models.ForeignKey("core.User", on_delete=models.CASCADE,
                                   related_name="import_batches")
```

- `errors` structure: `{"row": 3, "field": "nisn", "message": "Duplicate NISN"}`
- `status` choices: `PENDING`, `VALIDATED`, `COMPLETED`, `FAILED`
- Processing is done by a Celery task (`bulk_import_students` in `students/tasks.py`)

---

## apps/schedules/models.py

### TimeSlot

```python
class TimeSlot(TimestampMixin, SoftDeleteMixin, models.Model):
    day           = models.CharField(max_length=10, choices=DayType.choices)
    period        = models.PositiveSmallIntegerField()   # 1–10
    display_order = models.PositiveSmallIntegerField(default=0)
```

- **Unique constraint:** `(day, period)` — one slot per period per day
- `display_order` is used for UI ordering, not functional logic
- `day` choices: `SENIN`, `SELASA`, `RABU`, `KAMIS`, `JUMAT`, `SABTU`

---

## apps/grade_management/models.py

### GradeAssignment

The core "Grade Management" record: which teacher teaches which subject at which tingkat, when, in a given year.

```python
class GradeAssignment(TimestampMixin, SoftDeleteMixin, models.Model):
    grade_level   = models.ForeignKey("academic_structure.GradeLevel",
                                      on_delete=models.CASCADE,
                                      related_name="assignments")
    subject       = models.ForeignKey("academic_structure.Subject",
                                     on_delete=models.CASCADE,
                                     related_name="assignments")
    teacher       = models.ForeignKey("teachers.Teacher",
                                     on_delete=models.CASCADE,
                                     related_name="grade_assignments")
    time_slot     = models.ForeignKey("schedules.TimeSlot",
                                     on_delete=models.CASCADE,
                                     related_name="assignments")
    academic_year = models.ForeignKey("core.AcademicYear",
                                     on_delete=models.CASCADE,
                                     related_name="grade_assignments")
```

- **Unique constraint:** `(grade_level, subject, academic_year)` — one teacher per subject per tingkat per year
- **Slot conflict check:** before saving, call `schedules.is_slot_available(teacher, time_slot)` via `grade_management`'s service layer. Reject if unavailable.
- This model does NOT track which students are in the grade — that's `Enrollment`

---

## apps/assessment/models.py

### AssessmentComponent

Defines a scoring component type and its weight.

```python
class AssessmentComponent(TimestampMixin, SoftDeleteMixin, models.Model):
    component_type = models.CharField(max_length=10, choices=AssessmentComponentType.choices)
    weight         = models.DecimalField(max_digits=5, decimal_places=2)   # e.g. 25.00
    subject        = models.ForeignKey("academic_structure.Subject",
                                       on_delete=models.CASCADE,
                                       related_name="components")
    academic_year  = models.ForeignKey("core.AcademicYear",
                                       on_delete=models.CASCADE,
                                       related_name="components")
```

- **Unique constraint:** `(subject, component_type, academic_year)` — one weight per component type per subject per year
- `weight` is a percentage; sum of all component weights for a subject should equal 100. Enforce in service, not at DB level.
- `component_type` choices: `TUGAS`, `UH`, `UTS`, `UAS`

### Score

Individual student score for one component in one semester.

```python
class Score(TimestampMixin, SoftDeleteMixin, models.Model):
    student    = models.ForeignKey("students.Student", on_delete=models.CASCADE,
                                   related_name="scores")
    subject    = models.ForeignKey("academic_structure.Subject",
                                   on_delete=models.CASCADE,
                                   related_name="scores")
    component  = models.ForeignKey(AssessmentComponent, on_delete=models.CASCADE,
                                   related_name="scores")
    semester   = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE,
                                   related_name="scores")
    value      = models.DecimalField(max_digits=5, decimal_places=2)
    entered_by = models.ForeignKey("core.User", on_delete=models.SET_NULL,
                                   blank=True, null=True,
                                   related_name="entered_scores")
```

- **Unique constraint:** `(student, subject, component, semester)` — one score per component per student per semester
- **Authorization gate:** before saving, verify `entered_by` (or the request's user) has a `GradeAssignment` for `(grade_level, subject, semester.grade_level, semester)`. Reject if no matching assignment.
- `value` range: `0.00` to `100.00`
- **Never log `value`** (PII — student performance data)

### ReportCard

Per-student per-semester report card snapshot.

```python
class ReportCard(TimestampMixin, SoftDeleteMixin, models.Model):
    student       = models.ForeignKey("students.Student", on_delete=models.CASCADE,
                                      related_name="report_cards")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE,
                                      related_name="report_cards")
    generated_by  = models.ForeignKey("core.User", on_delete=models.SET_NULL,
                                      blank=True, null=True,
                                      related_name="generated_report_cards")
    generated_at  = models.DateTimeField(auto_now_add=True)
    pdf_file      = models.FileField(upload_to="report_cards/", blank=True, null=True)
```

- **Unique constraint:** `(student, academic_year)` — one report card per student per semester
- `pdf_file` is generated asynchronously by a Celery task
- If `pdf_file` is null, the report card is "pending" generation

---

## apps/onboarding/models.py

### OnboardingProgress

```python
class OnboardingProgress(models.Model):
    school      = models.OneToOneField("core.School", on_delete=models.CASCADE)
    current_step = models.PositiveSmallIntegerField(default=1)   # 1–4
    completed_at = models.DateTimeField(blank=True, null=True)
    status       = models.CharField(max_length=20, choices=OnboardingStatus.choices,
                                   default=OnboardingStatus.IN_PROGRESS)
```

- **One record per deployment** (`school` is OneToOne)
- `status` choices: `IN_PROGRESS`, `COMPLETE`, `SKIPPED`
- `completed_at` is set when `status` becomes `COMPLETE` or `SKIPPED`

---

## apps/shared/models.py

No domain models. Shared utilities only.

### Mixins

```python
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
```

---

## Cross-App FK Summary

| From model | FK field | To model | Direction |
|---|---|---|---|
| `GradeLevel` | `school` | `School` | ↓ L1→L0 |
| `Major` | `school` | `School` | ↓ L1→L0 |
| `Subject` | `school` | `School` | ↓ L1→L0 |
| `ClassSection` | `grade_level` | `GradeLevel` | ↓ L1→L1 |
| `ClassSection` | `major` | `Major` | ↓ L1→L1 |
| `ClassSection` | `academic_year` | `AcademicYear` | ↓ L1→L0 |
| `ClassSection` | `homeroom_teacher` | `Teacher` | ↓ L1→L2 |
| `Teacher` | `school` | `School` | ↓ L2→L0 |
| `Teacher` | `user_account` | `User` | ↓ L2→L0 |
| `Student` | `school` | `School` | ↓ L2→L0 |
| `Student` | `user_account` | `User` | ↓ L2→L0 |
| `Enrollment` | `student` | `Student` | ↓ L2→L2 |
| `Enrollment` | `class_section` | `ClassSection` | ↓ L2→L1 |
| `Enrollment` | `academic_year` | `AcademicYear` | ↓ L2→L0 |
| `ImportBatch` | `imported_by` | `User` | ↓ L2→L0 |
| `GradeAssignment` | `grade_level` | `GradeLevel` | ↓ L4→L1 |
| `GradeAssignment` | `subject` | `Subject` | ↓ L4→L1 |
| `GradeAssignment` | `teacher` | `Teacher` | ↓ L4→L2 |
| `GradeAssignment` | `time_slot` | `TimeSlot` | ↓ L4→L3 |
| `GradeAssignment` | `academic_year` | `AcademicYear` | ↓ L4→L0 |
| `AssessmentComponent` | `subject` | `Subject` | ↓ L5→L1 |
| `AssessmentComponent` | `academic_year` | `AcademicYear` | ↓ L5→L0 |
| `Score` | `student` | `Student` | ↓ L5→L2 |
| `Score` | `subject` | `Subject` | ↓ L5→L1 |
| `Score` | `component` | `AssessmentComponent` | ↓ L5→L5 |
| `Score` | `semester` | `AcademicYear` | ↓ L5→L0 |
| `Score` | `entered_by` | `User` | ↓ L5→L0 |
| `ReportCard` | `student` | `Student` | ↓ L5→L2 |
| `ReportCard` | `academic_year` | `AcademicYear` | ↓ L5→L0 |
| `PersonnelProfile` | `user` | `User` | ↓ L0→L0 |
| `OnboardingProgress` | `school` | `School` | ↓ orch→L0 |
