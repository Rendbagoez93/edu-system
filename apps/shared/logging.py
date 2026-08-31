"""Structlog processors and logger factory.

`redact_pii` is wired into the global processor chain by
`config/settings/logging.py`. Importing `get_logger` from here (instead of
calling `structlog.get_logger` directly) keeps the logging contract — and
any future configuration changes — in one place.
"""

from __future__ import annotations

from typing import Any

import structlog
from structlog.types import EventDict, Processor

from apps.shared.constants import PII_FIELD_NAMES, PII_REDACTED


def redact_pii(
    _logger: Any,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Replace values for known PII keys with `[REDACTED]`.

    Matched case-insensitively against the structlog event_dict keys.
    Only top-level keys are inspected — values nested inside dicts/lists
    are left alone (callers should not embed PII inside aggregate values).
    """
    for key in list(event_dict):
        if key.lower() in PII_FIELD_NAMES:
            event_dict[key] = PII_REDACTED
    return event_dict


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)


# Export the processor under its conventional name for the settings module.
__all__ = ["redact_pii", "get_logger", "Processor"]
