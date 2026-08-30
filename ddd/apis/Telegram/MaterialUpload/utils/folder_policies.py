"""
Folder privacy policies, backed by the SQL Server table LividFolderTable.

The table (created outside this project):

    CREATE TABLE LividFolderTable (
        ID        INT IDENTITY(1,1) PRIMARY KEY,
        Name      VARCHAR(255),
        LinkID    VARCHAR(255),      -- the Livid folder id
        CreatedAt DATETIME2 NOT NULL DEFAULT CURRENT_TIMESTAMP,
        Password  VARCHAR(255)       -- NULL means 'unlisted'
    )

Convention (one row per Livid folder, keyed by LinkID):
    Password set   -> new videos in that folder become password-protected
                      with that password (embed on).
    Password NULL  -> new videos become 'unlisted' (embed on) -- the HSP /
                      MLT folders work this way.
    No row at all  -> no policy; a new upload keeps Livid's default (private).

Reads are cached for a few minutes so the bot doesn't hit SQL Server on
every upload; call invalidate_cache() after editing rows out-of-band.
Connection settings come from .env via bot_db.build_conn_str().
"""

from __future__ import annotations

import time
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from django.db import connection

log = logging.getLogger("livid_bot")

TABLE = "LividFolderTable"
CACHE_TTL_SECONDS = 300


@dataclass
class FolderPolicy:
    folder_id: str
    name: str
    password: Optional[str]  # None -> unlisted

    @property
    def privacy(self) -> str:
        return "password" if self.password else "unlisted"


# folder_id -> (fetched_at, FolderPolicy | None). None is cached too, so
# folders without a policy don't re-query SQL on every upload.
_cache: dict[str, tuple[float, Optional[FolderPolicy]]] = {}


def invalidate_cache() -> None:
    _cache.clear()


def fetch_policy(folder_id: str) -> Optional[FolderPolicy]:
    """Blocking read of one folder's policy row (latest row wins if LinkID
    was ever duplicated). Use get_policy() from async code."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT TOP 1 Name, Password FROM {TABLE} WHERE LinkID = ? ORDER BY ID DESC",
            folder_id,
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return FolderPolicy(folder_id=folder_id, name=row[0] or "", password=row[1] or None)


def upsert_policy(folder_id: str, name: str, password: Optional[str]) -> str:
    """Blocking insert-or-update by LinkID. Returns 'inserted' or 'updated'."""
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE %s SET Name = %s, Password = %s WHERE LinkID = %s", 
            [TABLE, name, password, folder_id]
        )
        action = "updated"
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO %s (Name, LinkID, Password) VALUES (%s, %s, %s)",
                [TABLE, name, folder_id, password]
            )
            action = "inserted"
        return action


def delete_policy(folder_id: str) -> int:
    """Blocking delete by LinkID. Returns rows removed."""
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {TABLE} WHERE LinkID = ?", folder_id)
        return cursor.rowcount


def list_policies() -> list[FolderPolicy]:
    """Blocking read of every policy row."""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT LinkID, Name, Password FROM {TABLE} ORDER BY Name")
        return [
            FolderPolicy(folder_id=r[0], name=r[1] or "", password=r[2] or None)
            for r in cursor.fetchall()
        ]


async def get_policy(folder_id: str) -> Optional[FolderPolicy]:
    """Async, cached policy lookup. Returns None (and logs) if SQL Server is
    unreachable, so a missing DB never breaks an upload."""
    hit = _cache.get(folder_id)
    if hit and time.monotonic() - hit[0] < CACHE_TTL_SECONDS:
        return hit[1]
    try:
        policy = await asyncio.to_thread(fetch_policy, folder_id)
    except Exception as exc:
        log.warning("folder policy lookup failed for %s: %s", folder_id, exc)
        return None
    _cache[folder_id] = (time.monotonic(), policy)
    return policy
