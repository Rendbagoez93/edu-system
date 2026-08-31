"""Tests for service-layer base exceptions."""

from __future__ import annotations

import pytest

from apps.shared.exceptions import (
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ServiceError,
    ValidationError,
)


@pytest.mark.unit
class TestServiceError:
    def test_defaults(self):
        exc = ServiceError()
        assert exc.message == "Service error."
        assert exc.code == "SERVICE_ERROR"
        assert exc.http_status == 400
        assert exc.errors == []
        assert str(exc) == "Service error."

    def test_custom_message(self):
        exc = ServiceError("something went wrong")
        assert exc.message == "something went wrong"
        assert str(exc) == "something went wrong"

    def test_errors_list_is_copied(self):
        original = [{"field": "name", "message": "required"}]
        exc = ServiceError("bad", errors=original)
        original.append({"field": "x"})
        # Mutating the caller's list should not leak into the exception.
        assert exc.errors == [{"field": "name", "message": "required"}]


@pytest.mark.unit
class TestSubclasses:
    @pytest.mark.parametrize(
        ("cls", "code", "status"),
        [
            (ValidationError, "VALIDATION_ERROR", 400),
            (NotFoundError, "NOT_FOUND", 404),
            (PermissionDeniedError, "PERMISSION_DENIED", 403),
            (ConflictError, "CONFLICT", 409),
            (BusinessRuleViolation, "BUSINESS_RULE_VIOLATION", 422),
        ],
    )
    def test_subclass_defaults(self, cls, code, status):
        exc = cls()
        assert exc.code == code
        assert exc.http_status == status
        assert isinstance(exc, ServiceError)

    def test_subclass_accepts_message_and_errors(self):
        exc = NotFoundError(
            "Student with id 5 was not found.",
            errors=[{"field": "id", "message": "not found"}],
        )
        assert exc.code == "NOT_FOUND"
        assert exc.http_status == 404
        assert exc.message == "Student with id 5 was not found."
        assert exc.errors == [{"field": "id", "message": "not found"}]
