"""General commands cog."""

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import models
from bot.utils.logging import get_logger

logger = get_logger("cogs.general")


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the general cog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot
        self.start_time = datetime.now(timezone.utc)

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command,
    ) -> None:
        """Log slash command usage.

        Args:
            interaction: The interaction.
            command: The command that was executed.
        """
        # Get database from bot
        db = getattr(self.bot, "db", None)
        if db is None:
            return

        await models.log_command(
            db,
            guild_id=interaction.guild_id,
            channel_id=interaction.channel_id,
            user_id=interaction.user.id,
            command_name=command.qualified_name,
            command_args=str(interaction.data.get("options", [])),
            success=True,
        )

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check bot latency.

        Args:
            interaction: The interaction.
        """
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency_ms}ms")

    @app_commands.command(name="info", description="Show bot information")
    async def info(self, interaction: discord.Interaction) -> None:
        """Show bot information.

        Args:
            interaction: The interaction.
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            title="Bot Information",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="Uptime", value=uptime_str)
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)))
        embed.add_field(
            name="discord.py",
            value=discord.__version__,
        )

        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @commands.command(name="ping")
    async def ping_text(self, ctx: commands.Context) -> None:
        """Check bot latency (text command).

        Args:
            ctx: Command context.
        """
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency_ms}ms")


async def setup(bot: commands.Bot) -> None:
    """Load the general cog."""
    await bot.add_cog(General(bot))
