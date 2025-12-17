# How to Run the Swimming Biomechanics Platform

## Quick Start Guide

### Method 1: Using PowerShell Scripts (Easiest)

**Step 1: Open PowerShell in the project root directory**
```powershell
cd "E:\ai swimming project"
```

**Step 2: Start Backend Server**
Open a **new PowerShell window** and run:
```powershell
cd "E:\ai swimming project"
.\start_backend.ps1
```

**Step 3: Start Frontend Server**
Open **another new PowerShell window** and run:
```powershell
cd "E:\ai swimming project"
.\start_frontend.ps1
```

---

### Method 2: Manual Startup (Step-by-Step)

#### Backend Server Setup

**Step 1: Open PowerShell Terminal 1**
```powershell
# Navigate to project root
cd "E:\ai swimming project"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend directory
cd backend

# Start Flask server
python -m app.main --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:8000
```

#### Frontend Server Setup

**Step 2: Open PowerShell Terminal 2** (keep Terminal 1 running)
```powershell
# Navigate to project root
cd "E:\ai swimming project"

# Navigate to frontend directory
cd frontend

# Start Vite dev server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### Method 3: Using PowerShell Background Jobs

Run both servers in the background from one terminal:

```powershell
cd "E:\ai swimming project"

# Start Backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location "E:\ai swimming project\backend"
    & "E:\ai swimming project\.venv\Scripts\python.exe" -m app.main --host 0.0.0.0 --port 8000
}

# Start Frontend
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "E:\ai swimming project\frontend"
    npm run dev
}

# Check status
Get-Job

# View output
Receive-Job -Id $backendJob.Id
Receive-Job -Id $frontendJob.Id

# Stop servers
Stop-Job -Id $backendJob.Id, $frontendJob.Id
Remove-Job -Id $backendJob.Id, $frontendJob.Id
```

---

## Prerequisites Check

Before running, ensure:

### 1. MongoDB is Running
```powershell
# Check if MongoDB service is running
Get-Service MongoDB

# If not running, start it:
Start-Service MongoDB

# Or start manually:
mongod --dbpath "C:\path\to\mongodb\data"
```

### 2. Virtual Environment is Activated
```powershell
# Check if venv is activated (you should see (.venv) in prompt)
# If not:
.\.venv\Scripts\Activate.ps1
```

### 3. Dependencies are Installed
```powershell
# Backend dependencies (if not already installed)
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Frontend dependencies (if not already installed)
cd frontend
npm install
cd ..
```

---

## Access the Application

Once both servers are running:

- **Frontend UI**: Open your browser and go to **http://localhost:5173**
- **Backend API**: Available at **http://localhost:8000**
- **Health Check**: **http://localhost:8000/healthz**

---

## Troubleshooting

### Backend Won't Start

**Issue: MongoDB Connection Error**
```
Solution: Ensure MongoDB is running on localhost:27017
```

**Issue: Port 8000 Already in Use**
```powershell
# Use a different port
python -m app.main --host 0.0.0.0 --port 8001
```

**Issue: Import Errors**
```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies if needed
pip install -r backend/requirements.txt
```

### Frontend Won't Start

**Issue: Port 5173 Already in Use**
```
Vite will automatically use the next available port (5174, 5175, etc.)
Check the terminal output for the actual port.
```

**Issue: npm install errors**
```powershell
# Clear cache and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install
```

### Both Servers Running But Can't Access

1. **Check Firewall**: Ensure ports 8000 and 5173 are not blocked
2. **Check Browser**: Try a different browser or clear cache
3. **Check URLs**: Make sure you're using `http://localhost:5173` (not https)

---

## Stopping the Servers

### If using separate terminals:
- Press `Ctrl + C` in each terminal window

### If using background jobs:
```powershell
Get-Job | Stop-Job
Get-Job | Remove-Job
```

### If using PowerShell scripts:
- Close the PowerShell windows or press `Ctrl + C`

---

## Development Workflow

1. **Start MongoDB** (if not running as service)
2. **Start Backend** (Terminal 1)
3. **Start Frontend** (Terminal 2)
4. **Open Browser** → http://localhost:5173
5. **Make Changes** → Frontend auto-reloads, Backend may need restart
6. **Stop Servers** → `Ctrl + C` when done

---

## Quick Reference

| Component | Command | Port | URL |
|-----------|---------|------|-----|
| Backend | `python -m app.main` | 8000 | http://localhost:8000 |
| Frontend | `npm run dev` | 5173 | http://localhost:5173 |
| MongoDB | `mongod` | 27017 | mongodb://localhost:27017 |

---

## Need Help?

- Check server output in PowerShell windows for error messages
- Verify MongoDB is running: `Get-Service MongoDB`
- Check if ports are in use: `netstat -ano | findstr ":8000 :5173"`
- Review logs in the terminal windows where servers are running

