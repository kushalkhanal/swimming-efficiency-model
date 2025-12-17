# Offline Swim Biomechanics Platform

This repository contains a full-stack project skeleton for an offline, open-source swimming biomechanics analysis platform using React and Flask.

## Structure

```
.
├── backend/   # Flask service for video processing & analytics
└── frontend/  # React SPA for video playback and metric visualization
```

Refer to `backend/README.md` and the inline module docstrings for details on each component.

## Quick Start

### Prerequisites

- Python 3.11 or 3.12 (Python 3.13 has MediaPipe compatibility issues - see `MEDIAPIPE_NOTE.md`)
- Node.js 18+ and npm
- MongoDB (running locally on default port 27017)

### Installation

1. **Backend Setup:**
   ```powershell
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   .\.venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r backend/requirements.txt
   
   # Note: MediaPipe may not install on Python 3.13 - see MEDIAPIPE_NOTE.md
   ```

2. **Frontend Setup:**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

**Option 1: Use the provided scripts (Windows PowerShell)**

```powershell
# Terminal 1 - Backend
.\start_backend.ps1

# Terminal 2 - Frontend  
.\start_frontend.ps1
```

**Option 2: Manual startup**

```powershell
# Terminal 1 - Backend
.\.venv\Scripts\Activate.ps1
cd backend
python -m app.main --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:5173 (Vite default port)
- **Backend API:** http://localhost:8000

### Important Notes

- **MongoDB:** Ensure MongoDB is running locally before starting the backend
- **MediaPipe:** See `MEDIAPIPE_NOTE.md` for Python 3.13 compatibility information
- **Data Directories:** The application will create `data/uploads` and `data/artifacts` automatically

