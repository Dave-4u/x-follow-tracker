"""Load project config and cookie credentials from the environment."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"


@dataclass(frozen=True)
class AppConfig:
    username: str
    user_id: str | None
    auth_token: str
    ct0: str


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_project_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"username": "officialdev05", "user_id": "2095430768872841217"}
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def save_project_config(username: str, user_id: str | None = None) -> None:
    data = load_project_config()
    data["username"] = username.lstrip("@")
    if user_id:
        data["user_id"] = str(user_id)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def require_cookies() -> tuple[str, str]:
    """Load AUTH_TOKEN and CT0 from .env / environment. Exit clearly if missing."""
    load_dotenv(ROOT / ".env")
    auth = (os.environ.get("AUTH_TOKEN") or "").strip()
    ct0 = (os.environ.get("CT0") or "").strip()
    missing = []
    if not auth or auth.startswith("your_"):
        missing.append("AUTH_TOKEN")
    if not ct0 or ct0.startswith("your_"):
        missing.append("CT0")
    if missing:
        print(
            "Missing X session cookies: " + ", ".join(missing) + "\n\n"
            "Set them locally (do not send these to anyone):\n"
            "  1. Copy .env.example to .env\n"
            "  2. Log in at https://x.com → DevTools (F12) → Application → Cookies → https://x.com\n"
            "  3. Paste auth_token into AUTH_TOKEN and ct0 into CT0\n"
            "  4. Re-run this command\n\n"
            "Example:\n"
            "  cp .env.example .env\n"
            "  # edit .env, then:\n"
            "  python -m follow_tracker run\n",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return auth, ct0


def load_app_config(username: str | None = None) -> AppConfig:
    ensure_dirs()
    proj = load_project_config()
    uname = (username or proj.get("username") or "officialdev05").lstrip("@")
    uid = proj.get("user_id")
    auth, ct0 = require_cookies()
    return AppConfig(username=uname, user_id=str(uid) if uid else None, auth_token=auth, ct0=ct0)
