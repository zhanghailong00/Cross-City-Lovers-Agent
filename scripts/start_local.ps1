# Local startup script for the project.

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Checking local secret config..."
if (-not (Test-Path "config/secrets.toml")) {
    Write-Host "config/secrets.toml not found, creating from template..."
    Copy-Item "config/secrets.example.toml" "config/secrets.toml"
}

Write-Host "Checking runtime dependencies..."
$uvicornCheck = python -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('uvicorn') else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "The current Python environment does not have uvicorn." -ForegroundColor Yellow
    Write-Host "Please install project dependencies first:" -ForegroundColor Yellow
    Write-Host "python -m pip install -e ." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or run the bootstrap script:" -ForegroundColor Yellow
    Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_env.ps1" -ForegroundColor Cyan
    exit 1
}

Write-Host "Starting local dev server: http://127.0.0.1:8000"
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
