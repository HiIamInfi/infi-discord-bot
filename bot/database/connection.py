"""Database connection management."""

from pathlib import Path

import aiosqlite

from bot.utils.logging import get_logger

logger = get_logger("database")


class Database:
    """Async SQLite database connection manager."""

    def __init__(self, db_path: Path) -> None:
        """Initialize database manager.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    @property
    def connection(self) -> aiosqlite.Connection:
        """Get the active database connection.

        Raises:
            RuntimeError: If database is not connected.
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection

    async def connect(self) -> None:
        """Establish database connection and configure settings."""
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Connecting to database at {self.db_path}")
        self._connection = await aiosqlite.connect(self.db_path)

        # Enable WAL mode for better concurrent read performance
        await self._connection.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        await self._connection.execute("PRAGMA foreign_keys=ON")
        # Set busy timeout to 5 seconds
        await self._connection.execute("PRAGMA busy_timeout=5000")

        await self._connection.commit()
        logger.info("Database connected successfully")

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            logger.info("Closing database connection")
            await self._connection.close()
            self._connection = None

    async def execute(
        self,
        sql: str,
        parameters: tuple = (),
    ) -> aiosqlite.Cursor:
        """Execute a SQL statement.

        Args:
            sql: SQL statement to execute.
            parameters: Parameters for the SQL statement.

        Returns:
            Cursor object.
        """
        return await self.connection.execute(sql, parameters)

    async def executemany(
        self,
        sql: str,
        parameters: list[tuple],
    ) -> aiosqlite.Cursor:
        """Execute a SQL statement with multiple parameter sets.

        Args:
            sql: SQL statement to execute.
            parameters: List of parameter tuples.

        Returns:
            Cursor object.
        """
        return await self.connection.executemany(sql, parameters)

    async def fetchone(
        self,
        sql: str,
        parameters: tuple = (),
    ) -> aiosqlite.Row | None:
        """Execute a query and fetch one result.

        Args:
            sql: SQL query to execute.
            parameters: Parameters for the SQL query.

        Returns:
            Single row or None.
        """
        cursor = await self.execute(sql, parameters)
        return await cursor.fetchone()

    async def fetchall(
        self,
        sql: str,
        parameters: tuple = (),
    ) -> list[aiosqlite.Row]:
        """Execute a query and fetch all results.

        Args:
            sql: SQL query to execute.
            parameters: Parameters for the SQL query.

        Returns:
            List of rows.
        """
        cursor = await self.execute(sql, parameters)
        return await cursor.fetchall()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.connection.commit()
