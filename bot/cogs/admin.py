"""Admin cog for bot management commands."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.logging import get_logger

logger = get_logger("cogs.admin")


class Admin(commands.Cog):
    """Owner-only commands for managing the bot."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the admin cog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Check if the user is a bot owner.

        Args:
            ctx: Command context.

        Returns:
            True if the user is an owner.
        """
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="load")
    @commands.is_owner()
    async def load_cog(self, ctx: commands.Context, cog: str) -> None:
        """Load a cog.

        Args:
            ctx: Command context.
            cog: Name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"bot.cogs.{cog}")
            await ctx.send(f"Loaded `{cog}`")
            logger.info(f"Loaded cog: {cog}")
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to load `{cog}`: {e}")
            logger.error(f"Failed to load cog {cog}: {e}")

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Unload a cog.

        Args:
            ctx: Command context.
            cog: Name of the cog to unload.
        """
        if cog == "admin":
            await ctx.send("Cannot unload the admin cog.")
            return

        try:
            await self.bot.unload_extension(f"bot.cogs.{cog}")
            await ctx.send(f"Unloaded `{cog}`")
            logger.info(f"Unloaded cog: {cog}")
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to unload `{cog}`: {e}")
            logger.error(f"Failed to unload cog {cog}: {e}")

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Reload a cog.

        Args:
            ctx: Command context.
            cog: Name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"bot.cogs.{cog}")
            await ctx.send(f"Reloaded `{cog}`")
            logger.info(f"Reloaded cog: {cog}")
        except commands.ExtensionError as e:
            await ctx.send(f"Failed to reload `{cog}`: {e}")
            logger.error(f"Failed to reload cog {cog}: {e}")

    @app_commands.command(name="sync", description="Sync slash commands")
    @app_commands.guilds()  # Empty means global
    async def sync_commands(
        self,
        interaction: discord.Interaction,
        guild_only: bool = False,
    ) -> None:
        """Sync slash commands to Discord.

        Args:
            interaction: The interaction.
            guild_only: If True, sync only to the current guild.
        """
        # Check if user is owner
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(
                "This command is owner-only.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if guild_only and interaction.guild:
            # Sync to current guild only (faster for testing)
            self.bot.tree.copy_global_to(guild=interaction.guild)
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                f"Synced {len(synced)} commands to this guild."
            )
            logger.info(f"Synced {len(synced)} commands to guild {interaction.guild.id}")
        else:
            # Global sync
            synced = await self.bot.tree.sync()
            await interaction.followup.send(
                f"Synced {len(synced)} commands globally."
            )
            logger.info(f"Synced {len(synced)} commands globally")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context) -> None:
        """Shutdown the bot.

        Args:
            ctx: Command context.
        """
        logger.info("Shutdown requested by owner")
        await ctx.send("Shutting down...")
        await self.bot.close()


async def setup(bot: commands.Bot) -> None:
    """Load the admin cog."""
    await bot.add_cog(Admin(bot))
