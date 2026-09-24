"""Write Markdown + CSV reports under out/."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from follow_tracker.config import OUT_DIR


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_non_followback_report(
    username: str,
    non_fb: list[dict],
    following_count: int,
    followers_count: int,
) -> tuple[Path, Path]:
    stamp = _stamp()
    md_path = OUT_DIR / f"non_followbacks_{stamp}.md"
    csv_path = OUT_DIR / f"non_followbacks_{stamp}.csv"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Non-follow-backs for @{username}",
        "",
        f"- Generated: {now}",
        f"- Following: {following_count}",
        f"- Followers: {followers_count}",
        f"- Do not follow back: **{len(non_fb)}**",
        "",
        "| # | Username | Name | User ID |",
        "|---|----------|------|---------|",
    ]
    for i, u in enumerate(non_fb, 1):
        un = u.get("username", "")
        lines.append(
            f"| {i} | [@{un}](https://x.com/{un}) | {u.get('name', '')} | `{u.get('id', '')}` |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    write_csv(csv_path, non_fb, ["id", "username", "name"])

    # stable latest copies
    (OUT_DIR / "non_followbacks_latest.md").write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_csv(OUT_DIR / "non_followbacks_latest.csv", non_fb, ["id", "username", "name"])
    return md_path, csv_path


def write_unfollow_report(username: str, unfollowed: list[dict], previous_label: str) -> tuple[Path, Path]:
    stamp = _stamp()
    md_path = OUT_DIR / f"unfollows_{stamp}.md"
    csv_path = OUT_DIR / f"unfollows_{stamp}.csv"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Unfollows since last snapshot — @{username}",
        "",
        f"- Generated: {now}",
        f"- Compared against: `{previous_label}`",
        f"- Unfollowed you: **{len(unfollowed)}**",
        "",
    ]
    if not unfollowed:
        lines.append("_Nobody unfollowed since the previous followers snapshot._")
        lines.append("")
    else:
        lines.extend(
            [
                "| # | Username | Name | User ID |",
                "|---|----------|------|---------|",
            ]
        )
        for i, u in enumerate(unfollowed, 1):
            un = u.get("username", "")
            lines.append(
                f"| {i} | [@{un}](https://x.com/{un}) | {u.get('name', '')} | `{u.get('id', '')}` |"
            )
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    write_csv(csv_path, unfollowed, ["id", "username", "name"])
    (OUT_DIR / "unfollows_latest.md").write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_csv(OUT_DIR / "unfollows_latest.csv", unfollowed, ["id", "username", "name"])
    return md_path, csv_path
