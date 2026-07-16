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
from django.db import connection



def _exec_video_upload_proc(name: str, link_id: str, category: str) -> None:
    with connection.cursor() as cursor:
        sql = "EXEC spHSPVideoUpload @Name=%s, @LinkID=%s, @Category=%s"
        cursor.execute(sql, [name,link_id,category,])
        recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
    return recs[0] if recs else None  # Safer
    

async def run_video_upload_proc(name: str, link_id: str, category: str) -> None:
    """Run the stored procedure without blocking the event loop."""
    await asyncio.to_thread(_exec_video_upload_proc, name, link_id, category)
