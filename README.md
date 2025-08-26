# Telemetry Analytics Dashboard for Smart Drilling Machines

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-v18+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

This project is developed for educational and demonstration purposes.


## 🏆 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- Maps powered by [OpenStreetMap](https://www.openstreetmap.org/) 
---

**Note:** This dashboard processes simulated telemetry data for July 2025 drilling sessions in the Berlin area. The data includes realistic patterns for demonstration of analytics capabilities.

A comprehensive web-based dashboard for analyzing telemetry data from smart devices ("Pods") retrofitted into drilling machines. The dashboard provides insights into drilling operations, battery status, GPS tracking, and Smart Tag detection for July 2025 drilling sessions in the Berlin area.

## 📋 System Requirements

### Required
- **Python 3.11+**: For the backend server
- **Node.js 18+**: For the frontend application

### Optional (Recommended)
- **Git**: For easy updates and contributing (alternative: download ZIP)

## 🛠️ Installation Guide

**First-time users:** Install the requirements below, then come back to the Quick Start section.

### Windows
1. **Python 3.11+**: Download from [python.org](https://python.org/downloads/)
   - ✅ **Important**: Check "Add Python to PATH" during installation
   - 🔄 **Restart your terminal** after installation
2. **Node.js 18+**: Download LTS from [nodejs.org](https://nodejs.org/en/download)
   - Use the Windows Installer (.msi)
   - 🔄 **Restart your terminal** after installation
3. **Git** (Optional): Download from [git-scm.com](https://git-scm.com/)

### macOS
**Option A (Recommended):**
```bash
# Install Homebrew first (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install requirements
brew install python@3.11 node git
```

**Option B:**
1. **Python**: Download from [python.org](https://python.org/downloads/macos/)
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/)
3. **Git**: Pre-installed or download from [git-scm.com](https://git-scm.com/)

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

## ✅ Verify Installation

**After installing the requirements above, verify everything works:**

**Windows (PowerShell):**
```powershell
python --version; node --version
```

**macOS/Linux:**
```bash
python3 --version && node --version
```

**Optional:**
```bash
git --version
```

**Expected output example:**
```
Python 3.11.x
v18.x.x
git version 2.x.x
```

If any command shows an error, the software isn't installed correctly.

## 🚀 Quick Start: try Analytics Dashboard for Smart Drilling Machines

A comprehensive web-based dashboard for analyzing telemetry data from smart devices ("Pods") retrofitted into drilling machines. The dashboard provides insights into drilling operations, battery status, GPS tracking, and Smart Tag detection for July 2025 drilling sessions in the Berlin area.

### Method A: Using Git (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pepperumo/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines.git
   cd Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines
   ```

### Method B: Download ZIP (No Git Required)

1. **Download ZIP file:**
   - Go to [GitHub repository](https://github.com/pepperumo/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines)
   - Click "Code" → "Download ZIP"
   - Extract to your desired location
   - Open terminal/command prompt in the extracted folder

### Continue Setup (Both Methods)

2. **Start Backend:**
   **Windows:**
   ```bash
   ./start-backend.bat
   ```

   **macOS/Linux:**
   ```bash
   ./start-backend.sh
   ```

3. **Start Frontend** (new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Open Dashboard:**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:5173
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Access Points:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- API Documentation: `http://localhost:8000/docs`

## 🔧 Troubleshooting

### Common Issues

**❌ "git is not recognized" or don't have Git**
- **Solution 1**: Download project as ZIP file (see Method B above)
- **Solution 2**: Install Git from [git-scm.com](https://git-scm.com/) for future convenience

**❌ "python is not recognized"**
- **Windows**: Reinstall Python with "Add to PATH" checked
- **macOS/Linux**: Use `python3` instead of `python`

**❌ "npm command not found"**
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Restart your terminal after installation

**❌ "Permission denied" errors**
- **Windows**: Run terminal as Administrator
- **macOS/Linux**: Use `sudo` for system-wide installations

**❌ Port already in use**
```bash
# Kill processes on ports 8000 and 5173
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux  
lsof -ti:8000 | xargs kill
```

**❌ Virtual environment issues**
```bash
# Delete and recreate venv
rm -rf venv  # (macOS/Linux) or rmdir /s venv (Windows)
python -m venv venv
```

**Need help?** [Open an issue](https://github.com/pepperumo/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/issues)

## 📊 Features

### Core Analytics
- **Total drilling time** tracking with date range filtering
- **Session analytics** including count and average duration
- **Tagged vs untagged sessions** percentage analysis
- **Operating state distribution** (OFF/STANDBY/SPINNING/DRILLING)
- **Battery level monitoring** with low battery alerts
- **Interactive map** showing session locations in Berlin
- **Comprehensive anomaly detection**

## 🏗️ Architecture

```
📁 project-root/
├── 📁 backend/           # Python FastAPI backend
│   ├── 📁 app/
│   │   ├── 📁 api/       # REST API endpoints
│   │   ├── 📁 models/    # Pydantic data models
│   │   └── 📁 services/  # Data processing logic
│   ├── requirements.txt
│   └── main.py
├── 📁 frontend/          # React TypeScript frontend
│   ├── 📁 src/
│   │   ├── 📁 components/# Dashboard components
│   │   ├── 📁 services/  # API service layer
│   │   └── 📁 types/     # TypeScript interfaces
│   ├── package.json
│   └── tailwind.config.js
└── 📁 public/data/       # CSV data files
    └── raw_drilling_sessions.csv
```

## 🔧 Data Processing Pipeline

### Raw Data Structure
The system processes telemetry data captured every 30 seconds from retrofitted Pods with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | UTC time of measurement | 2025-07-15T10:30:00Z |
| `device_id` | Unique drilling machine identifier | device_001 |
| `seq` | Sequence number for detecting gaps | 1, 2, 3... |
| `current_amp` | RMS current draw in Amperes | 3.9 |
| `gps_lat/gps_lon` | Machine location (Berlin area) | 52.5200, 13.4050 |
| `battery_level` | Pod battery percentage | 85 |
| `ble_id` | Smart Tag BLE MAC address (if detected) | AA:BB:CC:DD:EE:FF |

### 1. Data Ingestion & Schema Enforcement
- **Input**: `raw_drilling_sessions.csv` in `public/data/`
- **Processing**: Type conversion and validation using pandas
- **Schema**: Enforced data types with proper categorical and numeric fields
- **Quality**: Missing value identification and forward-fill for battery levels

### 2. Operating State Classification
Current draw interpretation based on drilling machine behavior:

| Current Range | State | Description |
|---------------|-------|-------------|
| ≤ 0.5 A | OFF | Machine unplugged or completely off |
| 0.5 - 2.0 A | STANDBY | Plugged in, switch OFF |
| 2.0 - 4.5 A | SPIN | Motor ON, no load |
| > 4.5 A | DRILL | Under drilling load |

### 3. Session Segmentation
Sessions are defined as continuous telemetry sequences with specific break conditions:
- **Session Break**: Time gap > 30 seconds (telemetry sampling interval)
- **Session ID**: Combination of device_id + sequential session number
- **Tagged Sessions**: Any session containing non-empty `ble_id` values

### 4. Data Processing
- **Real-time Processing**: Sessions and states calculated on-the-fly from raw data
- **No Pre-computed Files**: Distance, speed, and bearing calculations are handled in the Jupyter notebook for analysis only
- **Memory Efficient**: Data processed directly from raw CSV without intermediate files
### 5. Anomaly Detection
The system automatically identifies:

| Anomaly Type | Condition | Impact |
|--------------|-----------|--------|
| **Short Sessions** | Duration < 5 minutes | Potential setup issues |
| **Missing Telemetry** | Sequence number gaps | Data transmission problems |
| **Missing GPS** | Null coordinates | Location tracking failures |
| **Low Battery** | Battery level < 20% | Device maintenance needed |

### 6. Data Output
The application works directly with:
- **raw_drilling_sessions.csv**: Original telemetry data (only file required)
- **Runtime Processing**: All analytics calculated on-demand from raw data

##  API Endpoints

### Core Analytics
- `GET /api/v1/insights` - Dashboard insights with optional date filtering
- `GET /api/v1/anomalies` - Anomaly detection results
- `GET /api/v1/sessions/timeline` - Session timeline data
- `GET /api/v1/battery/trends` - Battery level trends
- `GET /api/v1/devices` - Available device list
- `GET /api/v1/health` - API health check

### Query Parameters
- `start_date` (YYYY-MM-DD) - Filter start date
- `end_date` (YYYY-MM-DD) - Filter end date
- `device_id` - Filter by specific device

## 🎨 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pandas** - Data processing and analysis
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **React Leaflet** for mapping
- **Vite** for build tooling



## �📄 License

This project is developed for educational and demonstration purposes.

---

**Note:** This dashboard processes simulated telemetry data for July 2025 drilling sessions in the Berlin area. The data includes realistic patterns for demonstration of analytics capabilities.