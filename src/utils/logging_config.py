"""
Logging configuration for TwistyVoice

This module sets up structured logging for the application.
"""

import logging
import sys
from pathlib import Path

import structlog
from rich.logging import RichHandler


def setup_logging(log_level: str = "INFO"):
    """
    Set up structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        handlers=[
            RichHandler(rich_tracebacks=True),
            logging.FileHandler(logs_dir / "twistyvoice.log")
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("twilio").setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
