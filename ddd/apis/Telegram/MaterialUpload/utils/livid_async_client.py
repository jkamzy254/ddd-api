"""
Async Livid API client (httpx) used by the Telegram bot.

Reverse-engineered from HAR captures of the real web app (Livid_Log_1..4).
See livid_client.py for the full endpoint notes; this is the async twin the
bot drives. Auth is the `__Secure-livid.session_token` cookie -- pass its value
to the constructor (session_store.load_token() is the usual source).
"""

from __future__ import annotations

import html
import time
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

log = logging.getLogger("livid_bot")

API_BASE = "https://api.livid.com"
EMBED_BASE = "https://livid.com/embed"


class SessionExpiredError(RuntimeError):
    """Livid returned 401/403 -- the session token has expired or been revoked.
    Re-run auth.py to get a fresh one."""


def raise_for_status(resp: httpx.Response) -> None:
    """Like resp.raise_for_status(), but turns 401/403 into a clear
    SessionExpiredError so callers can prompt for re-login."""
    if resp.status_code in (401, 403):
        raise SessionExpiredError(f"Livid returned {resp.status_code} (session expired)")
    resp.raise_for_status()

# The appearance the account applied by hand in Livid_Log_2 and _3 -- reused as
# the automatic default for every upload.
DEFAULT_APPEARANCE = {
    "controlsAirplayEnabled": False,
    "controlsChromeCastEnabled": False,
    "controlsDefaultLogoEnabled": False,
    "controlsPIPEnabled": False,
    "controlsShareEnabled": False,
}


def _by_name(folders: list[dict]) -> list[dict]:
    """Case-insensitive A-Z sort. We also ask the API for ascending order, but
    its sort is case-sensitive (all uppercase names come before lowercase ones),
    so re-sort locally to get a listing that reads alphabetically."""
    return sorted(folders, key=lambda f: (f.get("name") or "").lower())


@dataclass
class VideoPreview:
    id: str
    title: str
    slug: str
    folder_id: Optional[str]
    is_encoded: bool

    @classmethod
    def from_json(cls, d: dict) -> "VideoPreview":
        asset = d.get("currentVideoAsset") or {}
        return cls(
            id=d["id"],
            title=d.get("title") or "(untitled)",
            slug=d["slug"],
            folder_id=d.get("folderId"),
            is_encoded=bool(asset.get("moderationStatus") or asset.get("length")),
        )


class AsyncLividClient:
    """Async Livid API client using httpx."""

    def __init__(self, session_token: str):
        self.client = httpx.AsyncClient(
            headers={
                "Origin": "https://livid.com",
                "Referer": "https://livid.com/",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36",
            },
            cookies={"__Secure-livid.session_token": session_token},
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self.client.aclose()

    # ---------- folders ----------

    async def list_folders(self) -> list[dict]:
        r = await self.client.get(f"{API_BASE}/v2/folders", params={"orderByField": "name", "orderByDirection": "asc"})
        raise_for_status(r)
        return _by_name(r.json()["childFolders"]["folders"])

    async def get_folder(self, folder_id: str) -> dict:
        """Returns {"folder": {...}, "childFolders": {"folders": [...]}}. The
        child folders are sorted A-Z here so every caller (get_folder and
        list_subfolders alike) gets the same alphabetical listing."""
        r = await self.client.get(f"{API_BASE}/v2/folders/{folder_id}", params={"orderByField": "name", "orderByDirection": "asc"})
        raise_for_status(r)
        data = r.json()
        child = data.get("childFolders") or {}
        if isinstance(child.get("folders"), list):
            child["folders"] = _by_name(child["folders"])
        return data

    async def list_subfolders(self, folder_id: str) -> list[dict]:
        data = await self.get_folder(folder_id)
        return data["childFolders"]["folders"]

    # ---------- videos: read ----------

    async def list_videos(self, folder_id: str) -> list[VideoPreview]:
        r = await self.client.get(f"{API_BASE}/v1/videos/previews", params={"folderId": folder_id, "orderByField": "title", "orderByDirection": "asc"})
        raise_for_status(r)
        videos = [VideoPreview.from_json(v) for v in r.json()["videoPreviews"]]
        return sorted(videos, key=lambda v: v.title.lower())

    async def find_video(self, folder_id: str, video_id: str) -> Optional[VideoPreview]:
        for v in await self.list_videos(folder_id):
            if v.id == video_id:
                return v
        return None

    async def get_video(self, video_id: str) -> dict:
        r = await self.client.get(f"{API_BASE}/v1/videos/id/{video_id}")
        raise_for_status(r)
        return r.json()

    # ---------- videos: metadata / privacy / appearance ----------

    async def update_video(self, video_id: str, **fields) -> dict:
        """PUT /v1/videos/id/{id} -- rename, privacy, password, embedEnabled."""
        r = await self.client.put(f"{API_BASE}/v1/videos/id/{video_id}", json=fields)
        raise_for_status(r)
        return r.json() if r.content else {}

    async def set_privacy(self, video_id: str, privacy: str, *, embed_enabled: Optional[bool] = None) -> dict:
        body = {"privacyPage": privacy}
        if embed_enabled is not None:
            body["embedEnabled"] = embed_enabled
        return await self.update_video(video_id, **body)

    async def set_password(self, video_id: str, password: str) -> dict:
        await self.set_privacy(video_id, "password")
        return await self.update_video(video_id, privacyPassword=password)

    async def update_appearance(self, video_id: str, **fields) -> dict:
        """PUT /v1/player-configurations/{id}. Resolves the config id from the
        video detail (video['playerConfiguration']['id'])."""
        detail = await self.get_video(video_id)
        pc_id = (detail.get("playerConfiguration") or {}).get("id")
        if not pc_id:
            raise RuntimeError(f"video {video_id} has no playerConfiguration.id")
        r = await self.client.put(f"{API_BASE}/v1/player-configurations/{pc_id}", json=fields)
        raise_for_status(r)
        return r.json() if r.content else {}

    # ---------- transcript ----------

    async def generate_transcript(self, video_id: str) -> dict:
        r = await self.client.post(f"{API_BASE}/v1/videos/id/{video_id}/generate-transcript")
        raise_for_status(r)
        return r.json() if r.content else {}

    # ---------- encode status (poll + SSE early-wake) ----------

    async def batch_status(self, video_ids: list[str]) -> dict:
        r = await self.client.post(f"{API_BASE}/v1/videos/batch-status", json={"videoIds": video_ids})
        raise_for_status(r)
        return r.json()

    async def _pump_stream_events(self, stream_url: str, wake: "asyncio.Event") -> None:
        """Listen to a Livid SSE stream forever, setting `wake` on every real
        push ('data:'/'event:' line). Keep-alive comment lines (': ...') are
        ignored. Reconnects on any hiccup. Cancel the task to stop it.

        This is only an *early-wake hint*: the caller still polls on a fixed
        cadence, so correctness never depends on the stream actually pushing --
        it just makes the caller react sooner when it does."""
        sse_timeout = httpx.Timeout(connect=15.0, read=120.0, write=15.0, pool=15.0)
        while True:
            try:
                async with self.client.stream(
                    "GET", stream_url,
                    headers={"Accept": "text/event-stream"}, timeout=sse_timeout,
                ) as r:
                    raise_for_status(r)
                    async for line in r.aiter_lines():
                        if line.startswith("data:") or line.startswith("event:"):
                            wake.set()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.debug("SSE %s hiccup (%s); reconnecting", stream_url, exc)
                await asyncio.sleep(3)

    async def _wait_until(self, check, stream_url: str, timeout_seconds: int, poll_seconds: int) -> dict:
        """Poll `check()` on a fixed cadence (the reliable backbone), but wake
        early whenever the SSE stream pushes an event. `check()` returns a
        truthy value to stop (returned here) or None to keep waiting."""
        got = await check()
        if got is not None:
            return got

        wake = asyncio.Event()
        pump = asyncio.create_task(self._pump_stream_events(stream_url, wake))
        try:
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                try:
                    await asyncio.wait_for(wake.wait(), timeout=poll_seconds)
                except asyncio.TimeoutError:
                    pass  # cadence tick -- check anyway
                wake.clear()
                got = await check()
                if got is not None:
                    return got
            raise TimeoutError(f"timed out waiting on {stream_url}")
        finally:
            pump.cancel()
            try:
                await pump
            except (asyncio.CancelledError, Exception):
                pass

    async def wait_for_encode(self, video_id: str, timeout_seconds: int = 7200, poll_seconds: int = 15) -> dict:
        """Wait until the video finishes transcoding. Polls batch-status every
        `poll_seconds` (guaranteed progress) and wakes early on updates-stream
        pushes. Returns the batch-status entry."""
        async def check():
            video = (await self.batch_status([video_id]))["videos"][0]
            if video.get("encodeStatus") == "FAILED":
                raise RuntimeError(f"encode failed for {video_id}")
            return video if video.get("isEncoded") else None

        url = f"{API_BASE}/v1/videos/id/{video_id}/updates-stream"
        return await self._wait_until(check, url, timeout_seconds, poll_seconds)


def build_embed_snippet(slug: str, title: str) -> str:
    """The full 'Share & Embed' block: responsive iframe + an 'Open in Full
    Screen' button, matching what Livid's share modal hands out."""
    embed_url = f"{EMBED_BASE}/{slug}"
    safe_title = html.escape(title, quote=True)
    return f'''<div style="padding:56.25% 0 0 0;position:relative;width:100%;"><iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture; web-share" allowfullscreen frameborder="0" referrerpolicy="strict-origin-when-cross-origin" src="{embed_url}" title="{safe_title}"></iframe></div>

<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; width: 100%;">

  <!-- THE COMPLEMENTARY FULLSCREEN BUTTON -->
  <div style="padding-top: 14px;">
    <a href="{embed_url}" target="_blank" style="display: inline-block; background-color: #111111; color: #ffffff; padding: 10px 20px; font-size: 14px; font-weight: 500; text-decoration: none; border-radius: 6px;">
      Open in Full Screen ↗
    </a>
  </div>

</div>'''
