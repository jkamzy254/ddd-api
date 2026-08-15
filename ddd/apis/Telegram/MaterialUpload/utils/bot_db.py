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

from dotenv import load_dotenv

# Load this project's .env (at the root, next to auth.py) regardless of the
# working directory -- e.g. when launched from a Django management command.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def build_conn_str() -> str:
    # Read env at call time (not import time) so it's correct no matter when
    # .env was loaded relative to this module being imported.
    conn = os.environ.get("SQL_CONN_STR", "")
    if conn:
        return conn
    server = os.environ.get("SQL_SERVER", "")
    database = os.environ.get("SQL_DATABASE", "")
    if not (server and database):
        raise RuntimeError(
            "SQL not configured -- set SQL_CONN_STR, or SQL_SERVER + SQL_DATABASE "
            "(and SQL_USERNAME/SQL_PASSWORD unless using Windows auth) in .env"
        )
    driver = os.environ.get("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    username = os.environ.get("SQL_USERNAME", "")
    password = os.environ.get("SQL_PASSWORD", "")
    parts = [f"DRIVER={{{driver}}}", f"SERVER={server}", f"DATABASE={database}"]
    if username:
        parts += [f"UID={username}", f"PWD={password}"]
    else:
        parts.append("Trusted_Connection=yes")
    return ";".join(parts) + ";"


def _exec_video_upload_proc(name: str, link_id: str, category: str) -> None:
    """Blocking pyodbc call -- run via run_video_upload_proc() off the loop.
    Executes:  EXEC spHSPVideoUpload @Name=?, @LinkID=?, @Category=?"""
    import pyodbc  # imported lazily so the bot still runs without the DB feature
    conn = pyodbc.connect(build_conn_str(), timeout=10)
    try:
        cur = conn.cursor()
        cur.execute(
            "EXEC spHSPVideoUpload @Name=?, @LinkID=?, @Category=?",
            name, link_id, category,
        )
        conn.commit()
    finally:
        conn.close()


async def run_video_upload_proc(name: str, link_id: str, category: str) -> None:
    """Run the stored procedure without blocking the event loop."""
    await asyncio.to_thread(_exec_video_upload_proc, name, link_id, category)
