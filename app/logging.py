"""Logging configuration for the application."""

import logging
import sys
from typing import Optional


def configure_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with the specified log level.
    
    Args:
        log_level: The log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Clear any existing handlers to avoid duplicate logs
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Configure the root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: The name of the logger (typically the module name)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name) 