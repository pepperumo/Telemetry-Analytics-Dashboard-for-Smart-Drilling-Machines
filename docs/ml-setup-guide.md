# ML System Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the Machine Learning (ML) system for the Telemetry Analytics Dashboard. The ML system provides equipment health scoring, predictive maintenance alerts, and intelligent insights.

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for models and data
- **CPU**: Multi-core processor (ML training benefits from additional cores)

### Dependencies

- **FastAPI**: Web framework (already included)
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning algorithms
- **NumPy**: Numerical computing
- **Joblib**: Model serialization

## Installation

### 1. Backend Environment Setup

If you haven't already set up the backend environment:

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate
```

### 2. Install ML Dependencies

```bash
# Install all dependencies including ML packages
pip install -r requirements.txt
```

### 3. Verify ML Dependencies

Check that key ML packages are installed:

```bash
python -c "import pandas, numpy, sklearn, joblib; print('ML dependencies OK')"
```

## Initial Configuration

### 1. Environment Variables

Create or update your `.env` file in the backend directory:

```env
# ML Configuration
ML_ENABLED=true
ML_MODEL_PATH=models/
ML_CACHE_SIZE=1000
ML_PREDICTION_CACHE_TTL=300

# Optional: ML Performance Settings
ML_BATCH_SIZE=100
ML_MAX_WORKERS=4
ML_MEMORY_LIMIT_GB=2

# Optional: Alert Settings
ML_ALERT_THRESHOLD_HIGH=30
ML_ALERT_THRESHOLD_CRITICAL=15
ML_ALERT_COOLDOWN_HOURS=6
```

### 2. Create Model Directory

```bash
mkdir -p backend/models
mkdir -p backend/data/cache
```

### 3. Verify Configuration

Start the backend and check ML system status:

```bash
# Start backend
cd backend
python main.py

# In another terminal, test ML health
curl http://localhost:8000/api/ml/health
```

Expected response:
```json
{
  "status": "healthy",
  "ml_enabled": true,
  "services": {
    "feature_engineering": "ready",
    "health_scoring": "ready", 
    "predictive_alerts": "ready",
    "model_manager": "ready"
  }
}
```

## Data Setup

### 1. Training Data Requirements

The ML system needs historical telemetry data for training. Ensure you have:

- **Minimum 500 data points** for initial training
- **Multiple devices** for better generalization
- **Time-series data** spanning at least 1 week
- **Complete sensor readings** (GPS, current, battery, temperature)

### 2. Data Validation

Verify your data format matches expected schema:

```bash
cd backend
python -c "
from app.services.data_processor import DataProcessor
processor = DataProcessor()
print('Data processor ready')
"
```

### 3. Initial Data Processing

Process existing data for ML training:

```bash
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "retrain_type": "full",
    "data_start_date": "2025-08-01",
    "data_end_date": "2025-08-26",
    "validation_split": 0.2
  }'
```

## Model Training

### 1. Automatic Training

The system can automatically train models when sufficient data is available:

```python
# This happens automatically on startup if data is available
# Check training status:
curl http://localhost:8000/api/ml/model-status
```

### 2. Manual Training Trigger

Force model training with specific parameters:

```bash
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "retrain_type": "incremental",
    "model_version": "v1.1.0",
    "validation_split": 0.25
  }'
```

### 3. Training Monitoring

Monitor training progress:

```bash
# Check model status
curl http://localhost:8000/api/ml/model-status

# View training statistics
curl http://localhost:8000/api/ml/statistics
```

## Testing the Installation

### 1. Basic Functionality Test

```bash
# Test health scores
curl "http://localhost:8000/api/ml/health-scores?page_size=5"

# Test alerts
curl "http://localhost:8000/api/ml/alerts?per_page=5"

# Test system health
curl "http://localhost:8000/api/ml/health"
```

### 2. Integration Test

Run the ML integration tests:

```bash
cd backend
python -m pytest tests/integration/ml/ -v
```

Expected output:
```
tests/integration/ml/test_ml_api_integration.py::test_health_scores_endpoint PASSED
tests/integration/ml/test_ml_api_integration.py::test_alerts_endpoint PASSED
tests/integration/ml/test_ml_api_integration.py::test_model_status_endpoint PASSED
tests/integration/ml/test_performance_benchmarks.py::test_ml_health_endpoint_performance PASSED
```

### 3. Frontend Integration

Start the frontend and verify ML features appear:

```bash
cd frontend
npm run dev
```

Navigate to:
- **Health Dashboard**: Check for health score displays
- **Alerts Panel**: Verify predictive alerts appear
- **Device Details**: Confirm ML insights are shown

## Performance Optimization

### 1. Memory Optimization

For systems with limited memory:

```env
# In .env file
ML_CACHE_SIZE=500
ML_BATCH_SIZE=50
ML_MEMORY_LIMIT_GB=1
```

### 2. CPU Optimization

For faster processing:

```env
# Use more workers (up to CPU core count)
ML_MAX_WORKERS=8
ML_ENABLE_MULTIPROCESSING=true
```

### 3. Storage Optimization

Configure model storage:

```env
# Compress models to save space
ML_COMPRESS_MODELS=true
ML_MODEL_CLEANUP_DAYS=30
```

## Monitoring and Maintenance

### 1. Health Monitoring

Set up regular health checks:

```bash
# Create monitoring script
cat > monitor_ml.sh << 'EOF'
#!/bin/bash
response=$(curl -s http://localhost:8000/api/ml/health)
status=$(echo $response | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$status" != "healthy" ]; then
    echo "ML system unhealthy: $response"
    # Add notification logic here
fi
EOF

chmod +x monitor_ml.sh
```

### 2. Performance Monitoring

Check system statistics regularly:

```bash
curl http://localhost:8000/api/ml/statistics | jq .
```

Monitor key metrics:
- **Error rate** (should be < 5%)
- **Processing time** (should be < 500ms)
- **Cache hit rate** (should be > 80%)
- **Memory usage** (should be within limits)

### 3. Model Maintenance

Regular model updates:

```bash
# Weekly model retrain (automate with cron)
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{"retrain_type": "incremental"}'
```

## Troubleshooting

### Common Issues

#### ML Service Not Available
```bash
# Check if ML is enabled
grep ML_ENABLED backend/.env

# Verify dependencies
pip list | grep -E "(pandas|sklearn|numpy)"

# Check logs
tail -f backend/logs/app.log
```

#### Model Training Fails
```bash
# Check data availability
curl "http://localhost:8000/api/dashboard/devices?include_telemetry=true"

# Verify data format
python -c "
from app.services.data_processor import DataProcessor
dp = DataProcessor()
print('Data processor can initialize')
"
```

#### Poor Model Performance
```bash
# Check model metrics
curl http://localhost:8000/api/ml/model-status | jq .performance_metrics

# Retrain with more data
curl -X POST http://localhost:8000/api/ml/train \
  -d '{"retrain_type": "full", "validation_split": 0.3}'
```

#### High Memory Usage
```bash
# Reduce cache size
echo "ML_CACHE_SIZE=200" >> backend/.env

# Reduce batch size
echo "ML_BATCH_SIZE=25" >> backend/.env

# Restart service
```

### Diagnostic Commands

```bash
# Check ML system status
curl http://localhost:8000/api/ml/health

# View detailed statistics
curl http://localhost:8000/api/ml/statistics

# Test specific device predictions
curl "http://localhost:8000/api/ml/health-scores?device_ids=device_001"

# Check model information
curl http://localhost:8000/api/ml/model-status
```

## Advanced Configuration

### 1. Custom Model Parameters

```env
# Feature Engineering
ML_FEATURE_WINDOW_SIZE=50
ML_FEATURE_AGGREGATION_METHODS=mean,std,trend

# Model Training
ML_MODEL_TYPE=random_forest
ML_MODEL_PARAMS='{"n_estimators":100,"max_depth":10}'
ML_CROSS_VALIDATION_FOLDS=5

# Alert Generation
ML_ALERT_LOOKBACK_HOURS=24
ML_ALERT_PREDICTION_HORIZON_HOURS=72
```

### 2. Integration with External Systems

```env
# Notification endpoints
ML_WEBHOOK_URL=https://your-monitoring-system.com/webhook
ML_ALERT_NOTIFICATION_ENABLED=true

# External data sources
ML_EXTERNAL_DATA_SOURCE=enabled
ML_WEATHER_API_KEY=your_api_key
```

### 3. Security Configuration

```env
# API Security
ML_API_KEY_REQUIRED=true
ML_RATE_LIMIT_ENABLED=true
ML_IP_WHITELIST=192.168.1.0/24,10.0.0.0/8

# Data Security
ML_ENCRYPT_MODELS=true
ML_AUDIT_PREDICTIONS=true
```

## Next Steps

After successful setup:

1. **Read the [ML User Guide](ml-user-guide.md)** to understand how to use ML features
2. **Check the [ML Operations Guide](ml-operations.md)** for ongoing management
3. **Review the [ML API Reference](ml-api-reference.md)** for integration details
4. **Set up monitoring** using the provided scripts
5. **Schedule regular model retraining** for optimal performance

## Support

For additional help:

- **Check logs**: `backend/logs/app.log` and `backend/logs/ml.log`
- **Review test failures**: Run `pytest tests/integration/ml/ -v` for detailed output
- **Monitor health**: Use `/api/ml/health` endpoint for system status
- **Performance metrics**: Use `/api/ml/statistics` for detailed performance data

The ML system is designed to be robust and self-monitoring. Regular health checks and periodic retraining will ensure optimal performance for your drilling equipment analytics.