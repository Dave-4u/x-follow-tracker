"""CLI entry: python -m follow_tracker <scan|watch|run>."""

from __future__ import annotations

import argparse
import sys

from follow_tracker import __version__
from follow_tracker.config import ensure_dirs, load_app_config, load_project_config, save_project_config


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="follow_tracker",
        description=(
            "Local X follow-tracker (twikit + browser cookies). "
            "No official X API / no API credits."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "--username",
        "-u",
        default=None,
        help="X username without @ (default: value in config.json)",
    )

    sub = p.add_subparsers(dest="command")

    sub.add_parser("scan", help="List accounts you follow who do not follow back; save snapshots + reports")
    sub.add_parser("watch", help="Diff current followers vs last snapshot; report who unfollowed")
    sub.add_parser("run", help="Fetch once: unfollow diff + non-follow-back report + snapshots")

    cfg_p = sub.add_parser("config", help="Show or set username in config.json")
    cfg_p.add_argument("--set-username", metavar="NAME", help="Persist username to config.json")

    return p


def main(argv: list[str] | None = None) -> int:
    ensure_dirs()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "config":
        if args.set_username:
            save_project_config(args.set_username.lstrip("@"))
            print(f"Saved username: {args.set_username.lstrip('@')}")
        proj = load_project_config()
        print(f"username: {proj.get('username')}")
        print(f"user_id:  {proj.get('user_id')}")
        return 0

    # Commands that hit X require cookies
    cfg = load_app_config(username=args.username)
    if args.username:
        save_project_config(cfg.username, cfg.user_id)

    from follow_tracker import tracker

    if args.command == "scan":
        tracker.scan(cfg)
    elif args.command == "watch":
        tracker.watch(cfg)
    elif args.command == "run":
        tracker.run(cfg)
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
