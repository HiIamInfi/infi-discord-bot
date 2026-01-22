"""Logging configuration for the bot."""

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.config import Settings


def setup_logging(settings: "Settings") -> logging.Logger:
    """Configure and return the bot logger.

    Args:
        settings: Bot configuration settings.

    Returns:
        Configured logger instance.
    """
    level = logging.DEBUG if settings.debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set discord.py logging level
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.WARNING if not settings.debug else logging.INFO)

    # Set aiohttp logging level
    aiohttp_logger = logging.getLogger("aiohttp")
    aiohttp_logger.setLevel(logging.WARNING)

    # Get bot logger
    logger = logging.getLogger("infi")
    logger.setLevel(level)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name under the bot namespace.

    Args:
        name: Logger name (will be prefixed with 'infi.').

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"infi.{name}")
