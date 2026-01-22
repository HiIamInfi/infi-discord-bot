"""Watch2Gether API service."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bot.services.api_client import APIClient
from bot.utils.logging import get_logger

if TYPE_CHECKING:
    import aiohttp

logger = get_logger("watch2gether")


@dataclass
class W2GRoom:
    """A Watch2Gether room."""

    id: str
    streamkey: str
    url: str


class Watch2GetherService:
    """Service for interacting with Watch2Gether API."""

    BASE_URL = "https://api.w2g.tv"

    def __init__(
        self,
        session: "aiohttp.ClientSession",
        api_key: str | None = None,
    ) -> None:
        """Initialize the Watch2Gether service.

        Args:
            session: Shared aiohttp session.
            api_key: Optional W2G API key (increases rate limits).
        """
        self.api_key = api_key

        headers = {}
        if api_key:
            headers["W2G-API-KEY"] = api_key

        self.client = APIClient(
            session,
            self.BASE_URL,
            default_headers=headers,
        )
        logger.info("Watch2Gether service initialized")

    async def create_room(
        self,
        video_url: str | None = None,
        *,
        bg_color: str = "#000000",
        bg_opacity: int = 100,
    ) -> W2GRoom:
        """Create a new Watch2Gether room.

        Args:
            video_url: Optional video URL to preload in the room.
            bg_color: Background color (hex).
            bg_opacity: Background opacity (0-100).

        Returns:
            Created room information.

        Raises:
            aiohttp.ClientError: On API errors.
        """
        payload: dict = {
            "w2g_api_key": self.api_key or "",
            "share": video_url or "",
            "bg_color": bg_color,
            "bg_opacity": str(bg_opacity),
        }

        logger.debug(f"Creating W2G room with video: {video_url or 'none'}")

        response = await self.client.post(
            "/rooms/create.json",
            json=payload,
        )

        room_id = response.get("streamkey", "")
        room_url = f"https://w2g.tv/rooms/{room_id}"

        logger.info(f"Created W2G room: {room_url}")

        return W2GRoom(
            id=response.get("id", ""),
            streamkey=room_id,
            url=room_url,
        )
