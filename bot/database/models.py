"""Database models and query functions."""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bot.database.connection import Database


@dataclass
class CommandRecord:
    """A logged command execution."""

    id: int
    guild_id: int | None
    channel_id: int
    user_id: int
    command_name: str
    command_args: str | None
    executed_at: datetime
    success: bool


@dataclass
class GuildSettings:
    """Settings for a Discord guild."""

    guild_id: int
    prefix: str | None
    updated_at: datetime


@dataclass
class UserData:
    """Stored data for a user."""

    user_id: int
    data: dict[str, Any]
    updated_at: datetime


async def log_command(
    db: "Database",
    *,
    guild_id: int | None,
    channel_id: int,
    user_id: int,
    command_name: str,
    command_args: str | None = None,
    success: bool = True,
) -> None:
    """Log a command execution to the database.

    Args:
        db: Database connection.
        guild_id: ID of the guild (None for DMs).
        channel_id: ID of the channel.
        user_id: ID of the user who executed the command.
        command_name: Name of the command.
        command_args: Command arguments as string.
        success: Whether the command succeeded.
    """
    await db.execute(
        """
        INSERT INTO command_history
        (guild_id, channel_id, user_id, command_name, command_args, success)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (guild_id, channel_id, user_id, command_name, command_args, int(success)),
    )
    await db.commit()


async def get_guild_settings(
    db: "Database",
    guild_id: int,
) -> GuildSettings | None:
    """Get settings for a guild.

    Args:
        db: Database connection.
        guild_id: ID of the guild.

    Returns:
        Guild settings or None if not found.
    """
    row = await db.fetchone(
        "SELECT guild_id, prefix, updated_at FROM guild_settings WHERE guild_id = ?",
        (guild_id,),
    )
    if row is None:
        return None

    return GuildSettings(
        guild_id=row[0],
        prefix=row[1],
        updated_at=datetime.fromisoformat(row[2]),
    )


async def set_guild_prefix(
    db: "Database",
    guild_id: int,
    prefix: str | None,
) -> None:
    """Set the command prefix for a guild.

    Args:
        db: Database connection.
        guild_id: ID of the guild.
        prefix: New prefix (None to use default).
    """
    await db.execute(
        """
        INSERT INTO guild_settings (guild_id, prefix, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(guild_id) DO UPDATE SET
            prefix = excluded.prefix,
            updated_at = CURRENT_TIMESTAMP
        """,
        (guild_id, prefix),
    )
    await db.commit()


async def get_user_data(
    db: "Database",
    user_id: int,
) -> UserData | None:
    """Get stored data for a user.

    Args:
        db: Database connection.
        user_id: ID of the user.

    Returns:
        User data or None if not found.
    """
    row = await db.fetchone(
        "SELECT user_id, data, updated_at FROM user_data WHERE user_id = ?",
        (user_id,),
    )
    if row is None:
        return None

    return UserData(
        user_id=row[0],
        data=json.loads(row[1]) if row[1] else {},
        updated_at=datetime.fromisoformat(row[2]),
    )


async def set_user_data(
    db: "Database",
    user_id: int,
    data: dict[str, Any],
) -> None:
    """Store data for a user.

    Args:
        db: Database connection.
        user_id: ID of the user.
        data: Data to store (will be JSON-serialized).
    """
    await db.execute(
        """
        INSERT INTO user_data (user_id, data, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
        """,
        (user_id, json.dumps(data)),
    )
    await db.commit()
