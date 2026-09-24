"""twikit client helpers (cookie auth only — no official X API)."""

from __future__ import annotations

import asyncio
from typing import Any

from twikit import Client

from follow_tracker.config import AppConfig, save_project_config


def make_client(cfg: AppConfig) -> Client:
    client = Client("en-US")
    client.set_cookies(
        {"auth_token": cfg.auth_token, "ct0": cfg.ct0},
        clear_cookies=True,
    )
    return client


async def resolve_user_id(client: Client, cfg: AppConfig) -> str:
    if cfg.user_id:
        return cfg.user_id
    user = await client.get_user_by_screen_name(cfg.username)
    uid = str(user.id)
    save_project_config(cfg.username, uid)
    return uid


def _user_row(user: Any) -> dict[str, str]:
    return {
        "id": str(getattr(user, "id", "")),
        "username": str(getattr(user, "screen_name", "") or getattr(user, "username", "")),
        "name": str(getattr(user, "name", "") or ""),
    }


async def _paginate_users(fetch_first, *, page_size: int = 100, pause: float = 0.6) -> list[dict[str, str]]:
    """Walk Result.next() until exhausted."""
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    result = await fetch_first()
    while True:
        batch = list(result) if result else []
        if not batch:
            break
        for u in batch:
            row = _user_row(u)
            if row["id"] and row["id"] not in seen:
                seen.add(row["id"])
                rows.append(row)
        nxt = await result.next()
        if not nxt or not list(nxt):
            break
        result = nxt
        await asyncio.sleep(pause)
    return rows


async def fetch_following(client: Client, user_id: str) -> list[dict[str, str]]:
    return await _paginate_users(
        lambda: client.get_user_following(user_id, count=100),
    )


async def fetch_followers(client: Client, user_id: str) -> list[dict[str, str]]:
    return await _paginate_users(
        lambda: client.get_user_followers(user_id, count=100),
    )
