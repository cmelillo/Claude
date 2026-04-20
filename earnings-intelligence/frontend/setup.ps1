# Setup script for Windows PowerShell
# Run this once to install npm dependencies

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
npm install
Write-Host "`nSetup complete! Run .\start.ps1 to launch the frontend." -ForegroundColor Green
