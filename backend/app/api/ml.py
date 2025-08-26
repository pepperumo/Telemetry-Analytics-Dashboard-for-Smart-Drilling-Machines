"""
ML API endpoints for health scores, model status, and ML operations
"""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional, List
from datetime import datetime
import logging

from app.models.ml_schemas import (
    HealthScoresListResponse, HealthScoreResponse, ModelStatusResponse,
    MLTrainingRequest, MLTrainingResponse, HealthScoreFilters,
    PaginationParams, ErrorResponse, RiskLevel, ExplanatoryFactor,
    # Alert-related models
    MaintenanceAlertResponse, AlertsListResponse, AlertFilters,
    AlertAcknowledgmentRequest, AlertAcknowledgmentResponse,
    AlertSuppressionRequest, AlertSuppressionResponse,
    AlertStatisticsResponse, AlertSeverity, AlertStatus, AlertType
)
from app.ml.services import MLService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_ml_service(request: Request) -> MLService:
    """Dependency to get ML service from app state"""
    if not hasattr(request.app.state, 'ml_service'):
        raise HTTPException(
            status_code=503, 
            detail="ML service not available. Please ensure ML service is initialized."
        )
    return request.app.state.ml_service


@router.get("/health-scores", response_model=HealthScoresListResponse)
async def get_health_scores(
    request: Request,
    device_ids: Optional[str] = Query(None, description="Comma-separated device IDs to filter"),
    min_health_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum health score"),
    max_health_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum health score"),
    risk_levels: Optional[str] = Query(None, description="Comma-separated risk levels (low,medium,high,critical)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get health scores for all devices with optional filtering and pagination
    
    Returns health scores with confidence intervals, risk levels, and explanatory factors.
    Supports filtering by device ID, health score range, risk level, and date range.
    """
    try:
        logger.info(f"Health scores request: device_ids={device_ids}, page={page}, page_size={page_size}")
        
        # Parse filters
        filters = {}
        if device_ids:
            filters['device_ids'] = [d.strip() for d in device_ids.split(',')]
        if min_health_score is not None:
            filters['min_health_score'] = min_health_score
        if max_health_score is not None:
            filters['max_health_score'] = max_health_score
        if risk_levels:
            filters['risk_levels'] = [RiskLevel(r.strip()) for r in risk_levels.split(',')]
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
            
        # Get health scores from ML service
        health_scores_result = await ml_service.calculate_health_scores()
        
        if health_scores_result.get('status') != 'success':
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate health scores: {health_scores_result.get('message', 'Unknown error')}"
            )
            
        raw_scores = health_scores_result['health_scores']
        
        # Convert to response format
        health_scores = []
        total_score = 0
        at_risk_count = 0
        
        for device_id, score_data in raw_scores.items():
            # Apply device filter
            if filters.get('device_ids') and device_id not in filters['device_ids']:
                continue
                
            health_score = float(score_data['health_score'])
            
            # Apply health score range filters
            if filters.get('min_health_score') is not None and health_score < filters['min_health_score']:
                continue
            if filters.get('max_health_score') is not None and health_score > filters['max_health_score']:
                continue
                
            # Determine risk level
            if health_score >= 80:
                risk_level = RiskLevel.LOW
            elif health_score >= 60:
                risk_level = RiskLevel.MEDIUM
            elif health_score >= 40:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
                
            # Apply risk level filter
            if filters.get('risk_levels') and risk_level not in filters['risk_levels']:
                continue
                
            # Count at-risk devices
            if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                at_risk_count += 1
                
            # Convert explanatory factors
            explanatory_factors = []
            for factor in score_data.get('explanatory_factors', []):
                explanatory_factors.append(ExplanatoryFactor(
                    feature=factor['feature'],
                    value=factor['value'],
                    importance=factor['importance'],
                    impact=factor['impact']
                ))
                
            health_scores.append(HealthScoreResponse(
                device_id=device_id,
                health_score=health_score,
                confidence_interval=tuple(score_data['confidence_interval']),
                risk_level=risk_level,
                explanatory_factors=explanatory_factors[:3],  # Top 3 factors
                last_calculated=datetime.now()
            ))
            
            total_score += health_score
            
        # Apply pagination
        total_devices = len(health_scores)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_scores = health_scores[start_idx:end_idx]
        
        # Calculate average health score
        average_score = total_score / total_devices if total_devices > 0 else 0
        
        return HealthScoresListResponse(
            health_scores=paginated_scores,
            total_devices=total_devices,
            average_health_score=round(average_score, 2),
            at_risk_devices=at_risk_count,
            filters_applied=filters
        )
        
    except Exception as e:
        logger.error(f"Error getting health scores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/model-status", response_model=ModelStatusResponse)
async def get_model_status(
    request: Request,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get ML model status, performance metrics, and metadata
    
    Returns information about model training status, performance metrics,
    feature importance, and last prediction time.
    """
    try:
        logger.info("Model status request")
        
        # Get model status from ML service
        status_result = ml_service.get_health_scoring_status()
        
        if not status_result.get('is_trained', False):
            return ModelStatusResponse(
                model_version="untrained",
                training_date=datetime.now(),
                is_trained=False,
                performance_metrics=None,
                feature_importance_top_10=[],
                status="not_trained",
                last_prediction_time=None
            )
            
        metadata = status_result.get('model_metadata', {})
        
        # Convert performance metrics
        performance_metrics = None
        if metadata:
            from app.models.ml_schemas import ModelPerformanceMetrics
            performance_metrics = ModelPerformanceMetrics(
                r2_score=metadata.get('r2_score', 0.0),
                rmse=metadata.get('rmse', 0.0),
                cross_val_score=metadata.get('cross_val_score', 0.0),
                feature_count=metadata.get('feature_count', 0),
                training_samples=metadata.get('training_samples', 0)
            )
        
        return ModelStatusResponse(
            model_version=metadata.get('model_version', 'unknown'),
            training_date=metadata.get('training_date', datetime.now()),
            is_trained=status_result.get('is_trained', False),
            performance_metrics=performance_metrics,
            feature_importance_top_10=metadata.get('feature_importance_top_10', []),
            status="ready" if status_result.get('is_trained') else "not_trained",
            last_prediction_time=datetime.now() if status_result.get('is_trained') else None
        )
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/train", response_model=MLTrainingResponse)
async def train_model(
    request: Request,
    training_request: MLTrainingRequest = MLTrainingRequest(),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Train or retrain the health scoring model
    
    Triggers model training using the latest telemetry data and features.
    Returns training results and updated model metadata.
    """
    try:
        logger.info(f"Model training request: force_retrain={training_request.force_retrain}")
        
        start_time = datetime.now()
        
        # Train the model
        training_result = await ml_service.train_health_scoring_model()
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        if training_result.get('status') != 'success':
            return MLTrainingResponse(
                status="error",
                message=training_result.get('message', 'Training failed'),
                model_metadata=None,
                training_time_seconds=training_time
            )
            
        # Get updated model status
        status_result = ml_service.get_health_scoring_status()
        metadata = status_result.get('model_metadata', {})
        
        # Convert to response format
        model_metadata = None
        if metadata:
            from app.models.ml_schemas import ModelPerformanceMetrics
            performance_metrics = ModelPerformanceMetrics(
                r2_score=metadata.get('r2_score', 0.0),
                rmse=metadata.get('rmse', 0.0),
                cross_val_score=metadata.get('cross_val_score', 0.0),
                feature_count=metadata.get('feature_count', 0),
                training_samples=metadata.get('training_samples', 0)
            )
            
            model_metadata = ModelStatusResponse(
                model_version=metadata.get('model_version', 'unknown'),
                training_date=metadata.get('training_date', datetime.now()),
                is_trained=True,
                performance_metrics=performance_metrics,
                feature_importance_top_10=metadata.get('feature_importance_top_10', []),
                status="ready",
                last_prediction_time=datetime.now()
            )
        
        return MLTrainingResponse(
            status="success",
            message=training_result.get('message', 'Training completed successfully'),
            model_metadata=model_metadata,
            training_time_seconds=training_time
        )
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/health", response_model=dict)
async def health_check(
    request: Request,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Health check for ML API
    
    Returns the status of ML services and components.
    """
    try:
        # Check if ML service is initialized
        ml_status = ml_service.get_health_scoring_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ml_service": "available",
            "health_scoring": "ready" if ml_status.get('is_trained') else "not_trained",
            "feature_engineering": "ready"
        }
        
    except Exception as e:
        logger.error(f"ML health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


# Alert Management Endpoints

@router.get("/alerts", response_model=AlertsListResponse)
async def get_alerts(
    request: Request,
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
    created_after: Optional[datetime] = Query(None, description="Filter alerts created after this date"),
    created_before: Optional[datetime] = Query(None, description="Filter alerts created before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=1000, description="Items per page"),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get predictive maintenance alerts with filtering and pagination
    
    Retrieves active and historical maintenance alerts generated by the
    predictive maintenance system. Supports filtering by device, severity,
    status, and date ranges.
    """
    try:
        # Get alerts from ML service
        alerts_data = ml_service.get_active_alerts(
            device_id=device_id,
            severity=severity.value if severity else None
        )
        
        # Convert to response models
        alerts = []
        for alert_dict in alerts_data:
            alert = MaintenanceAlertResponse(
                id=alert_dict["id"],
                device_id=alert_dict["device_id"],
                alert_type=AlertType(alert_dict["alert_type"]),
                severity=AlertSeverity(alert_dict["severity"]),
                status=AlertStatus(alert_dict["status"]),
                title=alert_dict["title"],
                description=alert_dict["description"],
                predicted_failure_time=datetime.fromisoformat(alert_dict["predicted_failure_time"]) if alert_dict["predicted_failure_time"] else None,
                confidence_score=alert_dict["confidence_score"],
                recommended_actions=alert_dict["recommended_actions"],
                affected_systems=alert_dict["affected_systems"],
                created_at=datetime.fromisoformat(alert_dict["created_at"]),
                acknowledged_at=datetime.fromisoformat(alert_dict["acknowledged_at"]) if alert_dict["acknowledged_at"] else None,
                resolved_at=datetime.fromisoformat(alert_dict["resolved_at"]) if alert_dict["resolved_at"] else None,
                metadata=alert_dict["metadata"]
            )
            alerts.append(alert)
        
        # Apply additional filters
        if status and status != AlertStatus.ACTIVE:
            # For non-active statuses, would need to query alert history
            # For now, just return empty list for non-active statuses
            alerts = []
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        if created_after:
            alerts = [a for a in alerts if a.created_at >= created_after]
        
        if created_before:
            alerts = [a for a in alerts if a.created_at <= created_before]
        
        # Apply pagination
        total_count = len(alerts)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_alerts = alerts[start_idx:end_idx]
        
        return AlertsListResponse(
            alerts=paginated_alerts,
            total_count=total_count,
            page=page,
            per_page=per_page,
            has_next=end_idx < total_count
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.post("/alerts/generate", response_model=AlertsListResponse)
async def generate_alerts(
    request: Request,
    device_id: Optional[str] = Query(None, description="Generate alerts for specific device"),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Generate new predictive maintenance alerts
    
    Analyzes current equipment health and generates new alerts based on
    trends and thresholds. This is typically called periodically by the
    system but can be triggered manually.
    """
    try:
        # Generate alerts
        alerts_data = await ml_service.generate_predictive_alerts(device_id)
        
        # Convert to response models
        alerts = []
        for alert_dict in alerts_data:
            alert = MaintenanceAlertResponse(
                id=alert_dict["id"],
                device_id=alert_dict["device_id"],
                alert_type=AlertType(alert_dict["alert_type"]),
                severity=AlertSeverity(alert_dict["severity"]),
                status=AlertStatus(alert_dict["status"]),
                title=alert_dict["title"],
                description=alert_dict["description"],
                predicted_failure_time=datetime.fromisoformat(alert_dict["predicted_failure_time"]) if alert_dict["predicted_failure_time"] else None,
                confidence_score=alert_dict["confidence_score"],
                recommended_actions=alert_dict["recommended_actions"],
                affected_systems=alert_dict["affected_systems"],
                created_at=datetime.fromisoformat(alert_dict["created_at"]),
                acknowledged_at=datetime.fromisoformat(alert_dict["acknowledged_at"]) if alert_dict["acknowledged_at"] else None,
                resolved_at=datetime.fromisoformat(alert_dict["resolved_at"]) if alert_dict["resolved_at"] else None,
                metadata=alert_dict["metadata"]
            )
            alerts.append(alert)
        
        return AlertsListResponse(
            alerts=alerts,
            total_count=len(alerts),
            page=1,
            per_page=len(alerts),
            has_next=False
        )
        
    except Exception as e:
        logger.error(f"Error generating alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate alerts: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertAcknowledgmentResponse)
async def acknowledge_alert(
    alert_id: str,
    request: Request,
    acknowledgment: AlertAcknowledgmentRequest,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Acknowledge a maintenance alert
    
    Marks an alert as acknowledged by a user or system, indicating that
    the alert has been seen and is being addressed.
    """
    try:
        success = ml_service.acknowledge_alert(alert_id, acknowledgment.acknowledged_by)
        
        if success:
            # Get updated alert details
            alerts = ml_service.get_active_alerts()
            updated_alert = None
            for alert_dict in alerts:
                if alert_dict["id"] == alert_id:
                    updated_alert = MaintenanceAlertResponse(
                        id=alert_dict["id"],
                        device_id=alert_dict["device_id"],
                        alert_type=AlertType(alert_dict["alert_type"]),
                        severity=AlertSeverity(alert_dict["severity"]),
                        status=AlertStatus(alert_dict["status"]),
                        title=alert_dict["title"],
                        description=alert_dict["description"],
                        predicted_failure_time=datetime.fromisoformat(alert_dict["predicted_failure_time"]) if alert_dict["predicted_failure_time"] else None,
                        confidence_score=alert_dict["confidence_score"],
                        recommended_actions=alert_dict["recommended_actions"],
                        affected_systems=alert_dict["affected_systems"],
                        created_at=datetime.fromisoformat(alert_dict["created_at"]),
                        acknowledged_at=datetime.fromisoformat(alert_dict["acknowledged_at"]) if alert_dict["acknowledged_at"] else None,
                        resolved_at=datetime.fromisoformat(alert_dict["resolved_at"]) if alert_dict["resolved_at"] else None,
                        metadata=alert_dict["metadata"]
                    )
                    break
            
            return AlertAcknowledgmentResponse(
                success=True,
                message=f"Alert {alert_id} acknowledged by {acknowledgment.acknowledged_by}",
                alert=updated_alert
            )
        else:
            return AlertAcknowledgmentResponse(
                success=False,
                message=f"Alert {alert_id} not found or already acknowledged",
                alert=None
            )
            
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/alerts/{alert_id}/resolve", response_model=AlertAcknowledgmentResponse)
async def resolve_alert(
    alert_id: str,
    request: Request,
    resolution: AlertAcknowledgmentRequest,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Resolve a maintenance alert
    
    Marks an alert as resolved, indicating that the maintenance issue
    has been addressed and the alert can be closed.
    """
    try:
        success = ml_service.resolve_alert(alert_id, resolution.acknowledged_by)
        
        if success:
            return AlertAcknowledgmentResponse(
                success=True,
                message=f"Alert {alert_id} resolved by {resolution.acknowledged_by}",
                alert=None  # Alert moved to history
            )
        else:
            return AlertAcknowledgmentResponse(
                success=False,
                message=f"Alert {alert_id} not found or already resolved",
                alert=None
            )
            
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.post("/alerts/suppress", response_model=AlertSuppressionResponse)
async def suppress_alerts(
    request: Request,
    suppression: AlertSuppressionRequest,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Suppress alerts for a device and alert type
    
    Temporarily prevents generation of alerts for a specific device and
    alert type for a specified duration. Useful during maintenance windows.
    """
    try:
        success = ml_service.suppress_alerts(
            device_id=suppression.device_id,
            alert_type=suppression.alert_type.value,
            suppress_hours=suppression.suppress_hours
        )
        
        if success:
            return AlertSuppressionResponse(
                success=True,
                message=f"Alerts suppressed for {suppression.device_id} "
                       f"({suppression.alert_type.value}) for {suppression.suppress_hours} hours"
            )
        else:
            return AlertSuppressionResponse(
                success=False,
                message="Failed to suppress alerts"
            )
            
    except Exception as e:
        logger.error(f"Error suppressing alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suppress alerts: {str(e)}")


@router.get("/alerts/statistics", response_model=AlertStatisticsResponse)
async def get_alert_statistics(
    request: Request,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get alert statistics and summary information
    
    Returns statistics about alert generation, resolution times, and
    current system status for operational monitoring.
    """
    try:
        stats = ml_service.get_alert_statistics()
        
        return AlertStatisticsResponse(
            active_alerts=stats["active_alerts"],
            total_generated=stats["total_generated"],
            severity_breakdown=stats["severity_breakdown"],
            average_resolution_time_hours=stats["average_resolution_time_hours"],
            suppression_rules_active=stats["suppression_rules_active"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alert statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")