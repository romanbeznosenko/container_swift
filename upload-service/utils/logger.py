"""
Logging configuration for the application.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with console and file handlers.

    Args:
        name: Name of the logger
        level: Logging level

    Returns:
        Logger instance
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    file_handler = RotatingFileHandler(
        f"logs/{name}.log",
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
