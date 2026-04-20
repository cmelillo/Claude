# Setup script for Windows PowerShell
# Run this once to create the virtual environment and install dependencies

Write-Host "Setting up Earnings Intelligence backend..." -ForegroundColor Cyan

# Create virtual environment
python -m venv venv
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create venv. Is Python 3.10+ installed?"; exit 1 }

# Activate and install
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy env template if .env doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "`n.env created. Edit it and add your ANTHROPIC_API_KEY." -ForegroundColor Yellow
}

Write-Host "`nSetup complete! Run .\start.ps1 to launch the backend." -ForegroundColor Green
