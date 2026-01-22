"""Database schema migrations."""

from typing import TYPE_CHECKING

from bot.utils.logging import get_logger

if TYPE_CHECKING:
    from bot.database.connection import Database

logger = get_logger("migrations")

# Schema version to migrations mapping
# Each migration is a list of SQL statements
MIGRATIONS: dict[int, list[str]] = {
    1: [
        # Schema versioning table
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # Command history for logging
        """
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            command_name TEXT NOT NULL,
            command_args TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 1
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_command_history_guild
        ON command_history(guild_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_command_history_user
        ON command_history(user_id)
        """,
        # Guild settings
        """
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            prefix TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # User data for storing user preferences
        """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ],
}

CURRENT_VERSION = max(MIGRATIONS.keys())


async def get_schema_version(db: "Database") -> int:
    """Get the current schema version from the database.

    Args:
        db: Database connection.

    Returns:
        Current schema version (0 if not initialized).
    """
    try:
        row = await db.fetchone(
            "SELECT MAX(version) FROM schema_version"
        )
        return row[0] if row and row[0] else 0
    except Exception:
        # Table doesn't exist yet
        return 0


async def run_migrations(db: "Database") -> None:
    """Run all pending database migrations.

    Args:
        db: Database connection.
    """
    current_version = await get_schema_version(db)
    logger.info(f"Current schema version: {current_version}")

    if current_version >= CURRENT_VERSION:
        logger.info("Database schema is up to date")
        return

    for version in range(current_version + 1, CURRENT_VERSION + 1):
        if version not in MIGRATIONS:
            continue

        logger.info(f"Applying migration version {version}")

        for sql in MIGRATIONS[version]:
            await db.execute(sql)

        # Record the migration
        await db.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (version,),
        )
        await db.commit()

        logger.info(f"Migration version {version} applied successfully")

    logger.info(f"Database migrated to version {CURRENT_VERSION}")
