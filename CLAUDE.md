# CLAUDE.md — School Management System

Conventions for generating code in this repo. The supporting docs in `docs/` and `.claude/design-pattern/` are the authoritative references for their domains — this file is the day-to-day coding contract, not a repeat of those docs.

## Before Making Any Decision

Before writing or changing any code, read in this order — don't skip straight to writing:

1. **`.claude/design-pattern/architecture-design-pattern.md`** — which module owns this, which layer it sits in, and what it's allowed to depend on.
2. **`.claude/design-pattern/about-me.md`** — how to think, decide, and communicate while doing it.
3. **`docs/glossary.md`** — canonical Indonesian↔English term mapping and exact field names. "Grade" = Tingkat, never a score. `nisn` not `student_number`. Resolve terminology here before writing a field.
4. **`docs/data-model.md`** — exact field names, types, constraints, and FK targets for every model. A field in code that diverges from this doc is a bug.
5. **`docs/api-conventions.md`** — URL naming, pagination shape, error envelope, and drf-spectacular patterns. When implementing a new endpoint, this doc decides the shape.
6. **`pyproject.toml`** — what's already available. Check this before reaching for a new dependency; Excel I/O, JWT, and schema generation are already covered.
7. **The `config/settings/` directory** — how the project is actually wired: installed apps, environment split, Celery/DB config. Generated code that contradicts current settings is a bug even if it looks correct in isolation.
8. **The relevant module itself** — the specific app's existing `models.py` / `services.py` / `selectors.py` / etc. New code matches what's already there; it doesn't introduce a second style for the same job.

Skipping this pass is how layer violations, dependency-list guesses, terminology drift, and inconsistent API shapes happen — each one is cheap to prevent up front and expensive to find in review.

## Project Context

Django modular monolith, deployed single-tenant (one Postgres + one Django process per school). No multi-tenancy code, no `tenant_id` — every deployment serves exactly one school. Admin auth is email-based, no username field.

## Module Boundaries (quick reference)

| App | Layer | Owns |
|---|---|---|
| `core` | 0 | School identity, Academic Year, User, AuditLog |
| `shared` | 0 | Base mixins, structlog processors — no domain models |
| `academic_structure` | 1 | GradeLevel, Major, Subject, ClassSection |
| `teachers` | 2 | Teacher profiles only |
| `students` | 2 | Student, Enrollment, bulk import |
| `schedules` | 3 | TimeSlot, conflict checks |
| `grade_management` | 4 | GradeAssignment (Tingkat ↔ Teacher ↔ Subject ↔ Schedule) |
| `assessment` | 5 | AssessmentComponent, Score, ReportCard |
| `onboarding` | orchestrator | First-run wizard only, no domain data |

**The one rule that matters most:** dependencies flow one direction — a lower-layer app never imports from a higher one. Cross-app access always goes through the owning app's service/selector function, never a direct ORM query into another app's models. If `assessment` needs to know if a teacher is assigned to a grade, it calls `grade_management`'s selector — it does not query `GradeAssignment` itself.

## Coding Conventions

### Imports
- All imports at the top of the file. Standard library → third-party → first-party (Django/local apps), in that order — this is what `ruff check --fix` enforces, so run it rather than hand-ordering.
- No imports inside a function or class body, with one exception: breaking a genuine circular import between two apps. If you do this, add a one-line comment saying why — an unexplained inline import reads as a mistake, not a decision.

### Functions do one thing
- If a function both validates input and persists it, split it into two. Validation, computation, and persistence are three different jobs even when they're always called together — e.g. `validate_import_row()`, then `enroll_student()`, composed by `bulk_import_students()` rather than one function inlining all three.
- A service function that's grown past ~30–40 lines is a signal it's doing more than one job — split it before adding to it.
- Reject "manager" or "helper" functions that do three or more unrelated things under one name.

### Clean logic, easy to read
- Guard clauses and early returns over nested `if`/`else`. Flatten, don't nest.
- Names describe what the code does; comments explain why, not what — a comment restating the line above it should be deleted, not written.
- Type hints on every function signature — this project already leans on pydantic and DRF serializers for shape validation, so untyped function boundaries are the weak link.
- Prefer explicit code over clever one-liners or long chained querysets — a query worth splitting across three lines is more debuggable than one dense line.

### Modularity
- One Django app per bounded context, per the table above. Don't add a model to an app it doesn't belong to because it's "easier" — add the cross-app service call instead.
- Views and serializers stay thin: a view calls exactly one service function and translates the result into a response. Business logic never lives in a view, a serializer's `validate()`, or a model's `save()` override.
- Shared logic that two or more apps need lives in `shared` — never copy-pasted between apps.

### Productivity
- Use `select_related()` / `prefetch_related()` proactively anywhere a service or view touches a related object in a loop — don't ship an N+1 query and fix it after the fact.
- Reuse `shared/` mixins (timestamps, soft delete) instead of re-implementing them per app.
- Don't build an abstraction for a second use case that doesn't exist yet — the fastest code to write is the code you don't have to write twice.

### Using the dependencies properly
- **pydantic-settings** — all config/env values go through a settings class. Never scatter `os.environ.get()` calls through the codebase.
- **structlog** — structured calls only: `logger.info("event_name", key=value)`, never an f-string message. Never log NISN, guardian contact info, date of birth, or `Score` values, per the architecture doc's PII rule — this applies to every log call, not just ones that look sensitive at a glance.
- **drf-spectacular** — every view's request/response shape must be described by a serializer, not a raw dict, or the generated schema silently goes stale.
- **django-filter** — list-endpoint filtering goes through a declarative `FilterSet`, not manual `request.GET.get(...)` parsing in the view.
- **Celery** — anything that isn't instant (report card PDF generation, bulk student import processing, notifications) is a task, not inline in a request/response cycle.
- Before adding a new dependency, check `pyproject.toml` first — Excel I/O, JWT, and schema generation are already covered; a new package for one of those is very likely redundant.

## Testing

Full guide: **`docs/testing-guide.md`** — directory structure, factory patterns, fixture conventions, marker usage (unit/integration/feature), and API testing via APIClient.

Summary

- `pytest-django` + `factory-boy`: one factory per model, living in `<app>/tests/factories.py`.
- Arrange–Act–Assert, one behavior asserted per test — not one giant test walking through five assertions.
- `freezegun` for anything that depends on the active `AcademicYear` or a date comparison.
- Run: `pytest -n auto --cov`

## Anti-patterns to reject on sight

- A lower-layer app importing from a higher-layer app, or any direct cross-app ORM query.
- Business logic inside a view, a serializer's `validate()`, or a model's `save()` override.
- Bare `except:` clauses.
- PII in a log line, in any form.
- A function doing more than one job because splitting it "felt like overkill."

## Commands

- Lint/format: `ruff check . && ruff format .`
- Test: `pytest -n auto --cov`
