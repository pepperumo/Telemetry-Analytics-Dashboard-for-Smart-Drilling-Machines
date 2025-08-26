"""
Predictive Maintenance Alert System

This module implements intelligent maintenance alerts based on health score trends
with 48-72 hour advance warning capabilities.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of maintenance alerts"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    EQUIPMENT_FAILURE_RISK = "equipment_failure_risk"
    BATTERY_MAINTENANCE = "battery_maintenance"
    MECHANICAL_WEAR = "mechanical_wear"
    THERMAL_STRESS = "thermal_stress"
    ELECTRICAL_ANOMALY = "electrical_anomaly"


class AlertStatus(Enum):
    """Alert status values"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class MaintenanceAlert:
    """Represents a predictive maintenance alert"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = ""
    alert_type: AlertType = AlertType.PERFORMANCE_DEGRADATION
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    title: str = ""
    description: str = ""
    predicted_failure_time: Optional[datetime] = None
    confidence_score: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'predicted_failure_time': self.predicted_failure_time.isoformat() if self.predicted_failure_time else None,
            'confidence_score': self.confidence_score,
            'recommended_actions': self.recommended_actions,
            'affected_systems': self.affected_systems,
            'created_at': self.created_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata
        }


class TrendAnalyzer:
    """Analyzes health score trends for degradation detection"""

    def __init__(self, min_data_points: int = 5, trend_window_hours: int = 24):
        self.min_data_points = min_data_points
        self.trend_window_hours = trend_window_hours

    def analyze_health_trends(self, health_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze health score trends to detect degradation patterns
        
        Args:
            health_history: List of health score records with timestamps
            
        Returns:
            Dictionary containing trend analysis results
        """
        if len(health_history) < self.min_data_points:
            return {
                'trend_direction': 'insufficient_data',
                'degradation_rate': 0.0,
                'confidence': 0.0,
                'projected_failure_time': None
            }

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(health_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Calculate recent trend (last 24-72 hours)
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=self.trend_window_hours)
        recent_data = df[df['timestamp'] >= recent_cutoff].copy()

        if len(recent_data) < 2:
            return {
                'trend_direction': 'insufficient_recent_data',
                'degradation_rate': 0.0,
                'confidence': 0.0,
                'projected_failure_time': None
            }

        # Calculate linear trend
        x = np.arange(len(recent_data))
        y = recent_data['health_score'].values
        
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = self._calculate_linear_trend(x, y)
        
        # Determine trend direction
        trend_direction = 'stable'
        if slope < -0.5:  # Significant negative trend
            trend_direction = 'degrading'
        elif slope > 0.5:  # Significant positive trend
            trend_direction = 'improving'

        # Calculate degradation rate (health points per hour)
        time_span_hours = (recent_data['timestamp'].iloc[-1] - recent_data['timestamp'].iloc[0]).total_seconds() / 3600
        degradation_rate = slope / max(time_span_hours, 1) if time_span_hours > 0 else 0

        # Calculate confidence based on correlation and data quality
        confidence = min(abs(r_value) * 0.8 + (len(recent_data) / 20) * 0.2, 1.0)

        # Project failure time if degrading
        projected_failure_time = None
        if trend_direction == 'degrading' and slope < 0:
            current_score = y[-1]
            failure_threshold = 30  # Health score below which equipment is considered at risk
            hours_to_failure = (current_score - failure_threshold) / abs(degradation_rate)
            
            if 0 < hours_to_failure <= 168:  # Within 7 days
                projected_failure_time = now + timedelta(hours=hours_to_failure)

        return {
            'trend_direction': trend_direction,
            'degradation_rate': degradation_rate,
            'confidence': confidence,
            'projected_failure_time': projected_failure_time,
            'slope': slope,
            'r_squared': r_value ** 2,
            'data_points': len(recent_data)
        }

    def _calculate_linear_trend(self, x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float, float, float]:
        """Calculate linear trend using least squares regression"""
        from scipy.stats import linregress
        return linregress(x, y)


class PredictiveAlertService:
    """Service for generating and managing predictive maintenance alerts"""

    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.active_alerts: Dict[str, MaintenanceAlert] = {}
        self.alert_history: List[MaintenanceAlert] = []
        self.suppression_rules: Dict[str, Dict[str, Any]] = {}

    def generate_alerts_for_device(self, device_id: str, health_history: List[Dict[str, Any]], 
                                 current_metrics: Dict[str, Any]) -> List[MaintenanceAlert]:
        """
        Generate predictive maintenance alerts for a specific device
        
        Args:
            device_id: Device identifier
            health_history: Historical health score data
            current_metrics: Current equipment metrics
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        # Analyze health trends
        trend_analysis = self.trend_analyzer.analyze_health_trends(health_history)
        
        # Generate alerts based on trend analysis
        if trend_analysis['trend_direction'] == 'degrading':
            alert = self._create_degradation_alert(device_id, trend_analysis, current_metrics)
            if alert and self._should_generate_alert(alert):
                alerts.append(alert)
                self.active_alerts[alert.id] = alert

        # Check for specific maintenance conditions
        alerts.extend(self._check_specific_maintenance_conditions(device_id, current_metrics, trend_analysis))
        
        return alerts

    def _create_degradation_alert(self, device_id: str, trend_analysis: Dict[str, Any], 
                                current_metrics: Dict[str, Any]) -> Optional[MaintenanceAlert]:
        """Create alert for health score degradation"""
        if trend_analysis['confidence'] < 0.3:  # Low confidence threshold
            return None

        # Determine severity based on degradation rate and projected failure time
        severity = self._calculate_severity(trend_analysis, current_metrics)
        
        # Generate alert description
        degradation_rate = abs(trend_analysis['degradation_rate'])
        projected_time = trend_analysis.get('projected_failure_time')
        
        if projected_time:
            hours_until_failure = (projected_time - datetime.now()).total_seconds() / 3600
            time_desc = f"within {int(hours_until_failure)} hours"
        else:
            time_desc = "timeline uncertain"

        alert = MaintenanceAlert(
            device_id=device_id,
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=severity,
            title=f"Equipment Health Degradation - {device_id}",
            description=f"Health score declining at {degradation_rate:.2f} points/hour. "
                       f"Maintenance recommended {time_desc}.",
            predicted_failure_time=projected_time,
            confidence_score=trend_analysis['confidence'],
            recommended_actions=self._get_degradation_recommendations(severity, current_metrics),
            affected_systems=self._identify_affected_systems(current_metrics),
            metadata={
                'trend_analysis': trend_analysis,
                'current_health_score': current_metrics.get('health_score', 0),
                'degradation_rate': degradation_rate
            }
        )
        
        return alert

    def _check_specific_maintenance_conditions(self, device_id: str, current_metrics: Dict[str, Any], 
                                             trend_analysis: Dict[str, Any]) -> List[MaintenanceAlert]:
        """Check for specific maintenance conditions beyond general degradation"""
        alerts = []
        
        # Battery maintenance alert
        battery_level = current_metrics.get('battery_level', 100)
        if battery_level < 20 and trend_analysis.get('confidence', 0) > 0.5:
            alert = MaintenanceAlert(
                device_id=device_id,
                alert_type=AlertType.BATTERY_MAINTENANCE,
                severity=AlertSeverity.HIGH,
                title=f"Battery Maintenance Required - {device_id}",
                description=f"Battery level at {battery_level}%. Immediate maintenance required.",
                predicted_failure_time=datetime.now() + timedelta(hours=12),
                confidence_score=0.9,
                recommended_actions=[
                    "Schedule battery replacement",
                    "Check charging system",
                    "Reduce equipment usage until maintenance"
                ],
                affected_systems=["Power System", "Battery Management"],
                metadata={'battery_level': battery_level}
            )
            alerts.append(alert)

        # Thermal stress alert
        max_temp = current_metrics.get('temperature_max', 0)
        if max_temp > 80 and trend_analysis.get('degradation_rate', 0) < -0.5:
            alert = MaintenanceAlert(
                device_id=device_id,
                alert_type=AlertType.THERMAL_STRESS,
                severity=AlertSeverity.MEDIUM,
                title=f"Thermal Stress Detected - {device_id}",
                description=f"Maximum temperature {max_temp}°C exceeding safe limits. "
                           f"Cooling system maintenance recommended.",
                predicted_failure_time=datetime.now() + timedelta(hours=48),
                confidence_score=0.7,
                recommended_actions=[
                    "Inspect cooling system",
                    "Clean air filters",
                    "Check thermal sensors",
                    "Reduce operational load"
                ],
                affected_systems=["Cooling System", "Temperature Control"],
                metadata={'max_temperature': max_temp}
            )
            alerts.append(alert)

        # Mechanical wear alert
        vibration_std = current_metrics.get('vibration_std', 0)
        if vibration_std > 3.0 and trend_analysis.get('confidence', 0) > 0.4:
            alert = MaintenanceAlert(
                device_id=device_id,
                alert_type=AlertType.MECHANICAL_WEAR,
                severity=AlertSeverity.MEDIUM,
                title=f"Mechanical Wear Indicators - {device_id}",
                description=f"Vibration patterns suggest mechanical wear. "
                           f"Inspection recommended within 72 hours.",
                predicted_failure_time=datetime.now() + timedelta(hours=72),
                confidence_score=0.6,
                recommended_actions=[
                    "Inspect mechanical components",
                    "Check bearing condition",
                    "Lubricate moving parts",
                    "Analyze vibration patterns"
                ],
                affected_systems=["Drive System", "Mechanical Components"],
                metadata={'vibration_std': vibration_std}
            )
            alerts.append(alert)

        return alerts

    def _calculate_severity(self, trend_analysis: Dict[str, Any], current_metrics: Dict[str, Any]) -> AlertSeverity:
        """Calculate alert severity based on multiple factors"""
        degradation_rate = abs(trend_analysis.get('degradation_rate', 0))
        confidence = trend_analysis.get('confidence', 0)
        projected_time = trend_analysis.get('projected_failure_time')
        current_health = current_metrics.get('health_score', 100)

        # Critical conditions
        if current_health < 30 or degradation_rate > 2.0:
            return AlertSeverity.CRITICAL

        # High severity conditions
        if projected_time:
            hours_until_failure = (projected_time - datetime.now()).total_seconds() / 3600
            if hours_until_failure < 48 or (degradation_rate > 1.0 and confidence > 0.7):
                return AlertSeverity.HIGH

        # Medium severity conditions
        if degradation_rate > 0.5 and confidence > 0.5:
            return AlertSeverity.MEDIUM

        return AlertSeverity.LOW

    def _get_degradation_recommendations(self, severity: AlertSeverity, current_metrics: Dict[str, Any]) -> List[str]:
        """Get recommended actions based on severity and current conditions"""
        base_actions = [
            "Schedule preventive maintenance inspection",
            "Monitor equipment more frequently",
            "Review operational parameters"
        ]

        if severity == AlertSeverity.CRITICAL:
            return [
                "IMMEDIATE ACTION REQUIRED",
                "Stop equipment operation",
                "Contact maintenance team urgently",
                "Prepare for emergency maintenance"
            ] + base_actions

        elif severity == AlertSeverity.HIGH:
            return [
                "Schedule maintenance within 24-48 hours",
                "Reduce operational load",
                "Increase monitoring frequency"
            ] + base_actions

        elif severity == AlertSeverity.MEDIUM:
            return [
                "Plan maintenance within next week",
                "Monitor performance trends closely"
            ] + base_actions

        return base_actions

    def _identify_affected_systems(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Identify systems likely to be affected based on current metrics"""
        affected = []
        
        if current_metrics.get('battery_level', 100) < 50:
            affected.append("Power System")
        
        if current_metrics.get('temperature_max', 0) > 75:
            affected.append("Cooling System")
        
        if current_metrics.get('current_mean', 0) > 10:
            affected.append("Electrical System")
        
        if current_metrics.get('vibration_std', 0) > 2.5:
            affected.append("Mechanical System")

        return affected if affected else ["General System"]

    def _should_generate_alert(self, alert: MaintenanceAlert) -> bool:
        """Determine if alert should be generated based on suppression rules"""
        # Check if similar alert already active for this device
        for existing_alert in self.active_alerts.values():
            if (existing_alert.device_id == alert.device_id and 
                existing_alert.alert_type == alert.alert_type and
                existing_alert.status == AlertStatus.ACTIVE):
                
                # Don't generate duplicate alerts within 4 hours
                time_diff = (alert.created_at - existing_alert.created_at).total_seconds() / 3600
                if time_diff < 4:
                    return False

        # Check suppression rules
        suppression_key = f"{alert.device_id}_{alert.alert_type.value}"
        if suppression_key in self.suppression_rules:
            rule = self.suppression_rules[suppression_key]
            if rule.get('suppressed_until', datetime.min) > datetime.now():
                return False

        return True

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.metadata['acknowledged_by'] = acknowledged_by
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        return False

    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.metadata['resolved_by'] = resolved_by
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
            return True
        return False

    def suppress_alerts(self, device_id: str, alert_type: AlertType, 
                       suppress_hours: int = 24) -> bool:
        """Suppress alerts for a device and alert type for specified duration"""
        suppression_key = f"{device_id}_{alert_type.value}"
        self.suppression_rules[suppression_key] = {
            'suppressed_until': datetime.now() + timedelta(hours=suppress_hours),
            'created_at': datetime.now()
        }
        logger.info(f"Alerts suppressed for {device_id} ({alert_type.value}) for {suppress_hours} hours")
        return True

    def get_active_alerts(self, device_id: Optional[str] = None, 
                         severity: Optional[AlertSeverity] = None) -> List[MaintenanceAlert]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if device_id:
            alerts = [a for a in alerts if a.device_id == device_id]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by severity and creation time
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.created_at), reverse=True)
        return alerts

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics about alert generation and resolution"""
        active_count = len(self.active_alerts)
        total_generated = len(self.alert_history) + active_count
        
        # Count by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                a for a in self.active_alerts.values() if a.severity == severity
            ])
        
        # Average resolution time for resolved alerts
        resolved_alerts = [a for a in self.alert_history if a.resolved_at and a.created_at]
        avg_resolution_time = 0
        if resolved_alerts:
            resolution_times = []
            for a in resolved_alerts:
                if a.resolved_at and a.created_at:
                    time_diff = (a.resolved_at - a.created_at).total_seconds() / 3600
                    if time_diff >= 0:  # Only include positive time differences
                        resolution_times.append(time_diff)
            
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return {
            'active_alerts': active_count,
            'total_generated': total_generated,
            'severity_breakdown': severity_counts,
            'average_resolution_time_hours': avg_resolution_time,
            'suppression_rules_active': len(self.suppression_rules)
        }