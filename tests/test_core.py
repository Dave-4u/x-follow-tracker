import json
import shutil
import subprocess
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from follow_tracker import dashboard
from follow_tracker.snapshot import diff_unfollowed
from follow_tracker.tracker import non_followbacks

ROOT = Path(__file__).resolve().parent.parent
A, B, C, D = ({"id": str(i), "username": f"u{i}", "name": f"User {i}"} for i in range(1, 5))


def test_non_followbacks():
    assert non_followbacks([A, B, C], [B, D]) == [A, C]


def test_diff_unfollowed():
    assert diff_unfollowed([A, B, C], [B]) == [A, C]
    assert diff_unfollowed([], [B]) == []


def _write(dirp: Path, name: str, kind: str, users):
    (dirp / name).write_text(json.dumps({"kind": kind, "users": users}))


def test_snapshot_payload_picks_latest_and_previous(tmp_path):
    _write(tmp_path, "following_20260101T000000Z.json", "following", [A, B, C])
    _write(tmp_path, "followers_20260101T000000Z.json", "followers", [A, B, D])
    _write(tmp_path, "followers_20260201T000000Z.json", "followers", [B, D])
    _write(tmp_path, "followers_latest.json", "followers", [B, D])
    p = dashboard.snapshot_payload(tmp_path)
    assert p["following"] == [A, B, C]
    assert p["followers"] == [B, D]
    assert p["previous_followers"] == [A, B, D]


def test_dashboard_serves_page_and_api(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard.cfgmod, "DATA_DIR", tmp_path)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        assert b"Follow Ledger" in urllib.request.urlopen(base + "/").read()
        data = json.loads(urllib.request.urlopen(base + "/api/snapshots").read())
        assert data["ok"] and data["following"] == []
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(base + "/../config.json")
    finally:
        srv.shutdown()


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_ledger_matches_python():
    following, followers, prev = [A, B, C], [B, D], [A, B, D]
    js = subprocess.check_output(
        ["node", "-e", f"const L=require('./docs/ledger.js');console.log(JSON.stringify(L.compare({json.dumps(following)},{json.dumps(followers)},{json.dumps(prev)})))"],
        cwd=ROOT,
    )
    r = json.loads(js)
    assert r["notBack"] == non_followbacks(following, followers)
    assert r["unfollowed"] == diff_unfollowed(prev, followers)
    assert r["mutuals"] == [B] and r["fans"] == [D]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_parses_x_archive():
    text = 'window.YTD.following.part0 = [{"following":{"accountId":"42","userLink":"https://twitter.com/intent/user?user_id=42"}}]'
    out = subprocess.check_output(["node", "-e", f"const L=require('./docs/ledger.js');console.log(JSON.stringify(L.parseFile('following.js',{json.dumps(text)})))"], cwd=ROOT)
    r = json.loads(out)
    assert r["kind"] == "following" and r["users"][0]["id"] == "42"
