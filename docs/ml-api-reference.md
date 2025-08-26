# ML API Reference

## Overview

The ML API provides endpoints for accessing machine learning capabilities including health scores, predictive alerts, and model management. All endpoints follow RESTful conventions and return JSON responses.

**Base URL**: `http://localhost:8000/api/ml`

**Authentication**: Inherits authentication from main API (if configured)

**Content-Type**: `application/json`

## Endpoints Overview

| Method | Endpoint | Purpose | Response Model |
|--------|----------|---------|----------------|
| GET | `/health-scores` | Get equipment health scores | HealthScoresListResponse |
| GET | `/health` | Check ML system health | HealthCheckResponse |
| GET | `/alerts` | Get predictive maintenance alerts | AlertsListResponse |
| POST | `/alerts/{alert_id}/acknowledge` | Acknowledge an alert | AlertAcknowledgmentResponse |
| POST | `/alerts/{alert_id}/resolve` | Resolve an alert | AlertResolutionResponse |
| GET | `/model-status` | Get ML model information | ModelStatusResponse |
| POST | `/train` | Trigger model training | MLTrainingResponse |
| GET | `/statistics` | Get ML system statistics | StatisticsResponse |

## Health Scores API

### Get Health Scores

**Endpoint**: `GET /health-scores`

**Description**: Retrieve current health scores for all devices with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `device_ids` | string | No | Comma-separated device IDs | `device_001,device_002` |
| `min_health_score` | float | No | Minimum health score (0-100) | `70.0` |
| `max_health_score` | float | No | Maximum health score (0-100) | `90.0` |
| `risk_levels` | string | No | Comma-separated risk levels | `high,critical` |
| `start_date` | string | No | Start date (YYYY-MM-DD) | `2025-08-01` |
| `end_date` | string | No | End date (YYYY-MM-DD) | `2025-08-26` |
| `page` | integer | No | Page number (default: 1) | `2` |
| `page_size` | integer | No | Items per page (1-100, default: 20) | `50` |

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/ml/health-scores?device_ids=device_001&min_health_score=50&page=1&page_size=10"
```

#### Response

```json
{
  "success": true,
  "health_scores": [
    {
      "device_id": "7a3f55e1",
      "health_score": 55.9,
      "confidence_interval": [50.94, 60.94],
      "risk_level": "medium",
      "explanatory_factors": [
        {
          "feature": "Current Draw Stability",
          "impact": "negative",
          "importance": 0.4,
          "value": 64.5
        },
        {
          "feature": "Battery Performance", 
          "impact": "negative",
          "importance": 0.4,
          "value": 25.4
        },
        {
          "feature": "GPS Reliability",
          "impact": "positive", 
          "importance": 0.2,
          "value": 100.0
        }
      ],
      "calculated_at": "2025-08-26T10:30:00Z",
      "data_quality_score": 0.95
    }
  ],
  "summary": {
    "total_devices": 1,
    "average_health_score": 55.9,
    "at_risk_devices": 1,
    "critical_devices": 0
  },
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "total_items": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

#### Risk Level Values

| Risk Level | Health Score Range | Description |
|------------|-------------------|-------------|
| `low` | 80-100 | Excellent condition |
| `medium` | 50-79 | Requires monitoring |
| `high` | 30-49 | Maintenance recommended |
| `critical` | 0-29 | Immediate attention required |

## Alerts API

### Get Alerts

**Endpoint**: `GET /alerts`

**Description**: Retrieve predictive maintenance alerts with filtering and pagination.

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `device_id` | string | No | Filter by device ID | `device_001` |
| `severity` | string | No | Filter by severity level | `high` |
| `status` | string | No | Filter by alert status | `active` |
| `alert_type` | string | No | Filter by alert type | `maintenance` |
| `page` | integer | No | Page number (default: 1) | `1` |
| `per_page` | integer | No | Items per page (default: 50) | `20` |

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/ml/alerts?severity=high&status=active&per_page=10"
```

#### Response

```json
{
  "alerts": [
    {
      "alert_id": "alert_20250826_001",
      "device_id": "device_001", 
      "severity": "high",
      "alert_type": "maintenance",
      "status": "active",
      "predicted_issue": "Battery replacement needed",
      "predicted_timeframe": "48-72 hours",
      "confidence": 0.87,
      "recommended_actions": [
        "Schedule battery replacement",
        "Monitor charging patterns",
        "Check current consumption trends"
      ],
      "health_context": {
        "current_health_score": 45.2,
        "trend": "declining",
        "previous_scores": [52.1, 48.7, 46.3, 45.2]
      },
      "created_at": "2025-08-26T12:00:00Z",
      "acknowledged_at": null,
      "resolved_at": null
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 10,
  "has_next": false
}
```

#### Severity Levels

| Severity | Description | Recommended Action Time |
|----------|-------------|------------------------|
| `low` | Informational | Monitor during routine maintenance |
| `medium` | Attention needed | Plan maintenance within 1-2 weeks |
| `high` | Action required | Schedule maintenance within 48-72 hours |
| `critical` | Immediate action | Address within 24 hours |

#### Alert Status Values

| Status | Description |
|--------|-------------|
| `active` | Alert is open and requires attention |
| `acknowledged` | Alert has been seen but not resolved |
| `resolved` | Alert has been addressed |
| `suppressed` | Alert has been manually suppressed |

### Acknowledge Alert

**Endpoint**: `POST /alerts/{alert_id}/acknowledge`

**Description**: Mark an alert as acknowledged by an operator.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique alert identifier |

#### Request Body

```json
{
  "acknowledged_by": "operator_001",
  "notes": "Maintenance scheduled for tomorrow morning"
}
```

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/ml/alerts/alert_20250826_001/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "operator_001",
    "notes": "Maintenance scheduled for tomorrow"
  }'
```

#### Response

```json
{
  "success": true,
  "alert_id": "alert_20250826_001",
  "acknowledged_at": "2025-08-26T15:30:00Z",
  "acknowledged_by": "operator_001",
  "status": "acknowledged"
}
```

### Resolve Alert

**Endpoint**: `POST /alerts/{alert_id}/resolve`

**Description**: Mark an alert as resolved after maintenance completion.

#### Request Body

```json
{
  "resolved_by": "technician_001",
  "resolution_notes": "Battery replaced, system tested",
  "maintenance_actions": [
    "Replaced main battery",
    "Tested charging system",
    "Verified current draw patterns"
  ]
}
```

#### Response

```json
{
  "success": true,
  "alert_id": "alert_20250826_001", 
  "resolved_at": "2025-08-26T16:45:00Z",
  "resolved_by": "technician_001",
  "status": "resolved"
}
```

## Model Management API

### Get Model Status

**Endpoint**: `GET /model-status`

**Description**: Retrieve information about the current ML model including training status, performance metrics, and metadata.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/ml/model-status"
```

#### Response

```json
{
  "model_version": "health_model_v1.2.0",
  "training_date": "2025-08-20T10:00:00Z",
  "is_trained": true,
  "status": "ready",
  "performance_metrics": {
    "r2_score": 0.85,
    "rmse": 12.3,
    "cross_val_score": 0.82,
    "feature_count": 15,
    "training_samples": 2500
  },
  "feature_importance_top_10": [
    {
      "feature": "current_draw_std",
      "importance": 0.23
    },
    {
      "feature": "battery_voltage_trend", 
      "importance": 0.19
    },
    {
      "feature": "gps_signal_quality",
      "importance": 0.15
    }
  ],
  "last_prediction_time": "2025-08-26T10:30:00Z"
}
```

### Trigger Model Training

**Endpoint**: `POST /train`

**Description**: Initiate ML model training with new data.

#### Request Body

```json
{
  "retrain_type": "incremental",
  "data_start_date": "2025-08-01",
  "data_end_date": "2025-08-26",
  "validation_split": 0.2,
  "model_version": "v1.3.0"
}
```

#### Response

```json
{
  "success": true,
  "training_job_id": "training_20250826_001",
  "status": "started",
  "estimated_duration_minutes": 15,
  "message": "Model training started successfully"
}
```

## System Health API

### Health Check

**Endpoint**: `GET /health`

**Description**: Check the overall health and status of the ML system.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/ml/health"
```

#### Response

```json
{
  "status": "healthy",
  "ml_enabled": true,
  "services": {
    "feature_engineering": "ready",
    "health_scoring": "ready",
    "predictive_alerts": "ready", 
    "model_manager": "ready"
  },
  "last_updated": "2025-08-26T10:30:00Z",
  "version": "1.0.0"
}
```

#### Health Status Values

| Status | Description |
|--------|-------------|
| `healthy` | All services operational |
| `degraded` | Some services have issues |
| `unhealthy` | Critical services down |

## Statistics API

### Get ML Statistics

**Endpoint**: `GET /statistics`

**Description**: Retrieve ML system performance and usage statistics.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/ml/statistics"
```

#### Response

```json
{
  "processing_stats": {
    "total_predictions": 1250,
    "average_processing_time_ms": 150,
    "cache_hit_rate": 0.85,
    "error_rate": 0.02
  },
  "alert_stats": {
    "alerts_generated_24h": 5,
    "alerts_acknowledged_24h": 3,
    "alerts_resolved_24h": 2,
    "average_resolution_time_hours": 4.5
  },
  "model_stats": {
    "model_accuracy": 0.87,
    "feature_importance_stability": 0.92,
    "last_training_date": "2025-08-20T10:00:00Z",
    "training_data_samples": 2500
  },
  "system_stats": {
    "uptime_hours": 72,
    "memory_usage_mb": 256,
    "disk_usage_mb": 150
  }
}
```

## Error Handling

### Error Response Format

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_DEVICE_ID",
    "message": "Device ID 'invalid_device' not found",
    "details": {
      "requested_device": "invalid_device",
      "available_devices": ["device_001", "device_002"]
    }
  },
  "timestamp": "2025-08-26T10:30:00Z"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_PARAMETERS` | Invalid query parameters or request body |
| 404 | `DEVICE_NOT_FOUND` | Requested device ID does not exist |
| 404 | `ALERT_NOT_FOUND` | Requested alert ID does not exist |
| 500 | `ML_SERVICE_ERROR` | Internal ML processing error |
| 503 | `ML_SERVICE_UNAVAILABLE` | ML service not initialized or down |

### Error Examples

#### Invalid Device ID
```json
{
  "success": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device 'invalid_device' not found"
  }
}
```

#### ML Service Down
```json
{
  "success": false, 
  "error": {
    "code": "ML_SERVICE_UNAVAILABLE",
    "message": "ML service not available. Please ensure ML service is initialized."
  }
}
```

#### Processing Error
```json
{
  "success": false,
  "error": {
    "code": "FEATURE_EXTRACTION_FAILED",
    "message": "Failed to extract features from telemetry data",
    "details": {
      "error_type": "insufficient_data",
      "minimum_required_samples": 30
    }
  }
}
```

## Rate Limiting

### Default Limits

| Endpoint Category | Requests per Minute | Burst Limit |
|------------------|-------------------|-------------|
| Health Scores | 60 | 10 |
| Alerts | 120 | 20 |
| Model Status | 30 | 5 |
| Training | 5 | 2 |
| Statistics | 30 | 5 |

### Rate Limit Headers

Responses include rate limiting headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1693036800
```

## SDKs and Client Libraries

### cURL Examples

#### Get health scores for specific devices
```bash
curl -X GET \
  "http://localhost:8000/api/ml/health-scores?device_ids=device_001,device_002&min_health_score=50" \
  -H "Accept: application/json"
```

#### Get critical alerts
```bash
curl -X GET \
  "http://localhost:8000/api/ml/alerts?severity=critical&status=active" \
  -H "Accept: application/json"
```

#### Acknowledge an alert
```bash
curl -X POST \
  "http://localhost:8000/api/ml/alerts/alert_123/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "operator_001", "notes": "Investigating issue"}'
```

### JavaScript Example

```javascript
// Get health scores
const response = await fetch('/api/ml/health-scores?device_ids=device_001');
const data = await response.json();

if (data.success) {
  console.log('Health scores:', data.health_scores);
} else {
  console.error('Error:', data.error.message);
}

// Acknowledge alert
const ackResponse = await fetch('/api/ml/alerts/alert_123/acknowledge', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    acknowledged_by: 'operator_001',
    notes: 'Maintenance scheduled'
  })
});
```

### Python Example

```python
import requests

# Get health scores
response = requests.get(
    'http://localhost:8000/api/ml/health-scores',
    params={'device_ids': 'device_001', 'min_health_score': 50}
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data['health_scores'])} devices")
else:
    print(f"Error: {response.status_code}")

# Acknowledge alert
ack_response = requests.post(
    'http://localhost:8000/api/ml/alerts/alert_123/acknowledge',
    json={
        'acknowledged_by': 'operator_001',
        'notes': 'Investigating issue'
    }
)
```

This API reference provides comprehensive documentation for integrating with the ML system programmatically. All endpoints support standard HTTP methods and return structured JSON responses with consistent error handling.