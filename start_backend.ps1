# Backend startup script for Windows PowerShell
# Activate virtual environment and start Flask server

Write-Host "Starting Backend Server..." -ForegroundColor Green

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Navigate to backend directory
Set-Location backend

# Start Flask server
python -m app.main --host 0.0.0.0 --port 8000


