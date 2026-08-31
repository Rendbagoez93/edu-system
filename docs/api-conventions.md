# API Conventions

This document is the **authoritative reference** for how the REST API is structured: URL naming, pagination, error responses, authentication, and schema generation. When implementing a new endpoint, this document decides the shape — not the last view written.

---

## 1. URL Naming

### Base prefix

All API endpoints live under `/api/v1/`.

```
/api/v1/{app}/{resource}/
```

| App | URL prefix | Examples |
|---|---|---|
| `core` | `/api/v1/core/` | `/api/v1/schools/`, `/api/v1/academic-years/` |
| `academic_structure` | `/api/v1/academic-structure/` | `/api/v1/grade-levels/`, `/api/v1/subjects/` |
| `teachers` | `/api/v1/teachers/` | `/api/v1/teachers/` |
| `students` | `/api/v1/students/` | `/api/v1/students/`, `/api/v1/enrollments/` |
| `schedules` | `/api/v1/schedules/` | `/api/v1/time-slots/` |
| `grade_management` | `/api/v1/grade-management/` | `/api/v1/grade-assignments/` |
| `assessment` | `/api/v1/assessment/` | `/api/v1/scores/`, `/api/v1/report-cards/` |
| `onboarding` | `/api/v1/onboarding/` | `/api/v1/onboarding/progress/` |

### Nested resources

Use path segments, not query parameters, for resource ownership:

```
GET /api/v1/grade-management/grade-assignments/{id}/  ← specific assignment
GET /api/v1/assessment/scores/?student=5&subject=2     ← filter by student (search/filter)

# NOT:
GET /api/v1/students/{id}/grades/                      ← ambiguous
GET /api/v1/teachers/{id}/assignments/                ← cross-app reach-around
```

Cross-app reads go through the owning app's endpoint with filters, not a sub-resource on the referenced model. `teachers/{id}/assignments/` would be a read-only view that proxies into `grade_management`'s endpoint — the actual source of truth stays in `grade_management`.

### HTTP verbs

| Verb | Use | Idempotent |
|---|---|---|
| `GET` | Retrieve one or many resources | Yes |
| `POST` | Create a resource | No |
| `PUT` / `PATCH` | Update (full / partial) | PUT yes, PATCH no |
| `DELETE` | Soft-delete | No (sets `is_deleted=True`) |

Use `PATCH` for partial updates (e.g., change homeroom teacher on a class section). Use `PUT` only for full replacement.

### File uploads

File endpoints use `POST`. The import endpoint on `students` is:

```
POST /api/v1/students/import/   → ImportBatch creation + async processing
GET  /api/v1/students/import-batches/{id}/   → check import status
```

### URL segment rules

- **Hyphen-separated lowercase** for all segments: `grade-assignments`, not `gradeAssignments` or `grade_assignments`
- **Singular for singleton resources**: `/api/v1/onboarding/progress/` (one record per school)
- **No verbs in URLs**: `POST /api/v1/assessment/scores/` not `POST /api/v1/assessment/record-score/`

---

## 2. Authentication

JWT via `djangorestframework-simplejwt`.

### Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/token/` | `POST` | Obtain token pair (access + refresh) |
| `/api/v1/auth/token/refresh/` | `POST` | Refresh access token |
| `/api/v1/auth/me/` | `GET` | Current user profile |

### Obtaining a token

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "email": "admin@school.sch",
    "password": "..."
}
```

```json
{
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
}
```

### Using the token

```http
GET /api/v1/assessment/scores/
Authorization: Bearer <jwt_access_token>
```

All endpoints require authentication unless explicitly marked otherwise.

---

## 3. Pagination

`PageNumberPagination` with `page_size=20`. Response envelope:

```json
{
    "count": 142,
    "next": "http://api/v1/students/?page=2",
    "previous": null,
    "results": [
        { ... }
    ]
}
```

| Field | Type | Notes |
|---|---|---|
| `count` | `int` | Total number of matching records |
| `next` | `string\|null` | URL to next page, or `null` on last page |
| `previous` | `string\|null` | URL to previous page, or `null` on first page |
| `results` | `array` | Page of resource objects |

### Controlling page size

```
GET /api/v1/students/?page=2&page_size=50
```

Max `page_size` is `100`. Clients that request more receive `100`.

### Non-paginated endpoints

Use `paginate = False` (custom attribute) on the view for:
- Bulk export downloads (CSV/Excel — handled as file responses, not JSON)
- Singleton resources (e.g., `/api/v1/onboarding/progress/`)

---

## 4. Error Response Envelope

**No custom exception handler is configured yet.** Until it is, DRF's default `{ "detail": "..." }` is in use. The first view written must establish the convention by wiring a custom handler. Define it once in `config/exception_handler.py` and register it in REST_FRAMEWORK in both local.py and production.py:

```python
REST_FRAMEWORK = {
    # ...
    "EXCEPTION_HANDLER": "config.exception_handler.custom_exception_handler",
}
```

### Standard envelope

All API errors return a JSON object with at minimum a `code` and `message`:

```json
{
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed.",
    "errors": [
        {
            "field": "nisn",
            "message": "This field must contain exactly 10 digits."
        }
    ]
}
```

### Per-status error shapes

**400 Bad Request — Validation error:**
```json
{
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed.",
    "errors": [
        {"field": "nisn", "message": "This field is required."},
        {"field": "guardian_contact", "message": "Enter a valid phone number."}
    ]
}
```

**401 Unauthorized:**
```json
{
    "code": "AUTHENTICATION_FAILED",
    "message": "Authentication credentials were not provided or are invalid."
}
```

**403 Forbidden:**
```json
{
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
    "code": "NOT_FOUND",
    "message": "<resource> with id <id> was not found."
}
```

**409 Conflict:**
```json
{
    "code": "SLOT_CONFLICT",
    "message": "Teacher is already assigned to another class during this time slot.",
    "errors": [
        {"field": "time_slot", "message": "Slot already occupied by: Matematika — X IPA 1"}
    ]
}
```

**422 Unprocessable Entity — Business rule violation:**
```json
{
    "code": "UNAUTHORIZED_GRADE",
    "message": "You are not assigned to this subject for the requested grade level.",
    "errors": []
}
```

**500 Internal Server Error:**
```json
{
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please try again."
}
```

### Rules

- `code` is always uppercase `SCREAMING_SNAKE_CASE`, machine-readable
- `message` is human-readable, in Bahasa Indonesia for user-facing errors
- `errors` is a flat list of `{field, message}` — never nested — for field-level validation errors
- HTTP status codes are set correctly; `code` does not duplicate the status meaning
- `detail` as a bare string (DRF default) must not appear in new code

---

## 5. Filter, Search, and Sort

Filter backends are configured globally (can be overridden per view):

| Backend | Applied to | Notes |
|---|---|---|
| `DjangoFilterBackend` | Any field | Use `filterset_fields` on views, or a `FilterSet` class for complex filters |
| `SearchFilter` | `?search=` | Use `search_fields` on views |
| `OrderingFilter` | `?ordering=` | Use `ordering_fields` on views |

### Filtering example

```
GET /api/v1/students/?gender=LAKI_LAKI&class_section=5&is_active=true
GET /api/v1/assessment/scores/?student=3&semester=2025/2026-GANJIL
```

### Search example

```
GET /api/v1/students/?search=budi
```

Searches across fields declared in `search_fields` on the view (usually `name`, `nisn`, `nis`).

### Ordering example

```
GET /api/v1/students/?ordering=name
GET /api/v1/students/?ordering=-date_of_birth
```

Only fields in `ordering_fields` on the view are accepted. Unknown ordering fields are silently ignored.

---

## 6. drf-spectacular — Schema Generation

Every view that is reachable from a URL **must** have a schema annotation via `@extend_schema`. Do not rely on DRF's auto-schema for anything that matters.

### Tags

Match the SPECTACULAR_SETTINGS tags in `config/settings/local.py` / `production.py`:

| Tag | App |
|---|---|
| `core` | `core` |
| `academic_structure` | `academic_structure` |
| `teachers` | `teachers` |
| `students` | `students` |
| `schedules` | `schedules` |
| `grade_management` | `grade_management` |
| `assessment` | `assessment` |
| `onboarding` | `onboarding` |

### Serializer as schema

Every request/response body is described by a serializer, not a raw dict. `extend_schema` references the serializer by name:

```python
from core.serializers import SchoolSerializer

@extend_schema(
    tags=["core"],
    request=SchoolSerializer,
    responses={200: SchoolSerializer},
)
def create_school(self, request):
    ...
```

If `responses` is omitted, DRF infers from the serializer. If the response is not a simple serializer, document it explicitly.

### OpenAPI generation command

```bash
python manage.py spectacular --file schema.yml
```

Schema is generated from `drf-spectacular`, not hand-written.

---

## 7. Common Patterns

### Soft delete in list views

List views return only non-deleted records by default (filter `is_deleted=False`). Include `?include_deleted=true` only for admin/debug endpoints that need to see deleted records.

### Celery tasks are fire-and-forget from the API

The import endpoint returns a `202 Accepted` with the `ImportBatch` ID immediately. The client polls `GET /api/v1/students/import-batches/{id}/` for status updates.

```http
POST /api/v1/students/import/
→ 202 Accepted
{
    "id": 7,
    "status": "PENDING",
    "file_name": "students.xlsx",
    "row_count": 0,
    "error_count": 0
}
```

### Role-based access (to implement)

| Role | Access |
|---|---|
| `HEADMASTER` | Full read/write on all apps |
| `ADMIN` | Full read/write on all apps |
| `TEACHER` | Read own assignments; write scores for assigned subjects only |
| `STUDENT` | Read own scores and report cards |
| `PARENT` | Read own children's scores and report cards |

Until roles beyond HEADMASTER/ADMIN are implemented, all authenticated users get full access. Implement `IsAdminOrReadOnly`, then expand to `IsTeacherForAssignedGrade` for score entry.

---

## 8. Content Types

- **Read/Write:** `application/json`
- **File uploads (import):** `multipart/form-data`
- **File downloads (export):** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (`.xlsx`)

---

## 9. CORS

`django-cors-headers` is installed but not yet configured. Until CORS settings are added, the API is not accessible from a browser-based frontend running on a different origin. Configure `CORS_ALLOWED_ORIGINS` in `production.py` before deploying.
