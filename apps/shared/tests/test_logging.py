"""Tests for the PII-redaction structlog processor."""

from __future__ import annotations

import pytest

from apps.shared.constants import PII_FIELD_NAMES, PII_REDACTED
from apps.shared.logging import redact_pii


@pytest.mark.unit
class TestRedactPii:
    def test_redacts_nisn_field(self):
        event_dict = {"event": "student_created", "nisn": "1234567890", "name": "Budi"}
        redact_pii(None, "info", event_dict)
        assert event_dict["nisn"] == PII_REDACTED
        # Non-PII keys pass through untouched.
        assert event_dict["name"] == "Budi"
        assert event_dict["event"] == "student_created"

    def test_redacts_score_value(self):
        event_dict = {"event": "score_recorded", "value": "85.50"}
        redact_pii(None, "info", event_dict)
        assert event_dict["value"] == PII_REDACTED

    def test_redacts_guardian_contact(self):
        event_dict = {"guardian_contact": "081234567890", "guardian_name": "Budi Sr."}
        redact_pii(None, "info", event_dict)
        assert event_dict["guardian_contact"] == PII_REDACTED
        assert event_dict["guardian_name"] == PII_REDACTED

    def test_match_is_case_insensitive(self):
        event_dict = {"NISN": "1234567890", "Guardian_Contact": "081234567890"}
        redact_pii(None, "info", event_dict)
        assert event_dict["NISN"] == PII_REDACTED
        assert event_dict["Guardian_Contact"] == PII_REDACTED

    def test_non_pii_keys_pass_through(self):
        event_dict = {
            "event": "student_created",
            "name": "Budi",
            "school_id": 1,
            "grade_level": "X",
            "tags": ["new", "active"],
        }
        original = dict(event_dict)
        redact_pii(None, "info", event_dict)
        assert event_dict == original

    def test_empty_event_dict(self):
        event_dict: dict = {}
        redact_pii(None, "info", event_dict)
        assert event_dict == {}

    def test_pii_field_names_constant_is_frozen(self):
        # Guard against accidental mutation — the constant is shared across
        # the whole project and a mutation here would silently weaken
        # redaction everywhere.
        with pytest.raises(AttributeError):
            PII_FIELD_NAMES.add("password")  # type: ignore[attr-defined]

    def test_processor_returns_event_dict(self):
        event_dict = {"nisn": "1234567890"}
        result = redact_pii(None, "info", event_dict)
        assert result is event_dict
