from __future__ import annotations

# Field names whose values must never appear in logs (PII redaction).
# Matched case-insensitively against structlog event_dict keys by
# `shared.logging.redact_pii`.
#
# Source of truth for what is PII:
#   - `docs/data-model.md` (AuditLog "Never log" note)
#   - `docs/architecture-design-pattern.md` §8 (PII redaction)
#   - `CLAUDE.md` (structlog conventions)
PII_FIELD_NAMES: frozenset[str] = frozenset(
    {
        # Student identifiers and contact info
        "nisn",
        "nis",
        "date_of_birth",
        "guardian_name",
        "guardian_contact",
        "guardian_relation",
        "phone",
        # Teacher identifiers and contact info
        "nuptk",
        "nip",
        "contact_phone",
        # Student performance data
        "value",
    }
)

# Replacement string for redacted PII values in log events.
PII_REDACTED: str = "[REDACTED]"
