# 🏊‍♂️ AI Biomechanical Swimming Analysis Platform

> **Offline-first computer vision system for quantitative stroke analysis and coaching feedback.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-cyan)](https://reactjs.org/)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-green)](https://github.com/ultralytics/ultralytics)
[![MediaPipe](https://img.shields.io/badge/Model-MediaPipe_BlazePose-orange)](https://developers.google.com/mediapipe)

## 📖 Overview

This platform provides **elite-level biomechanical analysis** for swimming coaches and athletes without requiring expensive hardware or internet connectivity. By leveraging state-of-the-art computer vision, it transforms standard training footage into actionable performance metrics.

The system processes video data locally to ensure **data privacy** and instant feedback, making it ideal for pool-side deployment.

---

## ✨ Key Features

- **Multi-Stroke Support**: Validated analysis for Freestyle, Backstroke, Breaststroke, and Butterfly.
- **Precision Kinematics**:
  - 📐 **Joint Angles**: Elbow, shoulder, and knee flexion validation.
  - ⚖️ **Symmetry Analysis**: Left vs. Right side power balance.
  - 🔄 **Body Roll**: Rotation mechanics quantification.
- **Performance Metrics**:
  - Stroke Rate (SPM) & Velocity tracking.
  - Phase Detection (Catch, Pull, Push, Recovery).
- **Interactive Reports**:
  - Dynamic dashboards with skeletal overlays.
  - Exportable PDF summaries for athlete portfolios.
- **Offline Capable**: Zero dependency on cloud APIs—run it on a laptop at the pool.

---

## 🛠️ Technical Architecture

### **Frontend** (React + Vite)
- Real-time video canvas with skeletal overlays.
- `Plotly.js` for manufacturing-grade kinematic graphs.
- WebSocket integration for live processing bars.

### **Backend** (Python + Flask)
- **Computer Vision Pipeline**:
  1.  **Detection**: `YOLOv8` for swimmer localization (ROI cropping).
  2.  **Pose Estimation**: `MediaPipe BlazePose` for 33-point skeletal tracking.
  3.  **Analytics**: `NumPy`/`SciPy` for signal processing and angle computation.
- **Database**: `MongoDB` for storing structured biomechanical data.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11** or **3.12** (⚠️ *Python 3.13 is currently incompatible with MediaPipe*)
- **Node.js 18+**
- **MongoDB** (Local instance running on port 27017)

### Installation

#### 1. Backend Setup
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
```

#### 2. Frontend Setup
```powershell
cd frontend
npm install
cd ..
```

### Running the Application

**Option 1: One-Click Script (Recommended)**
```powershell
.\start_backend.ps1
# Open a new terminal for frontend
.\start_frontend.ps1
```

**Option 2: Manual Start**
```powershell
# Backend
python -m app.main --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev
```

Visit the app at **`http://localhost:5173`**.

---

## 📊 Accuracy & Validation

System performance has been benchmarked against manual annotation:

| Metric | Accuracy / Latency |
|--------|-------------------|
| **Swimmer Detection** | **85-90%** (Clear Water) |
| **Pose Estimation** | **96.4%** PCK@0.2 |
| **Processing Speed** | **20-30 FPS** (CPU Only) |

*For detailed validation methodology, see [`backend/docs/VALIDATION.md`](./backend/docs/VALIDATION.md).*

---

## 📂 Documentation

- **[System Workflow](./backend/docs/SYSTEM_WORKFLOW.md)**: End-to-end data flow diagram.
- **[Validation Report](./backend/docs/VALIDATION.md)**: Accuracy findings and testing protocols.
