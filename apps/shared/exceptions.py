from __future__ import annotations

from typing import Any


class ServiceError(Exception):
    code: str = "SERVICE_ERROR"
    http_status: int = 400

    def __init__(
        self,
        message: str = "Service error.",
        *,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.errors: list[dict[str, Any]] = list(errors) if errors else []

    def __str__(self) -> str:
        return self.message


class ValidationError(ServiceError):
    code = "VALIDATION_ERROR"
    http_status = 400


class NotFoundError(ServiceError):
    code = "NOT_FOUND"
    http_status = 404


class PermissionDeniedError(ServiceError):
    code = "PERMISSION_DENIED"
    http_status = 403


class ConflictError(ServiceError):
    code = "CONFLICT"
    http_status = 409


class BusinessRuleViolation(ServiceError):
    code = "BUSINESS_RULE_VIOLATION"
    http_status = 422
