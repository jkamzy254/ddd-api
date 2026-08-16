"""
Telegram bot for uploading/managing videos on Livid.

Two entry points, both ending on the same Embed / Database / Rename / Privacy
action menu:

    send a video  -- pick a target folder, upload it, then act on it
    /browse       -- walk the folder tree, list a folder's videos, pick one

This file is just the Telegram wiring -- menus, handlers, and the upload
orchestration. The pieces it builds on live in sibling modules:

    livid_async_client.py  -- the async Livid API client + constants
    bot_db.py              -- the SQL Server 'Download' stored-proc call
    session_store.py       -- loads (and decrypts) the Livid session token

Run it with:  python livid_telegram_bot.py
"""

import os
import sys
import html
import asyncio
import logging
from functools import wraps
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button

# Make this folder importable as a top-level location so the sibling modules
# below resolve whether the bot is run standalone (python livid_telegram_bot.py)
# or imported as part of another package (e.g. a Django management command).
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from utils import session_store
from utils.livid_async_client import (
    AsyncLividClient,
    SessionExpiredError,
    raise_for_status,
    DEFAULT_APPEARANCE,
    build_embed_snippet,
    API_BASE,
)
from utils.bot_db import run_video_upload_proc
from utils import folder_policies

# Load this project's .env regardless of the working directory (so the bot
# works when launched from a Django management command in another package).
load_dotenv(Path(__file__).with_name(".env"))
logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger("livid_bot")

# --- Configuration ---
API_ID = int(os.environ.get("TELEGRAM_API_ID", 0))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.environ.get("TELEGRAM_LIVID_BOT", "")

CATEGORIES = ["Friday Verse Session", "Main Lesson", "Others", "Podcast", "Speech Prep"]
PAGE_SIZE = 8  # folder/video buttons per page (Telegram caps inline keyboards)
VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".avi")

# --- Global State ---
# One session per user, keyed by Telegram user id. Two kinds share this dict:
#   mode="upload"  -- started by sending a video; carries the pending media.
#   mode="browse"  -- started by /browse; no media, just folder navigation.
# Once a video is selected (uploaded, or picked from a folder listing) both
# kinds carry video_id/slug/title and drive the same action menu.
user_sessions = {}
# The client is created inside build_bot()/main() (not at import time) so this
# module can be imported with no side effects and no credentials -- which is
# what lets main() be launched from a multiprocessing.Process like the other
# bots. Handlers reference this global; it's set before the bot starts.
bot: Optional[TelegramClient] = None


# ---------- session token / client ----------

def _load_session_token() -> str:
    """Session token from session.json (auth.py, possibly encrypted), falling
    back to a SESSION_TOKEN env var for convenience."""
    tok = session_store.load_token_or_none()
    if tok:
        return tok
    env = os.environ.get("SESSION_TOKEN", "")
    if env:
        return env
    raise session_store.SessionError(
        "No session token found. Run `python auth.py` to log in "
        "(or set SESSION_TOKEN in .env)."
    )


_client: Optional[AsyncLividClient] = None

SESSION_EXPIRED_MSG = (
    "🔑 Your Livid session has expired.\n"
    "Run `python utils/auth.py` to log in again — the bot will pick up the new "
    "session automatically (or send /reload to force it)."
)


def get_client() -> AsyncLividClient:
    global _client
    if _client is None:
        _client = AsyncLividClient(_load_session_token())
    return _client


def reset_client() -> None:
    """Drop the cached client so the next call reloads a fresh token from disk
    (used by /reload and the session.json watcher after re-running auth.py)."""
    global _client
    old, _client = _client, None
    if old is not None:
        # Close the old client's connections without blocking, if a loop is up.
        try:
            asyncio.get_running_loop().create_task(old.aclose())
        except RuntimeError:
            pass


async def _watch_session_file(poll_seconds: int = 5) -> None:
    """Auto-reload the client whenever session.json changes on disk (e.g. after
    a fresh `python auth.py`), so an expired token recovers without a restart."""
    path = session_store.SESSION_FILE

    def _mtime():
        try:
            return path.stat().st_mtime
        except OSError:
            return None

    last = _mtime()
    while True:
        await asyncio.sleep(poll_seconds)
        cur = _mtime()
        if cur is not None and cur != last:
            last = cur
            reset_client()
            log.info("session.json changed -- reloaded Livid session token.")


def _guard(handler):
    """Wrap a handler so an expired Livid session shows friendly re-login
    guidance instead of a raw error."""
    @wraps(handler)
    async def wrapper(event):
        try:
            return await handler(event)
        except SessionExpiredError:
            log.warning("Livid session expired during %s", handler.__name__)
            try:
                await event.respond(SESSION_EXPIRED_MSG)
            except Exception:
                pass
    return wrapper


# ---------- menus ----------

def _pagination_row(page: int, pages: int, prefix: str) -> Optional[list]:
    """A [⬅️ Prev] [n/N] [Next ➡️] row, or None if there's only one page.
    Prev/Next carry '{prefix}:{page}' callback data; the counter is a no-op."""
    if pages <= 1:
        return None
    row = []
    if page > 0:
        row.append(Button.inline("⬅️ Prev", data=f"{prefix}:{page - 1}".encode('utf-8')))
    row.append(Button.inline(f"{page + 1}/{pages}", data=b"noop"))
    if page < pages - 1:
        row.append(Button.inline("Next ➡️", data=f"{prefix}:{page + 1}".encode('utf-8')))
    return row


async def _folder_menu(
    folder_id: Optional[str], client: AsyncLividClient, page: int = 0,
    mode: str = "upload", detail: Optional[dict] = None,
) -> tuple[str, list]:
    """Folder listing, alphabetical. In upload mode the current folder offers
    '💾 Save here'; in browse mode it offers '📹 Videos (n)' instead.

    `detail` lets a caller that already fetched GET /v2/folders/{id} hand it in
    rather than making the same request a second time.
    """
    video_count = 0
    if folder_id is None:
        folders = await client.list_folders()
        header = ("📁 Choose a folder to upload into:" if mode == "upload"
                  else "📁 Browse folders:")
    else:
        detail = detail or await client.get_folder(folder_id)
        folders = detail["childFolders"]["folders"]
        video_count = detail["folder"]["_count"]["videos"]
        header = ("📁 Save here, or go into a subfolder:" if mode == "upload"
                  else f"📁 {detail['folder']['name']}")

    total = len(folders)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    start = page * PAGE_SIZE
    chunk = folders[start:start + PAGE_SIZE]

    rows = []
    if folder_id is not None:
        if mode == "upload":
            rows.append([Button.inline("💾 Save here", data=f"savehere:{folder_id}".encode('utf-8'))])
        elif video_count:
            # Only the page number rides in the data; the folder being listed is
            # always session['stack'][-1].
            rows.append([Button.inline(f"📹 Videos ({video_count})", data=b"bvideos:0")])

    for f in chunk:
        label = f["name"] + (f" ({f['_count']['videos']})" if f["_count"]["videos"] else "")
        rows.append([Button.inline(label, data=f"nav:{f['id']}".encode('utf-8'))])

    page_row = _pagination_row(page, pages, "page")
    if page_row:
        rows.append(page_row)

    if folder_id is not None:
        rows.append([Button.inline("⬅️ Back", data=b"back")])

    text = header
    if mode == "browse" and folder_id is not None and not folders and not video_count:
        text += "\n(this folder is empty)"
    if total > PAGE_SIZE:
        text += f"\n(folders {start + 1}-{start + len(chunk)} of {total})"
    return text, rows


def _browse_video_menu(session: dict, page: int = 0) -> tuple[str, list]:
    """Paginated listing of a folder's videos (browse mode). Reads the cached
    list from session['browse_videos'] so paging doesn't refetch."""
    videos = session.get("browse_videos", [])
    if not videos:
        return "This folder has no videos.", [[Button.inline("⬅️ Back", data=b"bfback")]]

    total = len(videos)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    session["browse_page"] = page
    start = page * PAGE_SIZE
    chunk = videos[start:start + PAGE_SIZE]

    rows = [[Button.inline(v.title[:60], data=f"bvid:{v.id}".encode('utf-8'))] for v in chunk]
    page_row = _pagination_row(page, pages, "bvpage")
    if page_row:
        rows.append(page_row)
    rows.append([Button.inline("⬅️ Back", data=b"bfback")])

    text = "🎬 Pick a video:"
    if total > PAGE_SIZE:
        text += f"\n(videos {start + 1}-{start + len(chunk)} of {total})"
    return text, rows


async def _show_browse_videos(event, session: dict, client: AsyncLividClient,
                              page: int = 0, refetch: bool = False) -> None:
    """Render the video list for whichever folder the user is currently in."""
    folder_id = session["stack"][-1] if session.get("stack") else None
    if folder_id is None:
        await event.edit("Open a folder first.")
        return
    # Fetch on entry, and whenever the cache belongs to a different folder.
    if refetch or session.get("browse_folder") != folder_id:
        session["browse_videos"] = await client.list_videos(folder_id)
        session["browse_folder"] = folder_id
    text, buttons = _browse_video_menu(session, page)
    await event.edit(text, buttons=buttons)


def _replace_menu(upload: dict, page: int = 0) -> tuple[str, list]:
    """Paginated 'which video should this replace?' list. Reads the cached
    video list from upload['replace_videos'] so paging doesn't refetch."""
    videos = upload.get("replace_videos", [])
    total = len(videos)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    upload["replace_page"] = page
    start = page * PAGE_SIZE
    chunk = videos[start:start + PAGE_SIZE]

    rows = [[Button.inline(v.title[:60], data=f"replacevideo:{v.id}".encode('utf-8'))] for v in chunk]
    page_row = _pagination_row(page, pages, "rvpage")
    if page_row:
        rows.append(page_row)

    text = "Which video should this replace?"
    if total > PAGE_SIZE:
        text += f"\n(videos {start + 1}-{start + len(chunk)} of {total})"
    return text, rows


def _action_buttons(session: Optional[dict] = None) -> list:
    """The Embed / Database / Rename / Privacy menu. Identical for an
    just-uploaded video and one picked out of a folder via /browse -- the only
    difference is that browse mode gets a route back to the video list."""
    rows = [
        [Button.inline("🔗 Embed", b"output:embed"), Button.inline("🗂 Database", b"output:download")],
        [Button.inline("✏️ Rename", b"act:rename"), Button.inline("🔒 Privacy", b"act:privacy")],
    ]
    if (session or {}).get("mode") == "browse":
        rows.append([Button.inline("⬅️ Videos", data=b"bvback"), Button.inline("✅ Done", b"act:done")])
    else:
        rows.append([Button.inline("✅ Done", b"act:done")])
    return rows


def _action_text(session: dict) -> str:
    title = session.get("title") or "this video"
    return f"🎬 {title}\n\nWhat would you like to do?"


async def _target_folder_chosen(event, folder_id: str, upload: dict) -> None:
    upload["target_folder_id"] = folder_id
    buttons = [
        [
            Button.inline("✅ Yes, replace one", b"isreplace:yes"),
            Button.inline("🆕 No, new video", b"isreplace:no"),
        ]
    ]
    await event.edit("Is this file replacing an existing video in this folder?", buttons=buttons)


# ---------- upload orchestration ----------

async def _run_upload(event, upload: dict, folder_id: Optional[str], version_of_video_id: Optional[str]) -> None:
    client = get_client()

    # Step 1: Register the upload.
    #  - New video:  POST /v1/videos with a folderId.
    #  - Replace:    POST /v1/videos/id/{id}/versions -- a dedicated endpoint,
    #                confirmed from Livid_Log_2.har.
    try:
        if folder_id:
            body = {
                "folderId": folder_id,  # <-- without this the video lands at the root
                "size": upload["size"],
                "title": upload["title"],
                "fileName": upload["file_name"],
                "contentType": upload["content_type"],
            }
            create_resp = await client.client.post(f"{API_BASE}/v1/videos", json=body)
        else:
            body = {
                "size": upload["size"],
                "fileName": upload["file_name"],
                "contentType": upload["content_type"],
            }
            create_resp = await client.client.post(
                f"{API_BASE}/v1/videos/id/{version_of_video_id}/versions", json=body
            )
        raise_for_status(create_resp)
        data = create_resp.json()
        resumable_uri = data["resumableUri"]
        video_id = data.get("videoId", version_of_video_id)
        video_asset_id = data["videoAssetId"]

        # Step 2: Stream straight from Telegram to GCS
        last_pct = -1

        async def progress_cb(pct: float):
            nonlocal last_pct
            rounded = int(pct // 5) * 5
            if rounded != last_pct:
                last_pct = rounded
                try:
                    await event.edit(f"⬆️ Streaming to Livid... {rounded}%")
                except Exception:
                    pass

        uploaded = 0
        # Bare httpx client for GCS so we don't send Livid's cookies to Google.
        async with httpx.AsyncClient(timeout=120.0) as gcs_client:
            async for chunk in bot.iter_download(upload["media"], chunk_size=16 * 1024 * 1024):
                chunk_len = len(chunk)
                start = uploaded
                end = uploaded + chunk_len - 1

                headers = {
                    "Content-Type": upload["content_type"],
                    "Content-Range": f"bytes {start}-{end}/{upload['size']}",
                }

                resp = await gcs_client.put(
                    resumable_uri,
                    content=bytes(chunk) if not isinstance(chunk, bytes) else chunk,
                    headers=headers,
                )

                if resp.status_code in (200, 201):
                    uploaded += chunk_len
                    await progress_cb(100.0)
                    break
                elif resp.status_code == 308:
                    uploaded += chunk_len
                    await progress_cb(100.0 * uploaded / upload["size"])
                else:
                    raise RuntimeError(f"GCS upload failed at byte {start}: {resp.status_code} {resp.text}")

        # Step 3: Complete upload
        complete_resp = await client.client.post(
            f"{API_BASE}/v1/videos/id/{video_id}/complete-upload",
            json={"videoAssetId": video_asset_id},
        )
        raise_for_status(complete_resp)

    except SessionExpiredError:
        log.warning("Livid session expired during upload")
        await event.edit(SESSION_EXPIRED_MSG)
        return
    except Exception as exc:
        log.exception("Upload failed")
        await event.edit(f"❌ Upload failed: {exc}")
        return

    # Post-upload routing. The slug (used for the embed URL) is assigned at
    # creation, so it's available immediately -- no need to wait for encoding.
    try:
        detail = await client.get_video(video_id)
        slug = detail.get("slug") or video_id
        title = detail.get("title") or upload["title"]
    except Exception:
        slug = upload.get("replace_target_slug") or video_id
        title = upload.get("replace_target_title") or upload["title"]

    upload["video_id"] = video_id
    upload["slug"] = slug
    upload["title"] = title

    # Kick off automatic post-processing (wait for transcoding, then apply the
    # default appearance, the folder's privacy policy, and queue a transcript)
    # so the menu shows immediately. Folder policies only apply to NEW uploads;
    # a replacement keeps whatever privacy the video already had.
    asyncio.create_task(_auto_post_process(
        event.sender_id, video_id, title,
        folder_id=upload.get("target_folder_id"),
        is_new=folder_id is not None,
    ))

    await event.edit(
        "✅ Upload complete!\n"
        "⏳ Appearance + transcript will be applied automatically once "
        "transcoding finishes.\n\n"
        "Meanwhile, what would you like to do?",
        buttons=_action_buttons(upload),
    )


async def _ensure_embeddable(client: AsyncLividClient, video_id: str) -> tuple[str, str]:
    """Make sure the video can actually be viewed via its embed link, then
    return (slug, title). A brand-new video defaults to 'private', whose embed
    won't play for anyone else -- so bump it to 'unlisted' and enable embedding
    (exactly what the web app's share flow relies on; see Livid_Log_4)."""
    detail = await client.get_video(video_id)
    updates = {}
    if not detail.get("embedEnabled"):
        updates["embedEnabled"] = True
    if detail.get("privacyPage") == "private":
        updates["privacyPage"] = "unlisted"
    if updates:
        await client.update_video(video_id, **updates)
    return detail.get("slug") or video_id, detail.get("title") or ""


async def _auto_post_process(
    user_id: int, video_id: str, title: str,
    folder_id: Optional[str] = None, is_new: bool = True,
) -> None:
    """Runs after upload: wait for transcoding, then apply the default
    appearance, the folder's privacy policy (LividFolderTable), and queue a
    transcript. Reports progress in its own message."""
    client = get_client()
    try:
        status_msg = await bot.send_message(
            user_id,
            f"⏳ '{title}' is transcoding. Appearance + transcript will run "
            f"automatically when it's done...",
        )
    except Exception:
        status_msg = None

    async def _say(text: str) -> None:
        try:
            if status_msg:
                await status_msg.edit(text)
            else:
                await bot.send_message(user_id, text)
        except Exception:
            pass

    encode_ok = True
    try:
        await client.wait_for_encode(video_id)
    except Exception:
        encode_ok = False
        log.exception("wait_for_encode failed")

    lines = ["✅ Transcoding done." if encode_ok
             else "⚠️ Couldn't confirm transcoding finished; applying what I can."]

    # Appearance doesn't depend on transcoding, so apply it either way.
    try:
        await client.update_appearance(video_id, **DEFAULT_APPEARANCE)
        lines.append("🎨 Default appearance applied.")
    except Exception as exc:
        log.exception("auto appearance failed")
        lines.append(f"⚠️ Appearance failed: {exc}")

    # Folder privacy policy (LividFolderTable): Password set -> inherit it;
    # row with NULL password -> unlisted; no row -> leave Livid's default.
    # Only new uploads inherit -- replacements keep their existing privacy.
    if is_new and folder_id:
        try:
            policy = await folder_policies.get_policy(folder_id)
            if policy is None:
                pass  # no policy for this folder (or SQL unreachable -- logged)
            elif policy.password:
                # Same two-step PUT the web app does: mode first, then password.
                await client.update_video(video_id, privacyPage="password", embedEnabled=True)
                await client.update_video(video_id, privacyPassword=policy.password)
                lines.append(f"🔑 Folder policy: password-protected ('{policy.name}').")
            else:
                await client.set_privacy(video_id, "unlisted", embed_enabled=True)
                lines.append(f"🔗 Folder policy: unlisted ('{policy.name}').")
        except Exception as exc:
            log.exception("folder policy failed")
            lines.append(f"⚠️ Folder policy failed: {exc}")

    # A transcript needs the encoded media, so only queue it once encoding is
    # confirmed done.
    if encode_ok:
        try:
            await client.generate_transcript(video_id)
            lines.append("📝 Transcript queued (available shortly).")
        except Exception as exc:
            log.exception("auto transcript failed")
            lines.append(f"⚠️ Transcript request failed: {exc}")
    else:
        lines.append("⏭️ Transcript skipped — transcoding not confirmed.")

    await _say("\n".join(lines))


# ---------- handlers ----------

async def start(event):
    await event.respond(
        "Send me a video file and I'll stream it straight to Livid without "
        "downloading it locally.\n\n"
        "/browse — open the folder tree to find an existing video and grab its "
        "embed code, save it to the database, rename it, or change its privacy.\n"
        "/reload — re-read the Livid session token after running auth.py."
    )


@_guard
async def browse(event):
    """Browse existing videos without uploading anything: walk the folder tree,
    list a folder's videos, pick one, and use the same action menu an upload
    ends on."""
    try:
        client = get_client()
    except Exception as exc:
        await event.reply(f"⚠️ {exc}")
        return
    user_sessions[event.sender_id] = {"mode": "browse", "stack": []}
    status = await event.reply("🔄 Fetching folders...")
    text, buttons = await _folder_menu(None, client, mode="browse")
    await status.edit(text, buttons=buttons)


async def reload_session(event):
    """Re-read the session token from session.json without restarting the bot
    (use after re-running auth.py once the old token has expired)."""
    reset_client()
    try:
        get_client()
        await event.respond("🔄 Reloaded the Livid session token from session.json.")
    except Exception as exc:
        await event.respond(f"⚠️ Couldn't load session token: {exc}")


@_guard
async def handle_incoming_file(event):
    message = event.message

    if not message.file:
        return

    # Validate against the *real* file, so a captioned non-video is still rejected.
    actual_name = message.file.name or f"video_{message.id}.mp4"
    if message.document and not actual_name.lower().endswith(VIDEO_EXTS):
        await event.reply("That doesn't look like a video file.")
        return

    # Pick the title/name: prefer a caption typed on the message (so you can
    # name a video just by captioning it), then the real file name, then a
    # generic fallback. Videos sent via Telegram usually carry no file name.
    caption = (message.message or "").strip().replace("/", "-").replace("\\", "-")
    if caption:
        title = Path(caption).stem if caption.lower().endswith(VIDEO_EXTS) else caption
    elif message.file.name:
        title = Path(message.file.name).stem
    else:
        title = Path(actual_name).stem

    ext = Path(actual_name).suffix or ".mp4"
    file_name = f"{title}{ext}"

    user_sessions[event.sender_id] = {
        "mode": "upload",
        "media": message.media,
        "size": message.file.size,
        "content_type": message.file.mime_type or "video/mp4",
        "file_name": file_name,
        "title": title,
        "stack": [],
    }

    try:
        client = get_client()
    except Exception as exc:
        await event.reply(f"⚠️ {exc}")
        return
    status = await event.reply("🔄 Fetching folders...")
    text, buttons = await _folder_menu(None, client)
    await status.edit(text, buttons=buttons)


@_guard
async def handle_text_input(event):
    """Captures the free-text replies for the Rename / Password flows."""
    user_id = event.sender_id
    session = user_sessions.get(user_id)
    if not session or not session.get("awaiting") or not session.get("video_id"):
        return  # not waiting on anything -- ignore

    awaiting = session.pop("awaiting")
    text = event.raw_text.strip()
    client = get_client()
    video_id = session["video_id"]

    try:
        if awaiting == "rename":
            await client.update_video(video_id, title=text)
            session["title"] = text
            # Keep the cached browse listing in step with the new title.
            for v in session.get("browse_videos", []):
                if v.id == video_id:
                    v.title = text
                    break
            await event.reply(f"✏️ Renamed to: {text}", buttons=_action_buttons(session))
        elif awaiting == "password":
            await client.set_password(video_id, text)
            await event.reply(
                "🔑 Password set — the video is now password-protected.",
                buttons=_action_buttons(session),
            )
    except Exception as exc:
        log.exception("%s failed", awaiting)
        await event.reply(f"⚠️ Couldn't apply {awaiting}: {exc}", buttons=_action_buttons(session))


@_guard
async def folder_callback(event):
    # Answer the callback IMMEDIATELY to prevent expiration
    await event.answer()

    user_id = event.sender_id
    if user_id not in user_sessions:
        await event.answer(
            "No active session. Send a video to upload, or /browse existing ones.",
            alert=True,
        )
        return

    upload = user_sessions[user_id]
    mode = upload.get("mode", "upload")
    data = event.data.decode('utf-8')
    client = get_client()

    if data == "noop":
        return  # page counter button -- already answered above

    elif data.startswith("nav:"):
        folder_id = data.split(":", 1)[1]
        detail = await client.get_folder(folder_id)
        counts = detail["folder"]["_count"]
        upload["stack"].append(folder_id)
        upload["folder_page"] = 0  # entering a new level starts at page 1

        if mode == "browse":
            # A leaf folder that holds videos goes straight to the listing --
            # its folder menu would only be the Videos button and Back.
            if counts["childFolders"] == 0 and counts["videos"]:
                await _show_browse_videos(event, upload, client, refetch=True)
            else:
                text, buttons = await _folder_menu(folder_id, client, mode=mode, detail=detail)
                await event.edit(text, buttons=buttons)
        elif counts["childFolders"] == 0:
            await _target_folder_chosen(event, folder_id, upload)
        else:
            text, buttons = await _folder_menu(folder_id, client, mode=mode, detail=detail)
            await event.edit(text, buttons=buttons)

    elif data == "back":
        if upload["stack"]:
            upload["stack"].pop()
        upload["folder_page"] = 0
        parent = upload["stack"][-1] if upload["stack"] else None
        text, buttons = await _folder_menu(parent, client, mode=mode)
        await event.edit(text, buttons=buttons)

    elif data.startswith("page:"):
        page = int(data.split(":", 1)[1])
        upload["folder_page"] = page
        current = upload["stack"][-1] if upload["stack"] else None
        text, buttons = await _folder_menu(current, client, page=page, mode=mode)
        await event.edit(text, buttons=buttons)

    # ----- browse mode: folder -> video list -> action menu -----

    elif data.startswith("bvideos:"):
        page = int(data.split(":", 1)[1])
        await _show_browse_videos(event, upload, client, page=page, refetch=True)

    elif data.startswith("bvpage:"):
        page = int(data.split(":", 1)[1])
        await _show_browse_videos(event, upload, client, page=page)

    elif data == "bvback":
        # Action menu -> back to the video list we came from.
        await _show_browse_videos(event, upload, client, page=upload.get("browse_page", 0))

    elif data == "bfback":
        # Video list -> back to the folder menu (without leaving the folder).
        current = upload["stack"][-1] if upload["stack"] else None
        text, buttons = await _folder_menu(
            current, client, page=upload.get("folder_page", 0), mode=mode
        )
        await event.edit(text, buttons=buttons)

    elif data.startswith("bvid:"):
        video_id = data.split(":", 1)[1]
        video = next((v for v in upload.get("browse_videos", []) if v.id == video_id), None)
        upload["video_id"] = video_id
        upload["slug"] = video.slug if video else video_id
        upload["title"] = video.title if video else "(unknown)"
        await event.edit(_action_text(upload), buttons=_action_buttons(upload))

    elif data.startswith("savehere:"):
        folder_id = data.split(":", 1)[1]
        await _target_folder_chosen(event, folder_id, upload)

    elif data.startswith("isreplace:"):
        choice = data.split(":", 1)[1]
        folder_id = upload["target_folder_id"]

        if choice == "no":
            await event.edit("⬆️ Starting upload...")
            await _run_upload(event, upload, folder_id=folder_id, version_of_video_id=None)
        else:
            videos = await client.list_videos(folder_id)
            if not videos:
                await event.edit("No videos in this folder yet -- uploading as new.")
                await _run_upload(event, upload, folder_id=folder_id, version_of_video_id=None)
                return

            upload["replace_videos"] = videos  # cache for paging + lookup
            text, buttons = _replace_menu(upload, page=0)
            await event.edit(text, buttons=buttons)

    elif data.startswith("rvpage:"):
        page = int(data.split(":", 1)[1])
        text, buttons = _replace_menu(upload, page=page)
        await event.edit(text, buttons=buttons)

    elif data.startswith("replacevideo:"):
        video_id = data.split(":", 1)[1]
        video = next((v for v in upload.get("replace_videos", []) if v.id == video_id), None)
        if video is None:
            video = await client.find_video(upload["target_folder_id"], video_id)

        upload["replace_target_slug"] = video.slug if video else video_id
        upload["replace_target_title"] = video.title if video else upload["title"]

        await event.edit(f"⬆️ Streaming as a new version of '{upload['replace_target_title']}'...")
        await _run_upload(event, upload, folder_id=None, version_of_video_id=video_id)

    elif data == "output:embed":
        # Make sure the link actually plays for others, then hand back the
        # full embed snippet (iframe + Open in Full Screen button).
        try:
            slug, fresh_title = await _ensure_embeddable(client, upload["video_id"])
            upload["slug"] = slug or upload["slug"]
            if fresh_title:
                upload["title"] = fresh_title
        except Exception as exc:
            log.exception("ensure_embeddable failed")
            await event.respond(f"⚠️ Couldn't confirm embed settings ({exc}); giving you the code anyway.")
        snippet = build_embed_snippet(upload["slug"], upload["title"])
        await event.respond(f"<pre>{html.escape(snippet)}</pre>", parse_mode='html')

    elif data == "output:download":
        rows = [[Button.inline(c, f"dbcat:{i}".encode('utf-8'))] for i, c in enumerate(CATEGORIES)]
        rows.append([Button.inline("⬅️ Back", b"act:menu")])
        await event.edit("📥 Save to the database under which category?", buttons=rows)

    elif data.startswith("dbcat:"):
        idx = int(data.split(":", 1)[1])
        category = CATEGORIES[idx]
        # @Name = the (possibly renamed) title; @LinkID = the slug. Pull them
        # fresh from Livid so the DB matches the current state, falling back to
        # what we already have if that lookup fails.
        try:
            detail = await client.get_video(upload["video_id"])
            name = detail.get("title") or upload["title"]
            link_id = detail.get("slug") or upload["slug"]
        except Exception:
            name, link_id = upload["title"], upload["slug"]

        await event.edit(f"💾 Saving '{name}' to the database under '{category}'...")
        try:
            await run_video_upload_proc(name, link_id, category)
            await event.edit(
                "✅ Saved to the database:\n"
                f"• Name: {name}\n• LinkID: {link_id}\n• Category: {category}",
                buttons=_action_buttons(upload),
            )
        except Exception as exc:
            log.exception("spHSPVideoUpload failed")
            await event.edit(f"⚠️ Database save failed: {exc}", buttons=_action_buttons(upload))

    elif data == "act:menu":
        await event.edit(_action_text(upload), buttons=_action_buttons(upload))

    elif data == "act:rename":
        upload["awaiting"] = "rename"
        await event.edit(
            f"✏️ Send me the new title for '{upload['title']}' as a message.",
            buttons=[[Button.inline("⬅️ Cancel", b"act:menu")]],
        )

    elif data == "act:privacy":
        rows = [
            [Button.inline("🌍 Public", b"priv:public"), Button.inline("🔗 Unlisted", b"priv:unlisted")],
            [Button.inline("🔒 Private", b"priv:private"), Button.inline("🔑 Password", b"priv:password")],
            [Button.inline("⬅️ Back", b"act:menu")],
        ]
        await event.edit("Choose visibility:", buttons=rows)

    elif data in ("priv:public", "priv:unlisted", "priv:private"):
        level = data.split(":", 1)[1]
        try:
            # Enable embedding when making it publicly reachable (matches the
            # web app: public was sent together with embedEnabled=true).
            embed = True if level in ("public", "unlisted") else None
            await client.set_privacy(upload["video_id"], level, embed_enabled=embed)
            await event.edit(f"🔒 Visibility set to '{level}'.", buttons=_action_buttons(upload))
        except Exception as exc:
            log.exception("set_privacy failed")
            await event.edit(f"⚠️ Couldn't set privacy: {exc}", buttons=_action_buttons(upload))

    elif data == "priv:password":
        upload["awaiting"] = "password"
        await event.edit(
            "🔑 Send me the password to protect this video with.",
            buttons=[[Button.inline("⬅️ Cancel", b"act:menu")]],
        )

    elif data == "act:done":
        await event.edit(f"✅ All set — '{upload['title']}' is ready.")
        del user_sessions[user_id]


# ---------- startup ----------

def build_bot() -> TelegramClient:
    """Create the Telethon client and register all handlers. Called from main()
    so importing this module has no side effects."""
    global bot
    # Keep the Telethon .session file in the auth/ folder (alongside
    # session.json), absolute so it's independent of the working directory.
    session_store.AUTH_DIR.mkdir(parents=True, exist_ok=True)
    session_path = str(session_store.AUTH_DIR / "livid_bot_session")
    bot = TelegramClient(session_path, API_ID, API_HASH)

    bot.add_event_handler(start, events.NewMessage(pattern='/start'))
    bot.add_event_handler(browse, events.NewMessage(pattern='/browse'))
    bot.add_event_handler(reload_session, events.NewMessage(pattern='/reload'))
    bot.add_event_handler(handle_incoming_file, events.NewMessage(func=lambda e: e.video or e.document))
    bot.add_event_handler(handle_text_input, events.NewMessage(
        func=lambda e: bool(e.raw_text) and not e.raw_text.startswith('/') and not (e.video or e.document)))
    bot.add_event_handler(folder_callback, events.CallbackQuery())
    return bot


def main() -> None:
    """Entry point for the Livid Telegram bot. Blocks until disconnected.

    Safe to launch from a multiprocessing.Process(target=main) alongside other
    bots (e.g. python-telegram-bot ones) -- each process gets its own event
    loop, so the two frameworks never share one.
    """
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        log.error("Missing Telegram config! Set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_LIVID_BOT in .env.")
        return

    try:
        _load_session_token()  # fail fast with a clear message if it's missing
    except session_store.SessionError as exc:
        log.error("%s", exc)
        return

    # Give this process its own event loop (important when started via
    # multiprocessing and on Python versions where get_event_loop() is strict).
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = build_bot()
    log.info("Starting Telethon Livid bot...")
    client.start(bot_token=BOT_TOKEN)
    # Auto-reload the session token whenever session.json changes on disk.
    client.loop.create_task(_watch_session_file())
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
