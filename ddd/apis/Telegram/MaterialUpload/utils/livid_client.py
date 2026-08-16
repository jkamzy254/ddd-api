"""
Unofficial Livid.com API client.

Reverse-engineered from HAR captures of the real web app (Livid_Log_1/2/3).
Livid has no public API -- this replicates the private one their frontend
uses. Standard caveats apply: it's not supported, it can break without notice
whenever they ship a frontend change, and depending on their terms of service
this may or may not be something they're happy about. Use on your own account,
at your own risk, and don't hammer it.

Everything below was observed as a real request/response pair in the captures.

AUTH
  Just the `__Secure-livid.session_token` cookie. No CSRF token, no bearer
  token anywhere in the traffic. That cookie is httpOnly, so grab it once via
  auth.py (Playwright login) or DevTools -> Application -> Cookies. When calls
  start returning 401/403, log in again for a fresh value.

FOLDERS
  GET  /v2/folders                          -> top-level folders
  GET  /v2/folders/{id}                     -> a folder's info + child folders
  POST /v2/folders/video-counts  {ids:[..]} -> {folderId: videoCount}

VIDEOS (read)
  GET  /v1/videos/previews?folderId={id}    -> videos in a folder (has "slug")
  GET  /v1/videos/id/{id}                   -> full video detail. Includes
                                               title, slug, privacyPage,
                                               privacyPassword, embedEnabled,
                                               currentVideoAsset, versions[],
                                               and playerConfiguration.id
                                               (needed to change appearance).

UPLOAD a brand-new video (Livid_Log_1)
  1. POST /v1/videos  {folderId, size, title, fileName, contentType}
        -> {resumableUri, videoId, videoAssetId, signedUploadUrl}
  2. PUT  <resumableUri>                     -> file bytes, GCS resumable chunks
  3. POST /v1/videos/id/{videoId}/complete-upload  {videoAssetId}
        -> {videoEncodeId}   (kicks off transcoding)

REPLACE a video with a new file / new version (Livid_Log_2)  <-- CORRECTED
  This is NOT `POST /v1/videos` with a versionOfVideoId field (that was an
  earlier guess and is wrong). It's a dedicated endpoint:
  1. POST /v1/videos/id/{videoId}/versions  {size, fileName, contentType}
        -> {videoAssetId, resumableUri, videoId, signedUploadUrl}
  2. PUT  <resumableUri>                     -> file bytes (same GCS protocol)
  3. POST /v1/videos/id/{videoId}/complete-upload  {videoAssetId}
        -> {videoEncodeId}
  The video keeps its id, slug, and embed URL -- only the underlying asset
  changes -- which is exactly what you want for "replace".

RENAME / PRIVACY / PASSWORD  -- all via one endpoint (Livid_Log_2 & _3)
  PUT /v1/videos/id/{id}   with a partial body, e.g.:
     {"title": "New title"}                       -> rename
     {"privacyPage": "public", "embedEnabled": true}
     {"privacyPage": "unlisted"}
     {"privacyPage": "private"}
     {"privacyPage": "password"}                   -> then set the password:
     {"privacyPassword": "hunter2"}
  privacyPage is one of: private | public | unlisted | password.
  Response is {"message": "success"}.

APPEARANCE / player controls & colors (Livid_Log_2 & _3)
  PUT /v1/player-configurations/{playerConfigId}   with any subset of fields.
  Get {playerConfigId} from video detail: video["playerConfiguration"]["id"].
  Fields (null = "inherit default"):
     controlsAirplayEnabled, controlsCaptionsEnabled, controlsChromeCastEnabled,
     controlsDefaultLogoEnabled, controlsFullScreenEnabled, controlsPIPEnabled,
     controlsPlaybackSpeedEnabled, controlsPlayButtonPosition, controlsQualityEnabled,
     controlsShareEnabled, controlsTimeRangeEnabled, controlsVolumeEnabled,
     colorsAccent, colorsBackground, colorsPrimary, colorsText,
     customLogo*, detailsTitleEnabled

TRANSCRIPT (Livid_Log_2)
  POST /v1/videos/id/{id}/generate-transcript   -> {message, jobId}
  GET  /v1/videos/id/{id}/transcript-status     -> poll for completion
  GET  /v1/videos/id/{id}/transcripts           -> the finished transcript(s)
  GET  /v1/videos/id/{id}/transcript-segments?language=unknown

ENCODE STATUS
  POST /v1/videos/batch-status  {videoIds:[..]}
        -> {videos:[{id, encodeStatus, isEncoded, thumbnailReady, ...}]}
"""

from __future__ import annotations

import html
import mimetypes
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import requests

API_BASE = "https://api.livid.com"
EMBED_BASE = "https://livid.com/embed"

# GCS resumable uploads require chunk sizes that are a multiple of 256 KiB,
# except for the final chunk. 16 MiB matches what the web app used.
CHUNK_SIZE = 16 * 1024 * 1024
assert CHUNK_SIZE % (256 * 1024) == 0

ProgressCallback = Callable[[float], None]  # receives percent complete, 0-100

PRIVACY_VALUES = ("private", "public", "unlisted", "password")


@dataclass
class VideoPreview:
    """A single item from GET /v1/videos/previews."""
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
            is_encoded=bool(asset.get("isEncoded")),
        )


class LividError(RuntimeError):
    pass


class LividClient:
    def __init__(self, session_token: str):
        if not session_token:
            raise ValueError("session_token is required (see auth.py / README)")
        self.session = requests.Session()
        # __Secure- prefixed cookies require HTTPS, which requests uses for
        # these URLs by default, so this is fine.
        self.session.cookies.set(
            "__Secure-livid.session_token",
            session_token,
            domain=".livid.com",
            path="/",
        )
        self.session.headers.update(
            {
                "Origin": "https://livid.com",
                "Referer": "https://livid.com/",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/150.0.0.0 Safari/537.36"
                ),
            }
        )

    # ---------- low-level helpers ----------

    def _get(self, path: str, **params) -> dict:
        r = self.session.get(f"{API_BASE}{path}", params=params or None)
        self._raise(r)
        return r.json()

    def _put(self, path: str, body: dict) -> dict:
        r = self.session.put(f"{API_BASE}{path}", json=body)
        self._raise(r)
        return r.json() if r.content else {}

    def _post(self, path: str, body: Optional[dict] = None) -> dict:
        r = self.session.post(f"{API_BASE}{path}", json=body)
        self._raise(r)
        return r.json() if r.content else {}

    @staticmethod
    def _raise(r: requests.Response) -> None:
        if r.status_code == 401 or r.status_code == 403:
            raise LividError(
                f"{r.status_code} unauthorized -- your session_token has "
                f"probably expired. Re-run auth.py for a fresh one."
            )
        if not r.ok:
            raise LividError(f"{r.request.method} {r.url} -> {r.status_code}: {r.text[:300]}")

    # ---------- folders ----------

    def list_folders(self, order_field: str = "createdAt", order_dir: str = "desc") -> list[dict]:
        """Top-level folders."""
        data = self._get(
            "/v2/folders", orderByField=order_field, orderByDirection=order_dir
        )
        return data["childFolders"]["folders"]

    def get_folder(self, folder_id: str, order_field: str = "createdAt", order_dir: str = "desc") -> dict:
        """{"folder": {...}, "childFolders": {"folders": [...]}}. folder._count
        has childFolders / videos, useful to decide if it's a leaf folder."""
        return self._get(
            f"/v2/folders/{folder_id}", orderByField=order_field, orderByDirection=order_dir
        )

    def list_subfolders(self, folder_id: str, **kw) -> list[dict]:
        return self.get_folder(folder_id, **kw)["childFolders"]["folders"]

    def folder_video_counts(self, folder_ids: list[str]) -> dict:
        """POST /v2/folders/video-counts -> {folderId: count}."""
        return self._post("/v2/folders/video-counts", {"ids": folder_ids})

    def find_folder_id(self, name: str, folders: Optional[list[dict]] = None) -> Optional[str]:
        """Depth-first search the folder tree for a folder by exact name."""
        if folders is None:
            folders = self.list_folders()
        for f in folders:
            if f["name"] == name:
                return f["id"]
            if f.get("_count", {}).get("childFolders"):
                found = self.find_folder_id(name, self.list_subfolders(f["id"]))
                if found:
                    return found
        return None

    def print_folder_tree(self, folder_id: Optional[str] = None, indent: int = 0) -> None:
        folders = self.list_folders() if folder_id is None else self.list_subfolders(folder_id)
        for f in folders:
            c = f.get("_count", {})
            print("  " * indent + f"- {f['name']}  [{f['id']}]  "
                  f"({c.get('videos', 0)} videos, {c.get('childFolders', 0)} subfolders)")
            if c.get("childFolders"):
                self.print_folder_tree(f["id"], indent + 1)

    # ---------- videos: read ----------

    def list_videos(self, folder_id: str, order_field: str = "createdAt", order_dir: str = "desc") -> list[VideoPreview]:
        """GET /v1/videos/previews?folderId=... -> videos inside a folder."""
        data = self._get(
            "/v1/videos/previews",
            folderId=folder_id, orderByField=order_field, orderByDirection=order_dir,
        )
        return [VideoPreview.from_json(v) for v in data["videoPreviews"]]

    def get_video(self, video_id: str) -> dict:
        """Full video detail. Includes playerConfiguration.id, privacyPage,
        privacyPassword, embedEnabled, title, slug, currentVideoAsset, etc."""
        return self._get(f"/v1/videos/id/{video_id}")

    def find_video(self, folder_id: str, video_id: str) -> Optional[VideoPreview]:
        for v in self.list_videos(folder_id):
            if v.id == video_id:
                return v
        return None

    # ---------- videos: rename / privacy / password ----------

    def update_video(self, video_id: str, **fields) -> dict:
        """PUT /v1/videos/id/{id} with an arbitrary partial body. The typed
        helpers below are thin wrappers over this."""
        if not fields:
            raise ValueError("nothing to update")
        return self._put(f"/v1/videos/id/{video_id}", fields)

    def rename_video(self, video_id: str, title: str) -> dict:
        return self.update_video(video_id, title=title)

    def set_privacy(self, video_id: str, privacy: str, *, embed_enabled: Optional[bool] = None) -> dict:
        """privacy: private | public | unlisted | password. For 'password',
        follow up with set_password(). Livid_Log_2 sent embedEnabled=true
        together with privacyPage='public'."""
        if privacy not in PRIVACY_VALUES:
            raise ValueError(f"privacy must be one of {PRIVACY_VALUES}")
        body = {"privacyPage": privacy}
        if embed_enabled is not None:
            body["embedEnabled"] = embed_enabled
        return self.update_video(video_id, **body)

    def set_password(self, video_id: str, password: str) -> dict:
        """Set the password on a video. Web app first PUTs privacyPage='password'
        (see set_privacy) and then PUTs privacyPassword separately. This helper
        does both so the video is actually password-protected."""
        self.set_privacy(video_id, "password")
        return self.update_video(video_id, privacyPassword=password)

    def set_embed_enabled(self, video_id: str, enabled: bool) -> dict:
        return self.update_video(video_id, embedEnabled=enabled)

    # ---------- videos: appearance (player configuration) ----------

    def get_player_config(self, player_config_id: str) -> dict:
        return self._get(f"/v1/player-configurations/{player_config_id}")

    def update_appearance(self, video_id: str, **fields) -> dict:
        """Change how the player looks/behaves for a video. Resolves the
        video's playerConfiguration.id automatically, then PUTs the given
        fields. See module docstring for the full field list, e.g.:

            client.update_appearance(vid,
                controlsShareEnabled=False,
                controlsPIPEnabled=False,
                colorsAccent="#ff0000")
        """
        if not fields:
            raise ValueError("nothing to update")
        pc = self.get_video(video_id).get("playerConfiguration") or {}
        pc_id = pc.get("id")
        if not pc_id:
            raise LividError(f"video {video_id} has no playerConfiguration.id")
        return self._put(f"/v1/player-configurations/{pc_id}", fields)

    # ---------- videos: transcript ----------

    def generate_transcript(self, video_id: str) -> dict:
        """Queue transcript generation. Returns {message, jobId}. Poll with
        wait_for_transcript() or transcript_status()."""
        return self._post(f"/v1/videos/id/{video_id}/generate-transcript")

    def transcript_status(self, video_id: str) -> dict:
        return self._get(f"/v1/videos/id/{video_id}/transcript-status")

    def get_transcripts(self, video_id: str) -> dict:
        return self._get(f"/v1/videos/id/{video_id}/transcripts")

    def get_transcript_segments(self, video_id: str, language: str = "unknown") -> dict:
        return self._get(f"/v1/videos/id/{video_id}/transcript-segments", language=language)

    def wait_for_transcript(self, video_id: str, poll_seconds: int = 10, timeout_seconds: int = 1800) -> dict:
        """Generate (if needed) then poll transcript-status until it's ready."""
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            status = self.transcript_status(video_id)
            state = str(status.get("status") or status.get("state") or "").upper()
            if state in ("COMPLETED", "READY", "DONE", "SUCCESS"):
                return self.get_transcripts(video_id)
            if state in ("FAILED", "ERROR"):
                raise LividError(f"transcript generation failed: {status}")
            time.sleep(poll_seconds)
        raise TimeoutError(f"transcript for {video_id} not ready in time")

    # ---------- upload / replace ----------

    def upload_new_video(
        self,
        file_path: str | Path,
        folder_id: str,
        *,
        title: Optional[str] = None,
        progress_cb: Optional[ProgressCallback] = None,
    ) -> dict:
        """Upload a brand-new video into a folder (Livid_Log_1 flow).
        Returns {"videoId", "videoAssetId", "videoEncodeId"}."""
        file_path = Path(file_path)
        size, content_type, title = self._file_meta(file_path, title)
        body = {
            "eventId": str(uuid.uuid4()),
            "folderId": folder_id,
            "size": size,
            "title": title,
            "fileName": file_path.name,
            "contentType": content_type,
        }
        data = self._post("/v1/videos", body)
        return self._finish_upload(file_path, size, content_type, data, progress_cb)

    def replace_video(
        self,
        video_id: str,
        file_path: str | Path,
        *,
        progress_cb: Optional[ProgressCallback] = None,
    ) -> dict:
        """Replace an existing video's file with a new version (Livid_Log_2
        flow). The video keeps its id, slug and embed URL. Returns
        {"videoId", "videoAssetId", "videoEncodeId"}."""
        file_path = Path(file_path)
        size, content_type, _ = self._file_meta(file_path, None)
        body = {"size": size, "fileName": file_path.name, "contentType": content_type}
        data = self._post(f"/v1/videos/id/{video_id}/versions", body)
        # /versions response carries videoId; fall back to the arg just in case.
        data.setdefault("videoId", video_id)
        return self._finish_upload(file_path, size, content_type, data, progress_cb)

    def _finish_upload(self, file_path, size, content_type, create_data, progress_cb) -> dict:
        """Shared tail of both upload flows: PUT bytes to GCS, then
        complete-upload."""
        resumable_uri = create_data["resumableUri"]
        video_id = create_data["videoId"]
        video_asset_id = create_data["videoAssetId"]

        self._resumable_upload(resumable_uri, file_path, size, content_type, progress_cb)

        result = self._post(
            f"/v1/videos/id/{video_id}/complete-upload",
            {"eventId": str(uuid.uuid4()), "videoAssetId": video_asset_id},
        )
        return {
            "videoId": video_id,
            "videoAssetId": video_asset_id,
            "videoEncodeId": result.get("videoEncodeId"),
        }

    @staticmethod
    def _file_meta(file_path: Path, title: Optional[str]) -> tuple[int, str, str]:
        size = file_path.stat().st_size
        content_type = mimetypes.guess_type(file_path.name)[0] or "video/mp4"
        return size, content_type, (title or file_path.stem)

    def _resumable_upload(self, resumable_uri, file_path, size, content_type, progress_cb) -> None:
        """Drive the GCS resumable protocol: PUT chunks with Content-Range,
        follow 308s (trusting GCS's Range header) until a 200/201. Uses a
        bare requests call -- must NOT send Livid's session cookie to GCS."""
        uploaded = 0
        with open(file_path, "rb") as f:
            while uploaded < size:
                f.seek(uploaded)
                chunk = f.read(CHUNK_SIZE)
                end = uploaded + len(chunk) - 1
                resp = requests.put(
                    resumable_uri,
                    data=chunk,
                    headers={
                        "Content-Type": content_type,
                        "Content-Range": f"bytes {uploaded}-{end}/{size}",
                    },
                )
                if resp.status_code in (200, 201):
                    uploaded = size
                elif resp.status_code == 308:
                    rng = resp.headers.get("Range")
                    uploaded = int(rng.split("-")[1]) + 1 if rng else uploaded + len(chunk)
                else:
                    raise LividError(
                        f"GCS upload failed at byte {uploaded}: "
                        f"{resp.status_code} {resp.text[:200]}"
                    )
                if progress_cb:
                    progress_cb(min(100.0, 100.0 * uploaded / size))

    # ---------- encode status ----------

    def batch_status(self, video_ids: list[str]) -> dict:
        return self._post("/v1/videos/batch-status", {"videoIds": video_ids})

    def wait_for_encode(self, video_id: str, poll_seconds: int = 10, timeout_seconds: int = 3600) -> dict:
        """Poll batch-status until the video is encoded (or timeout)."""
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            video = self.batch_status([video_id])["videos"][0]
            if video.get("isEncoded"):
                return video
            if video.get("encodeStatus") == "FAILED":
                raise LividError(f"encode failed for {video_id}: {video}")
            time.sleep(poll_seconds)
        raise TimeoutError(f"video {video_id} did not finish encoding in time")


def build_embed_snippet(slug: str, title: str) -> str:
    """The exact markup Livid's 'Share & Embed' modal hands out."""
    embed_url = f"{EMBED_BASE}/{slug}"
    safe = html.escape(title, quote=True)
    return f"""<div style="padding:56.25% 0 0 0;position:relative;width:100%;"><iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture; web-share" allowfullscreen frameborder="0" referrerpolicy="strict-origin-when-cross-origin" src="{embed_url}" title="{safe}"></iframe></div>"""


# --------------------------------------------------------------------------
# CLI: quick manual exercising of every operation captured in the HARs.
#   Reads the session token from SESSION_TOKEN env var, or session.json.
# --------------------------------------------------------------------------
def _load_token() -> str:
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    # session.json (auth.py, possibly encrypted) is the primary source; the
    # SESSION_TOKEN env var is a convenience fallback.
    try:
        from utils import session_store
        tok = session_store.load_token_or_none()
        if tok:
            return tok
    except ImportError:
        pass
    tok = os.environ.get("SESSION_TOKEN")
    if tok:
        return tok
    raise SystemExit(
        "No session token. Run utils/auth.py to create session.json (set LIVID_SECRET_KEY "
        "in .env to encrypt it), or set SESSION_TOKEN."
    )


if __name__ == "__main__":
    import argparse, json as _json

    p = argparse.ArgumentParser(description="Unofficial Livid.com client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("folders", help="Print the folder tree with IDs")

    sv = sub.add_parser("videos", help="List videos in a folder")
    sv.add_argument("folder_id")

    gv = sub.add_parser("video", help="Show full detail for one video")
    gv.add_argument("video_id")

    up = sub.add_parser("upload", help="Upload a new video into a folder")
    up.add_argument("file")
    up.add_argument("--folder-id", required=True)
    up.add_argument("--title")

    rp = sub.add_parser("replace", help="Replace a video's file with a new version")
    rp.add_argument("video_id")
    rp.add_argument("file")

    rn = sub.add_parser("rename", help="Rename a video")
    rn.add_argument("video_id")
    rn.add_argument("title")

    pr = sub.add_parser("privacy", help="Set privacy: private|public|unlisted|password")
    pr.add_argument("video_id")
    pr.add_argument("privacy", choices=PRIVACY_VALUES)

    pw = sub.add_parser("password", help="Password-protect a video")
    pw.add_argument("video_id")
    pw.add_argument("password")

    ap = sub.add_parser("appearance", help="Update player appearance (key=value pairs)")
    ap.add_argument("video_id")
    ap.add_argument("fields", nargs="+", help='e.g. controlsShareEnabled=false colorsAccent=#ff0000')

    tr = sub.add_parser("transcript", help="Generate a transcript (and optionally wait)")
    tr.add_argument("video_id")
    tr.add_argument("--wait", action="store_true")

    args = p.parse_args()
    client = LividClient(_load_token())

    def _progress(pct):
        print(f"\r  uploading... {pct:5.1f}%", end="", flush=True)

    def _coerce(v: str):
        if v.lower() in ("true", "false"):
            return v.lower() == "true"
        if v.lower() in ("null", "none"):
            return None
        try:
            return int(v)
        except ValueError:
            return v

    if args.cmd == "folders":
        client.print_folder_tree()
    elif args.cmd == "videos":
        for v in client.list_videos(args.folder_id):
            print(f"{v.id}  {'[encoded]' if v.is_encoded else '[pending]'}  {v.title}")
    elif args.cmd == "video":
        print(_json.dumps(client.get_video(args.video_id), indent=2)[:4000])
    elif args.cmd == "upload":
        print(_json.dumps(client.upload_new_video(args.file, args.folder_id, title=args.title, progress_cb=_progress), indent=2))
    elif args.cmd == "replace":
        print(_json.dumps(client.replace_video(args.video_id, args.file, progress_cb=_progress), indent=2))
    elif args.cmd == "rename":
        print(client.rename_video(args.video_id, args.title))
    elif args.cmd == "privacy":
        print(client.set_privacy(args.video_id, args.privacy))
    elif args.cmd == "password":
        print(client.set_password(args.video_id, args.password))
    elif args.cmd == "appearance":
        fields = {}
        for pair in args.fields:
            k, _, v = pair.partition("=")
            fields[k] = _coerce(v)
        print(client.update_appearance(args.video_id, **fields))
    elif args.cmd == "transcript":
        print(client.generate_transcript(args.video_id))
        if args.wait:
            print(_json.dumps(client.wait_for_transcript(args.video_id), indent=2)[:2000])
