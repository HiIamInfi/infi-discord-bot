"""Google Gemini API service."""

from pathlib import Path

from google import genai
from google.genai import types

from bot.utils.logging import get_logger

logger = get_logger("gemini")

DEFAULT_SYSTEM_PROMPT = """You are a friendly and helpful assistant in a Discord server. \
Keep your responses conversational and natural. \
You can use Discord markdown formatting (bold, italic, code blocks, etc.) when appropriate."""


def load_system_prompt(path: Path | None = None) -> str:
    """Load system prompt from file or return default.

    Args:
        path: Path to the system prompt file.

    Returns:
        The system prompt text.
    """
    if path and path.exists():
        prompt = path.read_text(encoding="utf-8").strip()
        if prompt:
            logger.info(f"Loaded system prompt from {path}")
            return prompt
    logger.info("Using default system prompt")
    return DEFAULT_SYSTEM_PROMPT


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3-flash-preview",
        system_prompt: str | None = None,
    ) -> None:
        """Initialize the Gemini service.

        Args:
            api_key: Google AI Studio API key.
            model: Model name to use.
            system_prompt: System instruction for the model.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        logger.info(f"Gemini service initialized with model: {model}")

    async def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 8192,
    ) -> str:
        """Generate a response from Gemini.

        Args:
            prompt: The user's prompt.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text response.

        Raises:
            Exception: On API errors.
        """
        logger.debug(f"Generating response for prompt: {prompt[:50]}...")

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                max_output_tokens=max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        return response.text

    async def chat(
        self,
        message: str,
        history: list[types.Content] | None = None,
        *,
        max_tokens: int = 8192,
    ) -> str:
        """Have a chat conversation with Gemini.

        Args:
            message: The user's message.
            history: Optional conversation history.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text response.
        """
        contents = list(history) if history else []
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                max_output_tokens=max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        return response.text
