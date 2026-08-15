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

from utils.bot_db import build_conn_str

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


def _connect():
    import pyodbc  # lazy: the bot still runs without the DB feature
    return pyodbc.connect(build_conn_str(), timeout=10)


def fetch_policy(folder_id: str) -> Optional[FolderPolicy]:
    """Blocking read of one folder's policy row (latest row wins if LinkID
    was ever duplicated). Use get_policy() from async code."""
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT TOP 1 Name, Password FROM {TABLE} WHERE LinkID = ? ORDER BY ID DESC",
            folder_id,
        )
        row = cur.fetchone()
        if row is None:
            return None
        return FolderPolicy(folder_id=folder_id, name=row[0] or "", password=row[1] or None)
    finally:
        conn.close()


def upsert_policy(folder_id: str, name: str, password: Optional[str]) -> str:
    """Blocking insert-or-update by LinkID. Returns 'inserted' or 'updated'."""
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE {TABLE} SET Name = ?, Password = ? WHERE LinkID = ?",
            name, password, folder_id,
        )
        action = "updated"
        if cur.rowcount == 0:
            cur.execute(
                f"INSERT INTO {TABLE} (Name, LinkID, Password) VALUES (?, ?, ?)",
                name, folder_id, password,
            )
            action = "inserted"
        conn.commit()
        return action
    finally:
        conn.close()


def delete_policy(folder_id: str) -> int:
    """Blocking delete by LinkID. Returns rows removed."""
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {TABLE} WHERE LinkID = ?", folder_id)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def list_policies() -> list[FolderPolicy]:
    """Blocking read of every policy row."""
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT LinkID, Name, Password FROM {TABLE} ORDER BY Name")
        return [
            FolderPolicy(folder_id=r[0], name=r[1] or "", password=r[2] or None)
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


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
