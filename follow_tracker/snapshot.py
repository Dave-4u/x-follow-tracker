"""Persist and diff following/followers snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from follow_tracker.config import DATA_DIR


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def latest_snapshot_path(kind: str) -> Path | None:
    """kind is 'following' or 'followers'."""
    matches = sorted(DATA_DIR.glob(f"{kind}_*.json"))
    return matches[-1] if matches else None


def load_users(path: Path | None) -> list[dict]:
    if path is None or not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return list(data.get("users") or [])
    return list(data)


def save_snapshot(kind: str, users: list[dict], username: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{kind}_{_stamp()}.json"
    payload = {
        "kind": kind,
        "username": username,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "count": len(users),
        "users": users,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    # also write a stable "latest" pointer file for convenience
    latest = DATA_DIR / f"{kind}_latest.json"
    with latest.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return path


def index_by_id(users: list[dict]) -> dict[str, dict]:
    return {str(u["id"]): u for u in users if u.get("id")}


def diff_unfollowed(previous: list[dict], current: list[dict]) -> list[dict]:
    """Accounts present in previous followers but missing from current."""
    cur = index_by_id(current)
    return [u for u in previous if str(u.get("id")) not in cur]
