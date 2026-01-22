"""Custom Discord bot class with initialization logic."""

import aiohttp
import discord
from discord.ext import commands

from bot.config import Settings
from bot.database.connection import Database
from bot.database.migrations import run_migrations
from bot.services.gemini import GeminiService
from bot.services.watch2gether import Watch2GetherService
from bot.utils.logging import get_logger

logger = get_logger("bot")


class InfiBot(commands.Bot):
    """Custom Discord bot with database and service integrations."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the bot.

        Args:
            settings: Bot configuration settings.
        """
        self.settings = settings

        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True  # For text commands

        super().__init__(
            command_prefix=self._get_prefix,
            intents=intents,
            owner_ids=set(settings.discord_owner_ids),
        )

        # These will be initialized in setup_hook
        self.db: Database | None = None
        self.http_session: aiohttp.ClientSession | None = None
        self.gemini: GeminiService | None = None
        self.w2g: Watch2GetherService | None = None
        self._synced: bool = False  # Track if commands have been synced

    async def _get_prefix(
        self,
        bot: commands.Bot,
        message: discord.Message,
    ) -> list[str]:
        """Get the command prefix for a message.

        Allows guild-specific prefixes if configured.

        Args:
            bot: The bot instance.
            message: The message being processed.

        Returns:
            List of valid prefixes.
        """
        # Default prefix
        prefixes = [self.settings.discord_prefix]

        # Could add guild-specific prefix lookup here
        # if message.guild and self.db:
        #     guild_settings = await models.get_guild_settings(self.db, message.guild.id)
        #     if guild_settings and guild_settings.prefix:
        #         prefixes.insert(0, guild_settings.prefix)

        # Always allow mentioning the bot as a prefix
        return commands.when_mentioned_or(*prefixes)(bot, message)

    async def setup_hook(self) -> None:
        """Initialize bot resources before connecting to Discord."""
        logger.info("Running setup hook...")

        # Initialize database
        self.db = Database(self.settings.database_path)
        await self.db.connect()
        await run_migrations(self.db)

        # Initialize shared HTTP session
        self.http_session = aiohttp.ClientSession()

        # Initialize external services
        if self.settings.gemini_api_key:
            self.gemini = GeminiService(self.settings.gemini_api_key)
            logger.info("Gemini service initialized")
        else:
            logger.warning("Gemini API key not set, /ask command will be disabled")

        if self.http_session:
            self.w2g = Watch2GetherService(
                self.http_session,
                api_key=self.settings.w2g_api_key,
            )
            logger.info("Watch2Gether service initialized")

        # Load cogs
        await self._load_cogs()

        logger.info("Setup hook completed")

    async def _load_cogs(self) -> None:
        """Load all cogs."""
        cogs = [
            "bot.utils.error_handler",
            "bot.cogs.admin",
            "bot.cogs.general",
            "bot.cogs.gemini",
            "bot.cogs.watch2gether",
            "bot.cogs.moderation",
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Sync slash commands once on first ready
        if not self._synced:
            try:
                synced = await self.tree.sync()
                cmd_names = ", ".join(cmd.name for cmd in synced)
                logger.info(f"Synced {len(synced)} slash commands globally: {cmd_names}")
                self._synced = True
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")

        # Set presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for /help",
        )
        await self.change_presence(activity=activity)

    async def close(self) -> None:
        """Clean up resources before closing."""
        logger.info("Shutting down bot...")

        # Close HTTP session
        if self.http_session:
            await self.http_session.close()

        # Close database connection
        if self.db:
            await self.db.close()

        await super().close()
        logger.info("Bot shutdown complete")
