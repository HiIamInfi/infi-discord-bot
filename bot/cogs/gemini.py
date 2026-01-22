"""Gemini AI integration cog."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.services.gemini import GeminiService
from bot.utils.logging import get_logger

logger = get_logger("cogs.gemini")

# Maximum response length for Discord
MAX_RESPONSE_LENGTH = 2000


class Gemini(commands.Cog):
    """Google Gemini AI commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Gemini cog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot

    @property
    def gemini(self) -> GeminiService | None:
        """Get the Gemini service from the bot."""
        return getattr(self.bot, "gemini", None)

    @app_commands.command(name="ask", description="Ask Gemini AI a question")
    @app_commands.describe(prompt="Your question or prompt for the AI")
    async def ask(
        self,
        interaction: discord.Interaction,
        prompt: str,
    ) -> None:
        """Ask Gemini a question.

        Args:
            interaction: The interaction.
            prompt: The user's prompt.
        """
        if self.gemini is None:
            await interaction.response.send_message(
                "Gemini AI is not configured. Please set the GEMINI_API_KEY.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            logger.info(f"User {interaction.user.id} asking: {prompt[:50]}...")
            response = await self.gemini.generate(prompt)

            # Truncate if too long for Discord
            if len(response) > MAX_RESPONSE_LENGTH:
                response = response[: MAX_RESPONSE_LENGTH - 100]
                response += "\n\n*[Response truncated due to length]*"

            # Create embed for nicer formatting
            embed = discord.Embed(
                description=response,
                color=discord.Color.blue(),
            )
            embed.set_footer(text=f"Prompt: {prompt[:100]}...")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            await interaction.followup.send(
                f"An error occurred while generating a response: {e}",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    """Load the Gemini cog."""
    await bot.add_cog(Gemini(bot))
