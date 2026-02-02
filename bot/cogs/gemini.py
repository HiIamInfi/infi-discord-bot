"""Gemini AI integration cog."""

import discord
from discord import app_commands
from discord.ext import commands

from bot.services.gemini import GeminiService
from bot.utils.logging import get_logger

logger = get_logger("cogs.gemini")

# Maximum response length for Discord
MAX_MESSAGE_LENGTH = 2000


def split_response(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Split a long response into chunks that fit Discord's message limit.

    Tries to split on paragraph breaks, then newlines, then spaces.

    Args:
        text: The text to split.
        max_length: Maximum length per chunk.

    Returns:
        List of text chunks.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Find a good split point
        chunk = remaining[:max_length]

        # Try to split on paragraph break
        split_pos = chunk.rfind("\n\n")
        if split_pos == -1 or split_pos < max_length // 2:
            # Try to split on newline
            split_pos = chunk.rfind("\n")
        if split_pos == -1 or split_pos < max_length // 2:
            # Try to split on space
            split_pos = chunk.rfind(" ")
        if split_pos == -1 or split_pos < max_length // 2:
            # Hard split as last resort
            split_pos = max_length

        chunks.append(remaining[:split_pos].rstrip())
        remaining = remaining[split_pos:].lstrip()

    return chunks


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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handle messages that reply to another message and mention the bot.

        Args:
            message: The incoming message.
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # Check if bot is mentioned
        if not self.bot.user or self.bot.user not in message.mentions:
            return

        # Check if it's a reply to another message
        if not message.reference or not message.reference.message_id:
            return

        if self.gemini is None:
            return

        # Get the referenced message
        try:
            referenced = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            return

        # Extract the user's question (remove the bot mention)
        question = message.content
        for mention in message.mentions:
            question = question.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
        question = question.strip()

        if not question:
            question = "What do you think about this?"

        # Build the prompt with context
        prompt = f"""Someone is asking about this message:

---
**{referenced.author.display_name}** said:
{referenced.content}
---

Their question: {question}"""

        logger.info(f"User {message.author.id} asking about message {referenced.id}: {question[:50]}...")

        try:
            async with message.channel.typing():
                response = await self.gemini.generate(prompt)

            chunks = split_response(response)

            # Reply to the user's message
            await message.reply(chunks[0], mention_author=False)

            # Send remaining chunks as follow-ups
            for chunk in chunks[1:]:
                async with message.channel.typing():
                    await message.channel.send(chunk)

        except Exception as e:
            logger.error(f"Gemini reply error: {e}")
            await message.reply(f"Sorry, I couldn't process that: {e}", mention_author=False)

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

            # Show typing indicator while generating
            async with interaction.channel.typing():
                response = await self.gemini.generate(prompt)

            # Split into multiple messages if needed
            chunks = split_response(response)

            # Send first chunk as followup to the interaction
            await interaction.followup.send(chunks[0])

            # Send remaining chunks as regular messages
            for chunk in chunks[1:]:
                async with interaction.channel.typing():
                    await interaction.channel.send(chunk)

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            await interaction.followup.send(
                f"An error occurred while generating a response: {e}",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    """Load the Gemini cog."""
    await bot.add_cog(Gemini(bot))
