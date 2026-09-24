# Run X follow-tracker with the project venv (Windows PowerShell).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating .venv ..."
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    & .\.venv\Scripts\python.exe scripts\apply_twikit_patch.py
}

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env from .env.example — edit AUTH_TOKEN and CT0, then re-run."
        exit 1
    }
    Write-Host "Missing .env (and no .env.example). Add AUTH_TOKEN and CT0."
    exit 1
}

& .\.venv\Scripts\python.exe scripts\apply_twikit_patch.py | Out-Null
& .\.venv\Scripts\python.exe -m follow_tracker run @args
