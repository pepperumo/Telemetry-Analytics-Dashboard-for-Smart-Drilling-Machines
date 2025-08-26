# ML Troubleshooting Guide

## Overview

This guide provides solutions for common issues encountered with the ML system in the Telemetry Analytics Dashboard. Use this guide to diagnose and resolve ML-related problems quickly.

## Common Issues and Solutions

### ML Service Not Available

#### Symptoms
- `/api/ml/health` returns 503 or connection error
- Frontend shows "ML features unavailable"
- ML components fail to load

#### Diagnosis
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check ML system specifically
curl http://localhost:8000/api/ml/health

# Check backend logs
tail -f backend/logs/app.log
```

#### Solutions

**1. ML Service Not Initialized**
```bash
# Check if ML is enabled in environment
grep ML_ENABLED backend/.env

# If missing, add to .env file
echo "ML_ENABLED=true" >> backend/.env

# Restart backend
cd backend
python main.py
```

**2. Missing Dependencies**
```bash
# Verify ML packages are installed
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip list | grep -E "(pandas|sklearn|numpy|joblib)"

# If missing, reinstall requirements
pip install -r requirements.txt
```

**3. Configuration Issues**
```bash
# Check ML configuration
cat backend/.env | grep ML_

# Reset to defaults if needed
cat > backend/.env << 'EOF'
ML_ENABLED=true
ML_MODEL_PATH=models/
ML_CACHE_SIZE=1000
ML_PREDICTION_CACHE_TTL=300
EOF
```

### Health Scores Not Calculating

#### Symptoms
- `/api/ml/health-scores` returns empty array
- Health scores show as 0 or null
- "Insufficient data" errors

#### Diagnosis
```bash
# Check available data
curl "http://localhost:8000/api/v1/devices"

# Check if telemetry data exists
ls -la public/data/raw_drilling_sessions.csv

# Test specific device
curl "http://localhost:8000/api/ml/health-scores?device_ids=device_001"
```

#### Solutions

**1. Insufficient Telemetry Data**
```bash
# Check data file size and content
wc -l public/data/raw_drilling_sessions.csv
head -5 public/data/raw_drilling_sessions.csv

# Verify data format
python -c "
import pandas as pd
df = pd.read_csv('public/data/raw_drilling_sessions.csv')
print(f'Rows: {len(df)}, Columns: {df.columns.tolist()}')
print(f'Unique devices: {df.device_id.unique()}')
"
```

**2. Data Processing Errors**
```bash
# Check for data processing errors in logs
grep -i "error\|exception" backend/logs/app.log

# Test data processor manually
cd backend
python -c "
from app.services.data_processor import DataProcessor
dp = DataProcessor()
print('DataProcessor initialized successfully')
"
```

**3. Feature Engineering Issues**
```bash
# Check if ML service can process data
cd backend
python -c "
from app.ml.services import MLService
ml = MLService()
print('MLService initialized successfully')
"
```

### Model Training Failures

#### Symptoms
- POST `/api/ml/train` returns error
- Model status shows "not_trained"
- Training never completes

#### Diagnosis
```bash
# Check model status
curl http://localhost:8000/api/ml/model-status

# Check training logs
grep -i "train\|model" backend/logs/app.log

# Verify model directory exists
ls -la backend/models/
```

#### Solutions

**1. Insufficient Training Data**
```bash
# Check data availability for training
python -c "
import pandas as pd
df = pd.read_csv('public/data/raw_drilling_sessions.csv')
device_counts = df.groupby('device_id').size()
print('Records per device:')
print(device_counts)
if any(device_counts < 100):
    print('WARNING: Some devices have < 100 records')
"
```

**2. Model Directory Issues**
```bash
# Create model directory if missing
mkdir -p backend/models
chmod 755 backend/models

# Check disk space
df -h backend/models
```

**3. Memory Issues**
```bash
# Check available memory
free -h  # Linux/macOS
# For Windows: Task Manager > Performance > Memory

# Reduce memory usage if needed
echo "ML_BATCH_SIZE=50" >> backend/.env
echo "ML_MEMORY_LIMIT_GB=1" >> backend/.env
```

### Poor Model Performance

#### Symptoms
- Health scores seem inaccurate
- Model R² score < 0.5
- High prediction errors

#### Diagnosis
```bash
# Check model performance metrics
curl http://localhost:8000/api/ml/model-status | jq .performance_metrics

# Check data quality
curl http://localhost:8000/api/ml/statistics | jq .model_stats
```

#### Solutions

**1. Data Quality Issues**
```bash
# Analyze data quality
python -c "
import pandas as pd
df = pd.read_csv('public/data/raw_drilling_sessions.csv')
print('Missing values:')
print(df.isnull().sum())
print('Data types:')
print(df.dtypes)
"
```

**2. Retrain with More Data**
```bash
# Trigger full retraining
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "retrain_type": "full",
    "validation_split": 0.3
  }'
```

**3. Adjust Model Parameters**
```bash
# Update model configuration
echo "ML_MODEL_PARAMS='{\"n_estimators\":200,\"max_depth\":15}'" >> backend/.env
```

### Alert Generation Issues

#### Symptoms
- No alerts generated despite low health scores
- Too many false positive alerts
- Alerts not acknowledged properly

#### Diagnosis
```bash
# Check alert generation
curl "http://localhost:8000/api/ml/alerts?status=active"

# Check alert thresholds
grep ALERT backend/.env

# Check alert history
curl "http://localhost:8000/api/ml/alerts?per_page=50"
```

#### Solutions

**1. Adjust Alert Thresholds**
```bash
# Lower thresholds for more alerts
echo "ML_ALERT_THRESHOLD_HIGH=40" >> backend/.env
echo "ML_ALERT_THRESHOLD_CRITICAL=20" >> backend/.env

# Restart backend to apply changes
```

**2. Alert Cooldown Issues**
```bash
# Check cooldown period
grep COOLDOWN backend/.env

# Reduce cooldown if needed
echo "ML_ALERT_COOLDOWN_HOURS=2" >> backend/.env
```

**3. Alert Acknowledgment Problems**
```bash
# Test alert acknowledgment
curl -X POST "http://localhost:8000/api/ml/alerts/test_alert_001/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "test_user", "notes": "Testing acknowledgment"}'
```

### Performance Issues

#### Symptoms
- ML endpoints respond slowly (>5 seconds)
- High CPU/memory usage
- Dashboard becomes unresponsive

#### Diagnosis
```bash
# Check ML performance statistics
curl http://localhost:8000/api/ml/statistics | jq .processing_stats

# Monitor system resources
top -p $(pgrep -f "python main.py")  # Linux/macOS
# Windows: Task Manager > Details > python.exe
```

#### Solutions

**1. Enable Caching**
```bash
# Increase cache size and TTL
echo "ML_CACHE_SIZE=2000" >> backend/.env
echo "ML_PREDICTION_CACHE_TTL=600" >> backend/.env
```

**2. Optimize Batch Processing**
```bash
# Reduce batch size for lower memory usage
echo "ML_BATCH_SIZE=25" >> backend/.env

# Enable multiprocessing if CPU cores available
echo "ML_MAX_WORKERS=4" >> backend/.env
```

**3. Background Processing**
```bash
# Ensure ML processing runs in background
echo "ML_ENABLE_BACKGROUND_TASKS=true" >> backend/.env
```

### Integration Test Failures

#### Symptoms
- ML integration tests fail
- Performance benchmarks timeout
- API endpoints return unexpected responses

#### Diagnosis
```bash
# Run ML-specific tests
cd backend
python -m pytest tests/integration/ml/ -v

# Check test output for specific failures
python -m pytest tests/integration/ml/test_ml_api_integration.py::test_health_scores_endpoint -v
```

#### Solutions

**1. Test Environment Setup**
```bash
# Ensure test environment is properly configured
export ML_ENABLED=true
export ML_TEST_MODE=true

# Run tests with verbose output
python -m pytest tests/integration/ml/ -v -s
```

**2. Performance Test Adjustments**
```bash
# If performance tests timeout, check current performance
curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8000/api/ml/health-scores

# Adjust timeout if needed (in test files)
# Or optimize performance using cache settings above
```

**3. Mock Data for Tests**
```bash
# Verify test data exists
ls -la tests/data/

# If missing, tests may need sample data
# Check test setup in conftest.py
```

### Frontend Integration Issues

#### Symptoms
- ML components don't display
- "Loading..." state persists
- JavaScript console errors

#### Diagnosis
```bash
# Check browser console for errors
# Open Developer Tools > Console

# Test ML API from browser
# Open Developer Tools > Network tab
# Filter by "ml" to see ML API requests
```

#### Solutions

**1. API Endpoint Issues**
```javascript
// Test ML API directly in browser console
fetch('/api/ml/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**2. CORS Issues**
```bash
# Check if CORS is properly configured
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/ml/health
```

**3. Frontend Build Issues**
```bash
# Rebuild frontend with ML components
cd frontend
npm run build
npm run dev
```

## Diagnostic Commands

### Quick Health Check
```bash
#!/bin/bash
echo "=== ML System Health Check ==="

echo "1. Backend status:"
curl -s http://localhost:8000/api/v1/health | jq .status

echo "2. ML system status:"
curl -s http://localhost:8000/api/ml/health | jq .status

echo "3. Available devices:"
curl -s http://localhost:8000/api/v1/devices | jq '.devices | length'

echo "4. Health scores available:"
curl -s http://localhost:8000/api/ml/health-scores | jq '.health_scores | length'

echo "5. Model status:"
curl -s http://localhost:8000/api/ml/model-status | jq .is_trained

echo "6. Active alerts:"
curl -s "http://localhost:8000/api/ml/alerts?status=active" | jq '.alerts | length'

echo "=== Health Check Complete ==="
```

### Performance Check
```bash
#!/bin/bash
echo "=== ML Performance Check ==="

echo "1. ML statistics:"
curl -s http://localhost:8000/api/ml/statistics | jq .processing_stats

echo "2. Response time test:"
time curl -s http://localhost:8000/api/ml/health-scores > /dev/null

echo "3. Memory usage:"
ps aux | grep "python main.py" | grep -v grep

echo "=== Performance Check Complete ==="
```

### Configuration Check
```bash
#!/bin/bash
echo "=== ML Configuration Check ==="

echo "1. Environment variables:"
grep ML_ backend/.env

echo "2. Model directory:"
ls -la backend/models/

echo "3. Data availability:"
wc -l public/data/raw_drilling_sessions.csv

echo "4. Python packages:"
cd backend && source venv/bin/activate && pip list | grep -E "(pandas|sklearn|numpy|joblib)"

echo "=== Configuration Check Complete ==="
```

## Getting Help

### Log Analysis
```bash
# View recent ML-related logs
tail -50 backend/logs/app.log | grep -i "ml\|health\|alert"

# Search for specific errors
grep -i "error\|exception\|traceback" backend/logs/app.log | tail -10
```

### System Information
```bash
# Python version and packages
python --version
pip list | grep -E "(fastapi|pandas|sklearn|numpy)"

# System resources
free -h  # Linux/macOS
df -h .  # Disk space
```

### Contact and Support
- **Check logs first**: Most issues are logged in `backend/logs/app.log`
- **Test with curl**: Use the diagnostic commands above to isolate issues
- **GitHub Issues**: Report bugs with log output and system information
- **Documentation**: Refer to [ML User Guide](ml-user-guide.md) and [ML Operations Guide](ml-operations.md)

### Emergency Procedures

#### Disable ML System
```bash
# If ML system causes issues, disable it temporarily
echo "ML_ENABLED=false" >> backend/.env

# Restart backend - dashboard will work without ML features
cd backend
python main.py
```

#### Reset ML System
```bash
# Clear all ML data and restart fresh
rm -rf backend/models/*
rm -rf data/ml/cache/*

# Reset configuration to defaults
grep -v ML_ backend/.env > temp.env && mv temp.env backend/.env
echo "ML_ENABLED=true" >> backend/.env

# Restart and retrain
cd backend
python main.py

# Trigger training
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{"retrain_type": "full"}'
```

This troubleshooting guide covers the most common ML system issues. For complex problems, combine multiple diagnostic approaches and check the comprehensive logs for detailed error information.