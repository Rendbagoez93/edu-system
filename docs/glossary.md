# Glossary — Indonesian ↔ English Term Mapping

This document is the **single source of truth** for terminology used across the codebase. When a name conflicts between modules, this doc wins — not the most-recently-written one. Update this file when a new model field is added; don't update the model and leave this stale.

---

## The "Grade" Problem (Resolved Here)

**"Grade" has exactly one meaning in this codebase: Tingkat / grade level.**

If you are writing code and the word "grade" appears where a score, mark, or markah belongs — stop. That concept is `Score` / `Nilai`. The confusion is understandable because Indonesian school administration uses "nilai" and "grade" in overlapping ways, but in this codebase:

| What you mean | Use this | Never call it |
|---|---|---|
| Grade level (X, XI, XII) | `GradeLevel`, `name` | `grade`, `score`, `mark` |
| A student's mark | `Score`, `value` | `grade`, `final_grade` |
| A student's report card | `ReportCard`, `nilai_akhir` | `grade_sheet` |
| A class section | `ClassSection`, `name` (e.g. "X IPA 1") | `grade`, `kelas` (as a field name) |

---

## Field Name Conventions

### core

| Concept | Field name | Type | Notes |
|---|---|---|---|
| School name | `name` | `CharField(255)` | |
| National School ID | `npsn` | `CharField(8)` | 8-digit Kemdikbud number |
| School Statistics Number | `nss` | `CharField(12)` | Nullable |
| School address | `address` | `TextField` | |
| School level | `level` | `CharField` + `TextChoices` | `SD` / `SMP` / `SMA` / `SMK` |
| Headmaster name | `kepala_sekolah` | `CharField(255)` | |
| School phone | `phone` | `CharField(20)` | Nullable |
| School email | `email` | `EmailField` | Nullable |
| School logo | `logo` | `ImageField` | Nullable, upload to `school_logos/` |
| Academic year label | `label` | `CharField(9)` | Format: `"2025/2026"` |
| Semester | `semester` | `CharField` + `TextChoices` | `GANJIL` / `GENAP` |
| Active year flag | `is_active` | `BooleanField` | Only one active per school |
| Admin user | `email` | `EmailField` | **No `username` field** |
| Admin password | (managed by Django auth) | | |
| Admin role | `role` | `CharField` + `TextChoices` | `HEADMASTER` / `ADMIN` |
| AuditLog actor | `user` | `ForeignKey(User)` | Nullable for system events |
| AuditLog action | `action` | `CharField` + `TextChoices` | `CREATE` / `UPDATE` / `DELETE` |
| AuditLog target | `content_type` + `object_id` | `ForeignKey(ContentType)` + `CharField` | |
| AuditLog changes | `changes` | `JSONField` | Before/after snapshot |

### core — PersonnelProfile (Future)

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Linked user account | `user` | `OneToOneField(User)` | One profile per user |
| Personnel role | `role` | `CharField` + `TextChoices` | `ADMIN_STAFF` / `NURSE` / `LIBRARIAN` / `SECURITY` |
| Department | `department` | `CharField(100)` | Nullable |
| Contact phone | `contact_phone` | `CharField(20)` | Nullable |
| Address | `address` | `TextField` | Nullable |
| Role-specific notes | `notes` | `TextField` | Nullable; absorb role-specific data before promoting to dedicated app |

### academic_structure

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Grade level name | `name` | `CharField(5)` | e.g. `"X"`, `"XI"`, `"XII"`, `"1"`, `"6"` |
| School level | `school_level` | `ForeignKey(School.level)` | Derived from `School`, not stored on model |
| Major/Jurusan name | `name` | `CharField(100)` | e.g. `"IPA"`, `"IPS"`, `"AKL"` |
| Major is active | `is_active` | `BooleanField` | Default `True` |
| Subject name | `name` | `CharField(100)` | e.g. `"Matematika"`, `"Bahasa Indonesia"` |
| Subject code | `code` | `CharField(10)` | e.g. `"MTK"`, `"BIN"` — unique per school |
| Class section name | `name` | `CharField(20)` | e.g. `"X IPA 1"`, `"XI IPS 2"` |
| Class section | `grade_level` | `ForeignKey(GradeLevel)` | |
| Class section | `major` | `ForeignKey(Major)` | Nullable (not all levels have majors) |
| Class section year | `academic_year` | `ForeignKey(AcademicYear)` | |
| Homeroom teacher | `homeroom_teacher` | `ForeignKey(Teacher)` | Nullable; the **Wali Kelas** |

### teachers

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Teacher certification number | `nuptk` | `CharField(16)` | 16-digit; unique, nullable for non-certified |
| Teacher name | `name` | `CharField(255)` | Full name |
| Employment status | `employment_status` | `CharField` + `TextChoices` | `PNS` / `HONORER` / `GTY` |
| Contact phone | `contact_phone` | `CharField(20)` | Nullable |
| Address | `address` | `TextField` | Nullable |
| Email | `email` | `EmailField` | Nullable; used for User account linkage |
| Linked user account | `user` | `ForeignKey(User)` | Nullable; links to DRF auth |

### students

| Concept | Field name | Type | Notes |
|---|---|---|---|
| National Student ID | `nisn` | `CharField(10)` | 10-digit; **unique**, required |
| School Student ID | `nis` | `CharField(8)` | Unique per school |
| Student name | `name` | `CharField(255)` | Full name |
| Date of birth | `date_of_birth` | `DateField` | |
| Gender | `gender` | `CharField` + `TextChoices` | `LAKI_LAKI` / `PEREMPUAN` |
| Phone number | `phone` | `CharField(20)` | Nullable |
| Email | `email` | `EmailField` | Nullable |
| Guardian name | `guardian_name` | `CharField(255)` | Required |
| Guardian contact | `guardian_contact` | `CharField(20)` | Phone number — **never log this** |
| Guardian relation | `guardian_relation` | `CharField(50)` | e.g. `"Ayah"`, `"Ibu"`, `"Wali"` |
| Same phone as guardian | `phone_same_as_guardian` | `BooleanField` | Default `False` |
| Address | `address` | `TextField` | |
| Enrollment — student | `student` | `ForeignKey(Student)` | |
| Enrollment — class section | `class_section` | `ForeignKey(ClassSection)` | |
| Enrollment — academic year | `academic_year` | `ForeignKey(AcademicYear)` | |
| Enrollment — status | `status` | `CharField` + `TextChoices` | `ACTIVE` / `TRANSFERRED` / `GRADUATED` / `DROPPED` |
| ImportBatch — file name | `file_name` | `CharField(255)` | |
| ImportBatch — row count | `row_count` | `PositiveIntegerField` | |
| ImportBatch — error count | `error_count` | `PositiveIntegerField` | |
| ImportBatch — errors | `errors` | `JSONField` | List of `{row, field, message}` |
| ImportBatch — status | `status` | `CharField` + `TextChoices` | `PENDING` / `VALIDATED` / `COMPLETED` / `FAILED` |
| ImportBatch — imported by | `imported_by` | `ForeignKey(User)` | |

### schedules

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Day of week | `day` | `CharField` + `TextChoices` | `SENIN` / `SELASA` / `RABU` / `KAMIS` / `JUMAT` / `SABTU` |
| Period number | `period` | `PositiveSmallIntegerField` | e.g. `1`–`10` |
| Slot display label | `display_order` | `PositiveSmallIntegerField` | For ordering in UI |

### grade_management

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Assignment — grade level | `grade_level` | `ForeignKey(GradeLevel)` | The **Tingkat** |
| Assignment — subject | `subject` | `ForeignKey(Subject)` | The **Mata Pelajaran** |
| Assignment — teacher | `teacher` | `ForeignKey(Teacher)` | The assigned teacher |
| Assignment — time slot | `time_slot` | `ForeignKey(TimeSlot)` | Checked for conflicts before save |
| Assignment — academic year | `academic_year` | `ForeignKey(AcademicYear)` | |
| Unique constraint | `(grade_level, subject, academic_year)` | | One teacher per subject per tingkat per year |

### assessment

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Component type | `component_type` | `CharField` + `TextChoices` | `TUGAS` / `UH` / `UTS` / `UAS` |
| Component weight | `weight` | `DecimalField(max_digits=5, decimal_places=2)` | Percentage, e.g. `25.00` |
| Score — student | `student` | `ForeignKey(Student)` | |
| Score — subject | `subject` | `ForeignKey(Subject)` | |
| Score — component | `component` | `ForeignKey(AssessmentComponent)` | |
| Score — semester | `semester` | `ForeignKey(AcademicYear)` | Filter to active semester |
| Score — value | `value` | `DecimalField(max_digits=5, decimal_places=2)` | **Never log this field** |
| Score — entered by | `entered_by` | `ForeignKey(User)` | The teacher or admin who entered |
| Score — unique together | `(student, subject, component, semester)` | | One score per component per student per semester |
| ReportCard — student | `student` | `ForeignKey(Student)` | |
| ReportCard — academic year | `academic_year` | `ForeignKey(AcademicYear)` | |
| ReportCard — generated at | `generated_at` | `DateTimeField(auto_now_add=True)` | |
| ReportCard — PDF | `pdf_file` | `FileField` | Generated by Celery task |

### onboarding

| Concept | Field name | Type | Notes |
|---|---|---|---|
| Current step | `current_step` | `PositiveSmallIntegerField` | `1`–`4` |
| Completed timestamp | `completed_at` | `DateTimeField` | Nullable until COMPLETE |
| Onboarding status | `status` | `CharField` + `TextChoices` | `IN_PROGRESS` / `COMPLETE` / `SKIPPED` |

### shared

| Mixin | Fields added |
|---|---|
| `TimestampMixin` | `created_at` (`DateTimeField`), `updated_at` (`DateTimeField(auto_now=True)`) |
| `SoftDeleteMixin` | `is_deleted` (`BooleanField(default=False)`), `deleted_at` (`DateTimeField` nullable) |

---

## TextChoices Enums

Every status/type field uses `TextChoices`. Do not use bare string constants.

```python
class SemesterType(TextChoices):
    GANJIL = "GANJIL", "Ganjil"
    GENAP = "GENAP", "Genap"

class GenderType(TextChoices):
    LAKI_LAKI = "LAKI_LAKI", "Laki-laki"
    PEREMPUAN = "PEREMPUAN", "Perempuan"

class EmploymentStatus(TextChoices):
    PNS = "PNS", "PNS"
    HONORER = "HONORER", "Honorer"
    GTY = "GTY", "Guru Tidak Tetap"

class EnrollmentStatus(TextChoices):
    ACTIVE = "ACTIVE", "Aktif"
    TRANSFERRED = "TRANSFERRED", "Pindah"
    GRADUATED = "GRADUATED", "Lulus"
    DROPPED = "DROPPED", "Dropout"

class AssessmentComponentType(TextChoices):
    TUGAS = "TUGAS", "Tugas"
    UH = "UH", "Ulangan Harian"
    UTS = "UTS", "Ujian Tengah Semester"
    UAS = "UAS", "Ujian Akhir Semester"

class AuditAction(TextChoices):
    CREATE = "CREATE", "Created"
    UPDATE = "UPDATE", "Updated"
    DELETE = "DELETE", "Deleted"

class ImportBatchStatus(TextChoices):
    PENDING = "PENDING", "Pending"
    VALIDATED = "VALIDATED", "Validated"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"

class OnboardingStatus(TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETE = "COMPLETE", "Complete"
    SKIPPED = "SKIPPED", "Skipped"

class PersonnelRole(TextChoices):  # Future — not yet implemented
    ADMIN_STAFF = "ADMIN_STAFF", "Admin Staff"
    NURSE = "NURSE", "Nurse"
    LIBRARIAN = "LIBRARIAN", "Librarian"
    SECURITY = "SECURITY", "Security"
```

---

## What Not to Call Things

| Wrong | Correct | Why |
|---|---|---|
| `student_number`, `student_id` | `nisn` or `nis` | `nisn` is the canonical national ID; `nis` is the school-local ID |
| `grade`, `final_grade`, `mark` | `Score.value` | "Grade" = Tingkat only |
| `kelas` as a field name | `class_section` | `Kelas` can mean grade level or class section; `class_section` is unambiguous |
| `class_name` | `ClassSection.name` | `name` on `ClassSection` already holds the full name like "X IPA 1" |
| `teacher_id`, `instructor` | `Teacher` FK field | Standard FK naming via `related_name` |
| `score_value` | `Score.value` | `value` is sufficient; the model is already `Score` |
| `phone_number` | `phone` | Consistent with `contact_phone` on `Teacher` |
| `parent_contact` | `guardian_contact` | School administration convention |
| `year` | `academic_year` or `label` | `label` holds the string "2025/2026"; `academic_year` is the FK |
| `semester` as free text | `AcademicYear.semester` via FK | Use the enum, not a raw string |
