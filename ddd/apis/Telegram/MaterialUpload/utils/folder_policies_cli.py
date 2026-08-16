"""
Manage folder privacy policies in SQL Server's LividFolderTable.

    python utils/folder_policies_cli.py seed --dry-run     # infer from Livid, show only
    python utils/folder_policies_cli.py seed               # infer and write to SQL
    python utils/folder_policies_cli.py list                # show what's in the table
    python utils/folder_policies_cli.py set <folder_id> --password Xyz [--name "..."]
    python utils/folder_policies_cli.py set <folder_id> --unlisted   [--name "..."]
    python utils/folder_policies_cli.py remove <folder_id>

`seed` walks the whole Livid folder tree and infers each folder's policy from
its newest videos (--sample per folder, default 3):

    any password-protected video  -> password policy (most common password)
    else mostly unlisted          -> unlisted policy (Password NULL in SQL)
    else (private / mixed)        -> skipped; add manually with `set` if wanted

The bot then applies these policies to every NEW upload automatically
(see _auto_post_process in livid_telegram_bot.py).
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

# Windows console defaults to cp1252, which can't print Korean/CJK titles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # this file now lives in utils/
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from livid_client import LividClient, LividError
from utils import session_store, folder_policies


def _client() -> LividClient:
    return LividClient(session_store.load_token())


def infer_policy(client: LividClient, folder_id: str, sample: int) -> tuple[str, str | None] | None:
    """Look at the newest `sample` videos and decide the folder's policy.
    Returns ('password', pw) | ('unlisted', None) | None (no clear policy)."""
    videos = client.list_videos(folder_id)[:sample]
    if not videos:
        return None
    passwords: Counter[str] = Counter()
    pages: Counter[str] = Counter()
    for v in videos:
        detail = client.get_video(v.id)
        page = detail.get("privacyPage") or "private"
        pages[page] += 1
        if page == "password" and detail.get("privacyPassword"):
            passwords[detail["privacyPassword"]] += 1
    if passwords:
        return "password", passwords.most_common(1)[0][0]
    if pages.get("unlisted", 0) * 2 >= sum(pages.values()):
        return "unlisted", None
    return None


def walk_folders(client: LividClient, folders=None, path=""):
    """Yield (folder_dict, 'parent / child' display path) for the whole tree."""
    if folders is None:
        folders = client.list_folders()
    for f in folders:
        full = f"{path} / {f['name']}" if path else f["name"]
        yield f, full
        if f.get("_count", {}).get("childFolders"):
            yield from walk_folders(client, client.list_subfolders(f["id"]), full)


def cmd_seed(dry_run: bool, sample: int) -> None:
    client = _client()
    planned, skipped = [], []
    for f, full_path in walk_folders(client):
        if not f.get("_count", {}).get("videos"):
            continue
        try:
            policy = infer_policy(client, f["id"], sample)
        except LividError as exc:
            print(f"!! {full_path}: could not inspect videos ({exc})")
            continue
        if policy is None:
            skipped.append(full_path)
            continue
        privacy, password = policy
        planned.append((f["id"], f["name"], full_path, privacy, password))
        shown = f"password [{password}]" if password else "unlisted"
        print(f"   {full_path}  ->  {shown}")

    print(f"\n{len(planned)} folders with a policy, {len(skipped)} skipped (private/mixed):")
    for s in skipped:
        print(f"   skipped: {s}")

    if dry_run:
        print("\nDry run -- nothing written. Re-run without --dry-run to save.")
        return

    print()
    for folder_id, name, full_path, privacy, password in planned:
        action = folder_policies.upsert_policy(folder_id, name, password)
        print(f"   {action}: {full_path}")
    folder_policies.invalidate_cache()
    print(f"\nDone -- {len(planned)} rows written to {folder_policies.TABLE}.")


def cmd_list() -> None:
    rows = folder_policies.list_policies()
    if not rows:
        print(f"{folder_policies.TABLE} has no policy rows yet. Run `seed`.")
        return
    for p in rows:
        shown = f"password [{p.password}]" if p.password else "unlisted"
        print(f"   {p.name:<30} {shown:<28} {p.folder_id}")
    print(f"\n{len(rows)} rows.")


def cmd_set(folder_id: str, password: str | None, name: str | None) -> None:
    if not name:
        name = _client().get_folder(folder_id)["folder"]["name"]
        assert isinstance(name, str), "Expected folder name to be a string"
    action = folder_policies.upsert_policy(folder_id, name, password)
    folder_policies.invalidate_cache()
    shown = f"password [{password}]" if password else "unlisted"
    print(f"{action}: {name} ({folder_id}) -> {shown}")


def cmd_remove(folder_id: str) -> None:
    n = folder_policies.delete_policy(folder_id)
    folder_policies.invalidate_cache()
    print(f"removed {n} row(s) for {folder_id} -- new uploads there stay private.")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Folder privacy policies (LividFolderTable)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sd = sub.add_parser("seed", help="Infer policies from Livid and write them to SQL")
    sd.add_argument("--dry-run", action="store_true", help="show the plan without writing")
    sd.add_argument("--sample", type=int, default=3, help="videos to inspect per folder (default 3)")

    sub.add_parser("list", help="Show the policy rows in SQL")

    st = sub.add_parser("set", help="Set one folder's policy by hand")
    st.add_argument("folder_id")
    grp = st.add_mutually_exclusive_group(required=True)
    grp.add_argument("--password", help="password-protect new uploads with this")
    grp.add_argument("--unlisted", action="store_true", help="make new uploads unlisted")
    st.add_argument("--name", help="folder name for the row (default: fetched from Livid)")

    rm = sub.add_parser("remove", help="Remove a folder's policy row")
    rm.add_argument("folder_id")

    args = p.parse_args()
    if args.cmd == "seed":
        cmd_seed(args.dry_run, args.sample)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "set":
        cmd_set(args.folder_id, args.password if not args.unlisted else None, args.name)
    elif args.cmd == "remove":
        cmd_remove(args.folder_id)
