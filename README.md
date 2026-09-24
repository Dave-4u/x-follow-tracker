# X Follow Tracker

Local follow/follower tracker for X (Twitter). Uses **browser session cookies** via [twikit](https://github.com/d60/twikit) — **no official X API** and **no API credits**.

Default account: `@officialdev05` (configurable in `config.json`).

## What it does

| Command | Purpose |
|---------|---------|
| `scan` | List accounts you **follow who do not follow back**. Writes Markdown + CSV under `out/`, and snapshots under `data/`. |
| `watch` | Compare current followers to the previous snapshot; report who **unfollowed** you. |
| `run` | One fetch: unfollow diff **and** non-follow-back report + snapshots. |
| `config` | Show or set the tracked username. |

## Requirements

- Python 3.10+ (3.11/3.12/3.13 fine)
- Your own X account cookies (`AUTH_TOKEN`, `CT0`) — kept only on **your** machine

## Quick start

### 1. Unpack and create a venv

**macOS / Linux**

```bash
cd x-follow-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/apply_twikit_patch.py
```

**Windows (cmd)**

```bat
cd x-follow-tracker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\apply_twikit_patch.py
```

**Windows (PowerShell)**

```powershell
cd x-follow-tracker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\apply_twikit_patch.py
```

### 2. Get cookies from your browser

1. Log in to [https://x.com](https://x.com) in Chrome or Firefox.
2. Open DevTools → **F12** (or right-click → Inspect).
3. Go to **Application** (Chrome) or **Storage** (Firefox) → **Cookies** → `https://x.com`.
4. Copy:
   - `auth_token` → this is `AUTH_TOKEN`
   - `ct0` → this is `CT0`

Cookies expire over time. If requests start failing, repeat this step with fresh values.

### 3. Create `.env` (never commit this file)

```bash
cp .env.example .env
```

Edit `.env` and paste your values:

```env
AUTH_TOKEN=paste_auth_token_here
CT0=paste_ct0_here
```

Keep `.env` private. Do **not** email, chat, or upload these cookies.

### 4. (Optional) set username

Default is already `officialdev05` in `config.json`. To change:

```bash
# macOS / Linux (venv activated)
python -m follow_tracker config --set-username yourname

# Windows
.\.venv\Scripts\python.exe -m follow_tracker config --set-username yourname
```

Or edit `config.json` directly.

### 5. Run

> **Windows:** Do **not** use bare `python -m follow_tracker …` — that hits the system Python and usually fails with `ModuleNotFoundError: twikit`. Always use the venv interpreter or the helpers below.

**Windows (recommended)**

```powershell
# PowerShell — creates .venv / .env from example if needed, applies patches, then runs
.\run.ps1

# Or call the venv python directly:
.\.venv\Scripts\python.exe -m follow_tracker run
.\.venv\Scripts\python.exe -m follow_tracker scan
.\.venv\Scripts\python.exe -m follow_tracker watch
```

```bat
REM cmd.exe
run.bat
.venv\Scripts\python.exe -m follow_tracker run
```

**macOS / Linux**

```bash
# Help (works without cookies)
python -m follow_tracker --help

# Full pass: unfollow diff + non-follow-backs
python -m follow_tracker run

# Only non-follow-backs
python -m follow_tracker scan

# Only unfollow-since-last-snapshot
python -m follow_tracker watch
```

Without cookies, scan/watch/run exit with a clear message asking for `AUTH_TOKEN` and `CT0`.

## Outputs

| Path | Contents |
|------|----------|
| `out/non_followbacks_*.md` / `.csv` | Accounts you follow that do not follow back |
| `out/unfollows_*.md` / `.csv` | Accounts that unfollowed since the previous snapshot |
| `out/*_latest.*` | Most recent report copies |
| `data/following_*.json` | Snapshot of who you follow |
| `data/followers_*.json` | Snapshot of your followers |
| `data/*_latest.json` | Latest snapshot pointers used by `watch` |

First `watch`/`run` with no prior `data/` snapshot only saves a **baseline**. Run again later to see unfollows.

## Security notes

- Cookies act like a logged-in session. Treat them like a password.
- `.gitignore` excludes `.env`, `cookies.json`, `data/*`, and `out/*`.
- This tool never uses the official X API / MCP and does not need API credits.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| “Missing X session cookies” | Create `.env` from `.env.example` with real `AUTH_TOKEN` / `CT0` |
| Auth / 401-ish errors after a while | Re-copy cookies from the browser |
| `Couldn't get KEY_BYTE indices` | Run `python scripts/apply_twikit_patch.py` (Windows: `.\.venv\Scripts\python.exe scripts\apply_twikit_patch.py`). X changed a page format; twikit 2.3.3 needs this patch. |
| `KeyError: 'urls'` in `twikit/user.py` | Re-run the patch script (also patches `user.py`), or pull latest — runtime monkey-patch in `follow_tracker` hardens missing `entities.description.urls`. |
| `ModuleNotFoundError: twikit` | You used system `python` instead of the venv. On Windows: `.\.venv\Scripts\python.exe -m follow_tracker run` or `.\run.ps1`. |
| Rate limits / empty pages | Wait and re-run; the client pauses briefly between pages |
| Wrong account | `python -m follow_tracker config --set-username …` |

## License

Personal / local use. Unofficial client — use responsibly and within X’s terms.
