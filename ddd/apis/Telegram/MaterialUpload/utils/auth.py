"""
Interactive login for Livid.com.

Livid's login is "Sign in with Google" (via better-auth), so there's no
username/password request worth scripting. Instead, this opens a real browser
window, lets you complete the Google login yourself (including 2FA if you have
it), then saves the resulting session token to disk (encrypted if
LIVID_SECRET_KEY is set) so the bot / client can reuse it.

Usage:
    python utils/auth.py

This opens a browser. Log in to Livid as you normally would. Once you land on
your library page (https://livid.com/library), come back to the terminal and
press Enter. The token is saved to auth/session.json (see session_store).
"""

import os
import sys

# Allow running as a script (python utils/auth.py) or being imported as
# utils.auth: put the project root on sys.path so `from utils import ...` works
# either way.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from utils import session_store

load_dotenv(session_store.PROJECT_ROOT / ".env")

LOGIN_URL = "https://livid.com/login"
LOGGED_IN_URL_HINT = "livid.com/library"


def login_and_save_session():
    with sync_playwright() as p:
        # Google blocks Playwright's bundled Chromium build as an "insecure"
        # automated browser. Launching your real, installed Chrome (channel=
        # "chrome") with automation flags stripped avoids that check.
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
            )
        )
        # Playwright sets navigator.webdriver = true by default, which Google
        # also checks for. Strip it before any page script runs.
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        page.goto(LOGIN_URL)

        print(f"\nA browser window has opened at {LOGIN_URL}.")
        print("Log in with Google as you normally would.")
        print(f"Once you're redirected to your library ({LOGGED_IN_URL_HINT}),")
        input("come back here and press Enter to save the session...")

        cookies = context.cookies()
        token = session_store.extract_token_from_cookies(cookies)

        if not token:
            print("No Livid session token found — login probably didn't complete. Nothing saved.")
            browser.close()
            return

        # Save just the session token, encrypted at rest if LIVID_SECRET_KEY is
        # set in .env (recommended). session_store is the single source of truth.
        encrypted = session_store.save_token(token)
        how = "encrypted with LIVID_SECRET_KEY" if encrypted else "in plaintext (set LIVID_SECRET_KEY to encrypt)"
        print(f"Saved session token to {session_store.SESSION_FILE} ({how}).")
        browser.close()


def load_cookies_for_requests():
    """Return {name: value} suitable for requests.Session.cookies.update().
    Only the Livid session cookie matters, so that's all we reconstruct."""
    token = session_store.load_token()
    return {session_store.COOKIE_NAME: token}


if __name__ == "__main__":
    login_and_save_session()
