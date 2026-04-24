# Bootstrap Python dependencies for the project.

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Bootstrapping project dependencies..."
Write-Host "Using the currently active Python environment."

python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip. Please check the active Python environment."
}

python -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install project dependencies. Please check network access or package index settings."
}

Write-Host "Dependency installation completed. You can now start the server with:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1" -ForegroundColor Cyan
