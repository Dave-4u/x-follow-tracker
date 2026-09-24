@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating .venv ...
  python -m venv .venv
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  ".venv\Scripts\python.exe" scripts\apply_twikit_patch.py
)

if not exist ".env" (
  if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo Created .env from .env.example — edit AUTH_TOKEN and CT0, then re-run.
    exit /b 1
  )
  echo Missing .env. Add AUTH_TOKEN and CT0.
  exit /b 1
)

".venv\Scripts\python.exe" scripts\apply_twikit_patch.py >nul
".venv\Scripts\python.exe" -m follow_tracker run %*
