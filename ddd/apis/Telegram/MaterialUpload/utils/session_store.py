"""
Session-token storage for the unofficial Livid tooling.

Livid authenticates with a single cookie, `__Secure-livid.session_token`.
auth.py captures it via a real browser login; everything else replays it.
This module is the one place that reads/writes that token to disk, so it can
also encrypt it at rest.

Why encrypt: the raw token is equivalent to your logged-in session. Storing it
in plaintext in session.json means anyone who can read the file can act as you.
Instead, set a passphrase in .env:

    LIVID_SECRET_KEY=some-long-random-passphrase

and the token is encrypted with it (Fernet / AES). session.json then holds only
ciphertext; without the passphrase it's useless. If LIVID_SECRET_KEY is unset,
the token is stored in plaintext (with a warning) so nothing breaks -- but
setting it is recommended.

When the token expires (API calls start returning 401/403), just re-run
`python utils/auth.py` to log in again; it re-saves a fresh (encrypted) token here.

session.json format written by this module:
    {"format": "livid-session-v1", "encrypted": true|false,
     "token": "<ciphertext or plaintext>", "saved_at": "<iso8601>"}

For backward compatibility, load_token() also understands the older format
where session.json was the raw Playwright cookie list.
"""

from __future__ import annotations

import os
import json
import base64
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# This module lives in utils/, but the session artifacts live in an auth/
# folder at the project root, so anchor to the parent directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTH_DIR = PROJECT_ROOT / "auth"          # session.json + livid_bot_session.session
SESSION_FILE = AUTH_DIR / "session.json"
COOKIE_NAME = "__Secure-livid.session_token"
SECRET_ENV = "LIVID_SECRET_KEY"
FORMAT_TAG = "livid-session-v1"


class SessionError(RuntimeError):
    """Raised when the session token can't be loaded/decrypted."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fernet(secret: str):
    """Build a Fernet from an arbitrary passphrase. The passphrase is hashed to
    a 32-byte key so the user can pick any string as LIVID_SECRET_KEY."""
    from cryptography.fernet import Fernet  # lazy import; only needed when encrypting
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(key)


def _resolve_secret(secret: Optional[str]) -> str:
    return secret if secret is not None else os.environ.get(SECRET_ENV, "")


def save_token(token: str, secret: Optional[str] = None) -> bool:
    """Persist the session token to session.json. Encrypts it if a secret is
    given (or LIVID_SECRET_KEY is set). Returns True if it was encrypted."""
    if not token:
        raise ValueError("refusing to save an empty session token")
    secret = _resolve_secret(secret)
    if secret:
        stored = _fernet(secret).encrypt(token.encode("utf-8")).decode("ascii")
        encrypted = True
    else:
        stored = token
        encrypted = False
    payload = {
        "format": FORMAT_TAG,
        "encrypted": encrypted,
        "token": stored,
        "saved_at": _now_iso(),
    }
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(payload, indent=2))
    return encrypted


def extract_token_from_cookies(cookies: list[dict]) -> Optional[str]:
    """Pull the Livid session token out of a Playwright cookie list."""
    for c in cookies:
        if c.get("name") == COOKIE_NAME:
            return c.get("value")
    return None


def load_token(secret: Optional[str] = None) -> str:
    """Read (and decrypt if needed) the session token from session.json.
    Raises SessionError with an actionable message on any problem."""
    if not SESSION_FILE.exists():
        raise SessionError(
            f"No {SESSION_FILE.name} found. Run `python utils/auth.py` to log in first."
        )
    try:
        raw = json.loads(SESSION_FILE.read_text())
    except json.JSONDecodeError as exc:
        raise SessionError(f"{SESSION_FILE.name} is not valid JSON: {exc}")

    # Old format: the raw Playwright cookie list.
    if isinstance(raw, list):
        tok = extract_token_from_cookies(raw)
        if tok:
            return tok
        raise SessionError(
            f"{SESSION_FILE.name} (old cookie format) has no {COOKIE_NAME}. Re-run utils/auth.py."
        )

    if isinstance(raw, dict):
        if not raw.get("encrypted"):
            tok = raw.get("token")
            if tok:
                return tok
            raise SessionError(f"{SESSION_FILE.name} has no token. Re-run utils/auth.py.")
        # Encrypted -- need the passphrase.
        secret = _resolve_secret(secret)
        if not secret:
            raise SessionError(
                f"{SESSION_FILE.name} is encrypted but {SECRET_ENV} is not set in .env."
            )
        from cryptography.fernet import InvalidToken
        try:
            return _fernet(secret).decrypt(raw["token"].encode("ascii")).decode("utf-8")
        except InvalidToken:
            raise SessionError(
                f"Could not decrypt the session token -- wrong {SECRET_ENV}?"
            )

    raise SessionError(f"Unrecognized {SESSION_FILE.name} format. Re-run utils/auth.py.")


def load_token_or_none(secret: Optional[str] = None) -> Optional[str]:
    try:
        return load_token(secret)
    except SessionError:
        return None


# --------------------------------------------------------------------------
# CLI helpers:
#   python session_store.py check      -> report whether a token loads
#   python session_store.py migrate    -> re-encrypt an existing session.json
#                                          using the current LIVID_SECRET_KEY
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        try:
            tok = load_token()
        except SessionError as e:
            print(f"[x] {e}")
            sys.exit(1)
        raw = json.loads(SESSION_FILE.read_text()) if SESSION_FILE.exists() else {}
        enc = isinstance(raw, dict) and raw.get("encrypted")
        masked = tok[:6] + "..." + tok[-4:] if len(tok) > 12 else "..."
        print(f"[ok] token loads (encrypted at rest: {bool(enc)}) -> {masked}")

    elif cmd == "migrate":
        tok = load_token()  # decrypts/normalizes whatever is there now
        encrypted = save_token(tok)  # re-saves in current format
        if encrypted:
            print("[ok] session.json re-saved, encrypted with LIVID_SECRET_KEY.")
        else:
            print("[-] session.json re-saved in plaintext (LIVID_SECRET_KEY not set).")

    else:
        print("usage: python session_store.py [check|migrate]")
        sys.exit(2)
