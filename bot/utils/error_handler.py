"""Global error handling for the bot."""

import traceback

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.logging import get_logger

logger = get_logger("error_handler")


class ErrorHandler(commands.Cog):
    """Global error handling cog."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the error handler.

        Args:
            bot: The bot instance.
        """
        self.bot = bot
        # Set up the app command error handler
        self.bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        """Handle errors from text commands.

        Args:
            ctx: Command context.
            error: The error that occurred.
        """
        # Unwrap the error if it's wrapped
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return  # Silently ignore unknown commands

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: `{error.param.name}`")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument: {error}")
            return

        if isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"You need these permissions: {perms}")
            return

        if isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await ctx.send(f"I need these permissions: {perms}")
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send("This command is owner-only.")
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Command on cooldown. Try again in {error.retry_after:.1f}s"
            )
            return

        # Log unexpected errors
        logger.error(
            f"Unexpected error in command {ctx.command}: {error}",
            exc_info=error,
        )
        await ctx.send("An unexpected error occurred. Please try again later.")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle errors from slash commands.

        Args:
            interaction: The interaction that triggered the error.
            error: The error that occurred.
        """
        # Unwrap the error if it's wrapped
        error = getattr(error, "original", error)

        # Helper to send error message
        async def send_error(message: str) -> None:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)

        if isinstance(error, app_commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await send_error(f"You need these permissions: {perms}")
            return

        if isinstance(error, app_commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            await send_error(f"I need these permissions: {perms}")
            return

        if isinstance(error, app_commands.CommandOnCooldown):
            await send_error(
                f"Command on cooldown. Try again in {error.retry_after:.1f}s"
            )
            return

        if isinstance(error, app_commands.CheckFailure):
            await send_error("You don't have permission to use this command.")
            return

        # Log unexpected errors
        command_name = (
            interaction.command.name if interaction.command else "unknown"
        )
        logger.error(
            f"Unexpected error in slash command {command_name}: {error}",
            exc_info=error,
        )

        # Log full traceback for debugging
        logger.debug(traceback.format_exc())

        await send_error("An unexpected error occurred. Please try again later.")


async def setup(bot: commands.Bot) -> None:
    """Load the error handler cog."""
    await bot.add_cog(ErrorHandler(bot))
