"""
ML-specific Pydantic models for API responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Equipment health risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of maintenance alerts"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    EQUIPMENT_FAILURE_RISK = "equipment_failure_risk"
    BATTERY_MAINTENANCE = "battery_maintenance"
    MECHANICAL_WEAR = "mechanical_wear"
    THERMAL_STRESS = "thermal_stress"
    ELECTRICAL_ANOMALY = "electrical_anomaly"


class AlertStatus(str, Enum):
    """Alert status values"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class ExplanatoryFactor(BaseModel):
    """Factor explaining health score"""
    feature: str = Field(..., description="Feature name contributing to health score")
    value: float = Field(..., description="Current feature value")
    importance: float = Field(..., description="Feature importance score (0-1)")
    impact: str = Field(..., description="Human-readable impact description")


class HealthScoreResponse(BaseModel):
    """Individual device health score response"""
    device_id: str = Field(..., description="Device identifier")
    health_score: float = Field(..., description="Health score (0-100, higher is better)")
    confidence_interval: tuple[float, float] = Field(..., description="95% confidence interval for health score")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    explanatory_factors: List[ExplanatoryFactor] = Field(..., description="Top 3 factors explaining the health score")
    last_calculated: datetime = Field(..., description="When this health score was calculated")


class HealthScoresListResponse(BaseModel):
    """Response for health scores endpoint"""
    health_scores: List[HealthScoreResponse] = Field(..., description="List of device health scores")
    total_devices: int = Field(..., description="Total number of devices")
    average_health_score: float = Field(..., description="Fleet average health score")
    at_risk_devices: int = Field(..., description="Number of devices with medium/high/critical risk")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics"""
    r2_score: float = Field(..., description="R-squared score")
    rmse: float = Field(..., description="Root Mean Square Error")
    cross_val_score: float = Field(..., description="Cross-validation score")
    feature_count: int = Field(..., description="Number of features used")
    training_samples: int = Field(..., description="Number of training samples")


class ModelStatusResponse(BaseModel):
    """Model status and metadata"""
    model_version: str = Field(..., description="Model version identifier")
    training_date: datetime = Field(..., description="When the model was last trained")
    is_trained: bool = Field(..., description="Whether model is trained and ready")
    performance_metrics: Optional[ModelPerformanceMetrics] = Field(None, description="Model performance metrics")
    feature_importance_top_10: List[Dict[str, Any]] = Field(default_factory=list, description="Top 10 most important features")
    status: str = Field(..., description="Model status (ready, training, error)")
    last_prediction_time: Optional[datetime] = Field(None, description="When last prediction was made")


class MLTrainingRequest(BaseModel):
    """Request to train ML models"""
    force_retrain: bool = Field(default=False, description="Force retraining even if model exists")
    

class MLTrainingResponse(BaseModel):
    """Response from ML training"""
    status: str = Field(..., description="Training status (success, error)")
    message: str = Field(..., description="Training result message")
    model_metadata: Optional[ModelStatusResponse] = Field(None, description="Updated model metadata")


# Alert-related models
class MaintenanceAlertResponse(BaseModel):
    """Predictive maintenance alert response"""
    id: str = Field(..., description="Alert unique identifier")
    device_id: str = Field(..., description="Device identifier")
    alert_type: AlertType = Field(..., description="Type of maintenance alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(..., description="Current alert status")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    predicted_failure_time: Optional[datetime] = Field(None, description="Predicted failure time (if applicable)")
    confidence_score: float = Field(..., description="Alert confidence score (0-1)")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended maintenance actions")
    affected_systems: List[str] = Field(default_factory=list, description="Systems affected by potential failure")
    created_at: datetime = Field(..., description="When alert was created")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional alert metadata")


class AlertsListResponse(BaseModel):
    """List of alerts with pagination"""
    alerts: List[MaintenanceAlertResponse] = Field(..., description="List of maintenance alerts")
    total_count: int = Field(..., description="Total number of alerts matching filters")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of alerts per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class AlertFilters(BaseModel):
    """Filters for alert queries"""
    device_id: Optional[str] = Field(None, description="Filter by device ID")
    severity: Optional[AlertSeverity] = Field(None, description="Filter by severity level")
    status: Optional[AlertStatus] = Field(None, description="Filter by alert status")
    alert_type: Optional[AlertType] = Field(None, description="Filter by alert type")
    created_after: Optional[datetime] = Field(None, description="Filter alerts created after this date")
    created_before: Optional[datetime] = Field(None, description="Filter alerts created before this date")


class AlertAcknowledgmentRequest(BaseModel):
    """Request to acknowledge an alert"""
    acknowledged_by: str = Field(..., description="Who is acknowledging the alert")
    notes: Optional[str] = Field(None, description="Optional acknowledgment notes")


class AlertAcknowledgmentResponse(BaseModel):
    """Response from alert acknowledgment"""
    success: bool = Field(..., description="Whether acknowledgment was successful")
    message: str = Field(..., description="Result message")
    alert: Optional[MaintenanceAlertResponse] = Field(None, description="Updated alert details")


class AlertSuppressionRequest(BaseModel):
    """Request to suppress alerts"""
    device_id: str = Field(..., description="Device ID to suppress alerts for")
    alert_type: AlertType = Field(..., description="Type of alert to suppress")
    suppress_hours: int = Field(24, description="Hours to suppress alerts for")
    reason: Optional[str] = Field(None, description="Reason for suppression")


class AlertSuppressionResponse(BaseModel):
    """Response from alert suppression"""
    success: bool = Field(..., description="Whether suppression was successful")
    message: str = Field(..., description="Result message")


class AlertStatisticsResponse(BaseModel):
    """Alert statistics and summary"""
    active_alerts: int = Field(..., description="Number of currently active alerts")
    total_generated: int = Field(..., description="Total alerts generated")
    severity_breakdown: Dict[str, int] = Field(..., description="Count of alerts by severity")
    average_resolution_time_hours: float = Field(..., description="Average time to resolve alerts (hours)")
    suppression_rules_active: int = Field(..., description="Number of active suppression rules")
    training_time_seconds: float = Field(..., description="Time taken for training")


class HealthScoreFilters(BaseModel):
    """Filters for health scores endpoint"""
    device_ids: Optional[List[str]] = Field(None, description="Filter by specific device IDs")
    min_health_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum health score")
    max_health_score: Optional[float] = Field(None, ge=0, le=100, description="Maximum health score")
    risk_levels: Optional[List[RiskLevel]] = Field(None, description="Filter by risk levels")
    start_date: Optional[str] = Field(None, description="Start date for filtering (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for filtering (YYYY-MM-DD)")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")