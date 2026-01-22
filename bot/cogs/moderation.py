"""Moderation commands cog."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.logging import get_logger

logger = get_logger("cogs.moderation")


class ConfirmPurgeView(discord.ui.View):
    """Confirmation view for purge command."""

    def __init__(self, author_id: int) -> None:
        super().__init__(timeout=30)
        self.author_id = author_id
        self.confirmed: bool | None = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the command author can confirm.", ephemeral=True
            )
            return
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the command author can cancel.", ephemeral=True
            )
            return
        self.confirmed = False
        self.stop()
        await interaction.response.defer()


class Moderation(commands.Cog):
    """Moderation commands for channel management."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="purge", description="Delete all messages in this channel")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction) -> None:
        """Delete all messages in the current channel.

        Args:
            interaction: The interaction.
        """
        channel = interaction.channel

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.",
                ephemeral=True,
            )
            return

        # Ask for confirmation
        view = ConfirmPurgeView(interaction.user.id)
        await interaction.response.send_message(
            f"**Warning:** This will delete ALL messages in #{channel.name}.\n"
            "This action cannot be undone. Are you sure?",
            view=view,
            ephemeral=True,
        )

        await view.wait()

        if view.confirmed is None:
            await interaction.edit_original_response(
                content="Purge cancelled (timed out).", view=None
            )
            return

        if not view.confirmed:
            await interaction.edit_original_response(
                content="Purge cancelled.", view=None
            )
            return

        await interaction.edit_original_response(
            content="Purging messages...", view=None
        )

        # Delete messages in batches
        deleted_total = 0
        try:
            while True:
                deleted = await channel.purge(limit=100)
                deleted_total += len(deleted)

                if len(deleted) < 100:
                    break

                logger.info(f"Purged {deleted_total} messages so far in #{channel.name}")

        except discord.HTTPException as e:
            logger.error(f"Purge error in #{channel.name}: {e}")
            await interaction.followup.send(
                f"Error during purge after {deleted_total} messages: {e}",
                ephemeral=True,
            )
            return

        logger.info(
            f"User {interaction.user.id} purged {deleted_total} messages in #{channel.name}"
        )

        # Send confirmation (this message will be in the now-empty channel)
        await channel.send(
            f"Channel purged by {interaction.user.mention}. "
            f"Deleted {deleted_total} messages.",
            delete_after=10,
        )


async def setup(bot: commands.Bot) -> None:
    """Load the moderation cog."""
    await bot.add_cog(Moderation(bot))
