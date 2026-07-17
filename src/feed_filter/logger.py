"""
Structured logging setup using structlog.

This module provides a configured logger for the application with
structured JSON output suitable for production environments.
"""

import logging
import sys
from typing import cast

import structlog
from structlog.typing import Processor

from feed_filter.config import settings


def setup_logging() -> None:
    """Configure structlog for structured logging."""
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]

    # Use JSON formatting in production, console formatting in development
    if settings.is_production:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Configured structlog logger
    """
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


# Setup logging on module import
setup_logging()

# Default logger for the application
logger = get_logger(__name__)
