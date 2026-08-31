
import logging
import sys

import structlog
from structlog.types import Processor

from apps.shared.logging import redact_pii


def configure_logging(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.INFO

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # Runs last in the pre-render chain so non-PII context is already
        # in place. Replaces known PII fields with "[REDACTED]" — see
        # `apps/shared/constants.py` for the field set.
        redact_pii,
    ]

    if debug:
        # Local: human-readable plain text
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Production: structured JSON
        shared_processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=False,
    )

    # Configure Python stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    # Environment-specific loggers
    logging.getLogger("django").setLevel(logging.INFO)
    logging.getLogger("django.server").setLevel(logging.INFO)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
