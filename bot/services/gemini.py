"""Google Gemini API service."""

from google import genai
from google.genai import types

from bot.utils.logging import get_logger

logger = get_logger("gemini")


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        """Initialize the Gemini service.

        Args:
            api_key: Google AI Studio API key.
            model: Model name to use (default: gemini-2.0-flash).
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        logger.info(f"Gemini service initialized with model: {model}")

    async def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 1024,
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
        max_tokens: int = 1024,
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
                max_output_tokens=max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Empty response from Gemini")

        return response.text
