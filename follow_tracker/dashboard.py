"""Follow Ledger: a local, read-only dashboard over your saved snapshots.

    python -m follow_tracker dashboard        # http://127.0.0.1:8770

Needs no cookies: it only reads data/*.json written by scan/watch/run and
serves docs/index.html (the same page as the GitHub Pages demo). It binds to
127.0.0.1 by default so your lists stay on your machine.
"""

from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from follow_tracker import config as cfgmod
from follow_tracker.snapshot import load_users

DOCS = cfgmod.ROOT / "docs"


def _timestamped(kind: str, data_dir: Path) -> list[Path]:
    return sorted(p for p in data_dir.glob(f"{kind}_*.json") if not p.name.endswith("_latest.json"))


def snapshot_payload(data_dir: Path | None = None) -> dict:
    data_dir = data_dir or cfgmod.DATA_DIR
    fing = _timestamped("following", data_dir)
    fers = _timestamped("followers", data_dir)
    files = []
    following = load_users(fing[-1]) if fing else []
    followers = load_users(fers[-1]) if fers else []
    previous = load_users(fers[-2]) if len(fers) > 1 else []
    if fing:
        files.append(f"{fing[-1].name} · {len(following)}")
    if fers:
        files.append(f"{fers[-1].name} · {len(followers)}")
    if len(fers) > 1:
        files.append(f"{fers[-2].name} (previous) · {len(previous)}")
    return {
        "ok": True,
        "username": cfgmod.load_project_config().get("username", ""),
        "following": following,
        "followers": followers,
        "previous_followers": previous,
        "files": files,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = unquote(urlparse(self.path).path)
        if path in ("/api/snapshots", "/api/snapshots/"):
            return self._send(200, json.dumps(snapshot_payload()).encode(), "application/json")
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (DOCS / rel).resolve()
        if DOCS.resolve() not in target.parents or not target.is_file():
            return self._send(404, b'{"error":"not found"}', "application/json")
        self._send(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or "application/octet-stream")


def serve(host: str = "127.0.0.1", port: int = 8770) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Follow Ledger on http://{host}:{port}  (read-only, Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
