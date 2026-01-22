"""Base HTTP client for external API integrations."""

from typing import Any

import aiohttp

from bot.utils.logging import get_logger

logger = get_logger("api_client")


class APIClient:
    """Base async HTTP client for external APIs."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        *,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the API client.

        Args:
            session: Shared aiohttp session.
            base_url: Base URL for API requests.
            default_headers: Default headers to include in all requests.
        """
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint (will be appended to base_url).
            json: JSON body for the request.
            params: Query parameters.
            headers: Additional headers (merged with defaults).

        Returns:
            Parsed JSON response.

        Raises:
            aiohttp.ClientError: On network errors.
            ValueError: On non-JSON responses.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)

        logger.debug(f"{method} {url}")

        async with self.session.request(
            method,
            url,
            json=json,
            params=params,
            headers=request_headers,
        ) as response:
            response.raise_for_status()

            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                text = await response.text()
                raise ValueError(f"Non-JSON response: {text[:200]}")

    async def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self._request(
            "POST", endpoint, json=json, params=params, headers=headers
        )
