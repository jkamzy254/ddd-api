"""
SQL Server access for the bot's 'Download' flow.

The Download action files a finished video into the database by calling the
stored procedure:

    EXEC spHSPVideoUpload @Name=?, @LinkID=?, @Category=?

Configuration comes from .env -- either a full ODBC connection string
(SQL_CONN_STR) or the individual pieces. Omit SQL_USERNAME/SQL_PASSWORD to use
Windows (trusted) auth.
"""

from __future__ import annotations

import os
import asyncio
from pathlib import Path
from django.db import connection

from dotenv import load_dotenv

# Load this project's .env (at the root, next to auth.py) regardless of the
# working directory -- e.g. when launched from a Django management command.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _exec_video_upload_proc(name: str, link_id: str, category: str) -> None:
    """Blocking pyodbc call -- run via run_video_upload_proc() off the loop.
    Executes:  EXEC spHSPVideoUpload @Name=?, @LinkID=?, @Category=?"""
    with connection.cursor() as cursor:
        cursor.execute("EXEC spHSPVideoUpload @Name=%s, @LinkID=%s, @Category=%s", [name, link_id, category],)
        return None


async def run_video_upload_proc(name: str, link_id: str, category: str) -> None:
    """Run the stored procedure without blocking the event loop."""
    await asyncio.to_thread(_exec_video_upload_proc, name, link_id, category)
