"""Main entry point for the bot."""

import asyncio
import sys

from bot.bot import InfiBot
from bot.config import get_settings
from bot.utils.logging import setup_logging


def main() -> None:
    """Run the bot."""
    # Load settings
    settings = get_settings()

    # Set up logging
    logger = setup_logging(settings)

    logger.info(f"Starting bot in {settings.environment} mode")
    logger.info(f"Debug: {settings.debug}")

    # Create and run bot
    bot = InfiBot(settings)

    try:
        asyncio.run(bot.start(settings.discord_token))
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
