"""Watch2Gether integration cog."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.services.watch2gether import Watch2GetherService
from bot.utils.logging import get_logger

logger = get_logger("cogs.watch2gether")


class Watch2Gether(commands.Cog):
    """Watch2Gether room creation commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Watch2Gether cog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot

    @property
    def w2g(self) -> Watch2GetherService | None:
        """Get the Watch2Gether service from the bot."""
        return getattr(self.bot, "w2g", None)

    @app_commands.command(
        name="watch",
        description="Create a Watch2Gether room to watch videos together",
    )
    @app_commands.describe(
        url="Optional video URL to preload in the room (YouTube, etc.)"
    )
    async def watch(
        self,
        interaction: discord.Interaction,
        url: str | None = None,
    ) -> None:
        """Create a Watch2Gether room.

        Args:
            interaction: The interaction.
            url: Optional video URL to preload.
        """
        if self.w2g is None:
            await interaction.response.send_message(
                "Watch2Gether service is not available.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            room = await self.w2g.create_room(url)

            embed = discord.Embed(
                title="Watch2Gether",
                description=f"**{interaction.user.display_name}** created a room!\n\n[Join Room]({room.url})",
                color=discord.Color.from_rgb(253, 189, 0)
            )

            await interaction.followup.send(embed=embed)
            logger.info(
                f"User {interaction.user.id} created W2G room: {room.streamkey}"
            )

        except Exception as e:
            logger.error(f"Watch2Gether error: {e}")
            await interaction.followup.send(
                f"Failed to create Watch2Gether room: {e}",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    """Load the Watch2Gether cog."""
    await bot.add_cog(Watch2Gether(bot))
