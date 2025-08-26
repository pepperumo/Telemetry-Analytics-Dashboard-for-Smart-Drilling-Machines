# Telemetry Analytics Dashboard for Smart Drilling Machines

A comprehensive web-based dashboard for analyzing telemetry data from smart devices ("Pods") retrofitted into drilling machines. The dashboard provides insights into drilling operations, battery status, GPS tracking, and Smart Tag detection for July 2025 drilling sessions in the Berlin area.

## � Quick Start

### Prerequisites
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)

### Option 1: Using Startup Scripts
**Windows:**
```bash
./start-backend.bat
```

**Linux/Mac:**
```bash
./start-backend.sh
```

**Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Open Dashboard:**
Navigate to `http://localhost:5173`

### Option 2: Manual Setup

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

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

The backend will run at `http://localhost:8000` and the frontend at `http://localhost:5173`.

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

## 🔍 Troubleshooting

### Common Issues

**Backend not loading data:**
- Ensure `raw_drilling_sessions.csv` is in `public/data/` directory
- Check file permissions and paths in `data_processor.py`
- Verify Python dependencies: `pip install -r requirements.txt`

**Frontend connection errors:**
- Confirm backend is running on port 8000 (`python main.py`)
- Check CORS configuration in `main.py`
- Verify API endpoints in `frontend/src/services/api.ts`

**Map not displaying:**
- Ensure internet connection for tile loading
- Check leaflet CSS imports in React components
- Verify GPS coordinates are valid in data

**Development servers:**
- Backend: `http://localhost:8000` 
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs` (FastAPI auto-generated)

## � Data Processing Details

For detailed technical documentation on data processing, see the Jupyter notebook:
- **Location**: `public/notebooks/raw_data_analysis.ipynb`
- **Content**: Complete data processing pipeline with feature engineering
- **Sections**: Ingestion, validation, geospatial processing, session segmentation, and export
- **Note**: The notebook shows advanced processing (distance, speed, bearing) for analysis purposes, while the dashboard uses simplified real-time processing

## �📄 License

This project is developed for educational and demonstration purposes.

---

**Note:** This dashboard processes simulated telemetry data for July 2025 drilling sessions in the Berlin area. The data includes realistic patterns for demonstration of analytics capabilities.