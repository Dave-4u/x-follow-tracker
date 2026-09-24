"""Core scan / watch logic."""

from __future__ import annotations

import asyncio

from follow_tracker.client import fetch_followers, fetch_following, make_client, resolve_user_id
from follow_tracker.config import AppConfig, DATA_DIR
from follow_tracker.report import write_non_followback_report, write_unfollow_report
from follow_tracker.snapshot import (
    diff_unfollowed,
    index_by_id,
    latest_snapshot_path,
    load_users,
    save_snapshot,
)


async def _gather(cfg: AppConfig) -> tuple[list[dict], list[dict]]:
    client = make_client(cfg)
    user_id = await resolve_user_id(client, cfg)
    print(f"Fetching lists for @{cfg.username} (id={user_id}) …")
    following = await fetch_following(client, user_id)
    print(f"  following: {len(following)}")
    followers = await fetch_followers(client, user_id)
    print(f"  followers: {len(followers)}")
    return following, followers


def non_followbacks(following: list[dict], followers: list[dict]) -> list[dict]:
    follower_ids = index_by_id(followers)
    return [u for u in following if str(u.get("id")) not in follower_ids]


async def scan_async(cfg: AppConfig) -> None:
    following, followers = await _gather(cfg)
    save_snapshot("following", following, cfg.username)
    save_snapshot("followers", followers, cfg.username)
    nf = non_followbacks(following, followers)
    md, csv_path = write_non_followback_report(cfg.username, nf, len(following), len(followers))
    print(f"Non-follow-backs: {len(nf)}")
    print(f"  Markdown: {md}")
    print(f"  CSV:      {csv_path}")
    print(f"Snapshots saved under {DATA_DIR}")


async def watch_async(cfg: AppConfig) -> None:
    """Compare current followers to previous snapshot; then save new snapshots."""
    prev_path = DATA_DIR / "followers_latest.json"
    if not prev_path.exists():
        prev_path = latest_snapshot_path("followers")
    previous = load_users(prev_path)

    following, followers = await _gather(cfg)
    # Save new snapshots after diff so "previous" is truly the last run
    unfollowed = diff_unfollowed(previous, followers) if previous else []
    label = prev_path.name if prev_path else "(none — first run)"
    md, csv_path = write_unfollow_report(cfg.username, unfollowed, label)

    save_snapshot("following", following, cfg.username)
    save_snapshot("followers", followers, cfg.username)

    if not previous:
        print("No previous followers snapshot — saved a baseline. Run watch again later to detect unfollows.")
    else:
        print(f"Unfollowed since {label}: {len(unfollowed)}")
    print(f"  Markdown: {md}")
    print(f"  CSV:      {csv_path}")


async def run_async(cfg: AppConfig) -> None:
    """Watch (unfollow diff) then non-follow-back report, one fetch."""
    prev_path = DATA_DIR / "followers_latest.json"
    if not prev_path.exists():
        prev_path = latest_snapshot_path("followers")
    previous = load_users(prev_path)

    following, followers = await _gather(cfg)

    unfollowed = diff_unfollowed(previous, followers) if previous else []
    label = prev_path.name if prev_path else "(none — first run)"
    umd, ucsv = write_unfollow_report(cfg.username, unfollowed, label)

    nf = non_followbacks(following, followers)
    nmd, ncsv = write_non_followback_report(cfg.username, nf, len(following), len(followers))

    save_snapshot("following", following, cfg.username)
    save_snapshot("followers", followers, cfg.username)

    if not previous:
        print("No previous followers snapshot — saved a baseline for future unfollow diffs.")
    else:
        print(f"Unfollowed since {label}: {len(unfollowed)}")
        print(f"  Markdown: {umd}")
        print(f"  CSV:      {ucsv}")
    print(f"Non-follow-backs: {len(nf)}")
    print(f"  Markdown: {nmd}")
    print(f"  CSV:      {ncsv}")


def scan(cfg: AppConfig) -> None:
    asyncio.run(scan_async(cfg))


def watch(cfg: AppConfig) -> None:
    asyncio.run(watch_async(cfg))


def run(cfg: AppConfig) -> None:
    asyncio.run(run_async(cfg))
