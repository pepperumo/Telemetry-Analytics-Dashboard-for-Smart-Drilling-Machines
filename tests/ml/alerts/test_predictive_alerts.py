"""
Test suite for Predictive Maintenance Alert System
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.ml.alerts.predictive_alerts import (
    TrendAnalyzer, PredictiveAlertService, MaintenanceAlert,
    AlertSeverity, AlertType, AlertStatus
)


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer"""

    @pytest.fixture
    def trend_analyzer(self):
        """Create TrendAnalyzer instance"""
        return TrendAnalyzer(min_data_points=3, trend_window_hours=24)

    @pytest.fixture
    def degrading_health_data(self):
        """Create mock health data showing degradation"""
        now = datetime.now()
        return [
            {'timestamp': now - timedelta(hours=48), 'health_score': 95.0},
            {'timestamp': now - timedelta(hours=36), 'health_score': 89.0},
            {'timestamp': now - timedelta(hours=24), 'health_score': 82.0},
            {'timestamp': now - timedelta(hours=12), 'health_score': 75.0},
            {'timestamp': now - timedelta(hours=6), 'health_score': 68.0},
            {'timestamp': now - timedelta(hours=2), 'health_score': 62.0}
        ]

    @pytest.fixture
    def stable_health_data(self):
        """Create mock health data showing stability"""
        now = datetime.now()
        return [
            {'timestamp': now - timedelta(hours=48), 'health_score': 85.0},
            {'timestamp': now - timedelta(hours=36), 'health_score': 84.5},
            {'timestamp': now - timedelta(hours=24), 'health_score': 85.2},
            {'timestamp': now - timedelta(hours=12), 'health_score': 84.8},
            {'timestamp': now - timedelta(hours=6), 'health_score': 85.1},
            {'timestamp': now - timedelta(hours=2), 'health_score': 84.9}
        ]

    @pytest.fixture
    def improving_health_data(self):
        """Create mock health data showing improvement"""
        now = datetime.now()
        return [
            {'timestamp': now - timedelta(hours=48), 'health_score': 65.0},
            {'timestamp': now - timedelta(hours=36), 'health_score': 70.0},
            {'timestamp': now - timedelta(hours=24), 'health_score': 75.0},
            {'timestamp': now - timedelta(hours=12), 'health_score': 80.0},
            {'timestamp': now - timedelta(hours=6), 'health_score': 85.0},
            {'timestamp': now - timedelta(hours=2), 'health_score': 88.0}
        ]

    def test_insufficient_data(self, trend_analyzer):
        """Test behavior with insufficient data points"""
        health_data = [
            {'timestamp': datetime.now(), 'health_score': 85.0}
        ]
        
        result = trend_analyzer.analyze_health_trends(health_data)
        
        assert result['trend_direction'] == 'insufficient_data'
        assert result['degradation_rate'] == 0.0
        assert result['confidence'] == 0.0
        assert result['projected_failure_time'] is None

    def test_degrading_trend_detection(self, trend_analyzer, degrading_health_data):
        """Test detection of degrading health trends"""
        result = trend_analyzer.analyze_health_trends(degrading_health_data)
        
        assert result['trend_direction'] == 'degrading'
        assert result['degradation_rate'] < 0  # Negative rate indicates degradation
        assert result['confidence'] > 0.5  # Should have reasonable confidence
        assert result['projected_failure_time'] is not None
        assert isinstance(result['projected_failure_time'], datetime)

    def test_stable_trend_detection(self, trend_analyzer, stable_health_data):
        """Test detection of stable health trends"""
        result = trend_analyzer.analyze_health_trends(stable_health_data)
        
        assert result['trend_direction'] == 'stable'
        assert abs(result['degradation_rate']) < 0.5  # Small change rate
        assert result['projected_failure_time'] is None

    def test_improving_trend_detection(self, trend_analyzer, improving_health_data):
        """Test detection of improving health trends"""
        result = trend_analyzer.analyze_health_trends(improving_health_data)
        
        assert result['trend_direction'] == 'improving'
        assert result['degradation_rate'] > 0  # Positive rate indicates improvement
        assert result['projected_failure_time'] is None

    @patch('app.ml.alerts.predictive_alerts.TrendAnalyzer._calculate_linear_trend')
    def test_linear_trend_calculation(self, mock_linregress, trend_analyzer, degrading_health_data):
        """Test linear trend calculation"""
        # Mock scipy.stats.linregress return values
        mock_linregress.return_value = (-2.5, 100, -0.95, 0.001, 0.1)  # slope, intercept, r_value, p_value, std_err
        
        result = trend_analyzer.analyze_health_trends(degrading_health_data)
        
        mock_linregress.assert_called_once()
        assert result['slope'] == -2.5
        assert result['r_squared'] == 0.9025  # r_value^2

    def test_confidence_calculation(self, trend_analyzer, degrading_health_data):
        """Test confidence score calculation"""
        result = trend_analyzer.analyze_health_trends(degrading_health_data)
        
        # Confidence should be between 0 and 1
        assert 0 <= result['confidence'] <= 1
        
        # With clear degrading trend, confidence should be reasonably high
        assert result['confidence'] > 0.3

    def test_failure_time_projection(self, trend_analyzer):
        """Test projection of failure time"""
        # Create data that should project failure within reasonable timeframe
        now = datetime.now()
        rapid_degradation_data = [
            {'timestamp': now - timedelta(hours=12), 'health_score': 50.0},
            {'timestamp': now - timedelta(hours=8), 'health_score': 45.0},
            {'timestamp': now - timedelta(hours=4), 'health_score': 40.0},
            {'timestamp': now - timedelta(hours=2), 'health_score': 35.0},
            {'timestamp': now, 'health_score': 32.0}
        ]
        
        result = trend_analyzer.analyze_health_trends(rapid_degradation_data)
        
        if result['projected_failure_time']:
            # Should project failure within reasonable timeframe (not too far in future)
            time_to_failure = result['projected_failure_time'] - now
            assert timedelta(hours=1) <= time_to_failure <= timedelta(days=7)


class TestMaintenanceAlert:
    """Test cases for MaintenanceAlert dataclass"""

    def test_alert_creation(self):
        """Test creation of maintenance alert"""
        alert = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.HIGH,
            title="Test Alert",
            description="Test description",
            confidence_score=0.85
        )
        
        assert alert.device_id == "device_001"
        assert alert.alert_type == AlertType.PERFORMANCE_DEGRADATION
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.ACTIVE  # Default status
        assert alert.confidence_score == 0.85
        assert isinstance(alert.created_at, datetime)
        assert alert.id  # Should have auto-generated ID

    def test_alert_to_dict(self):
        """Test conversion of alert to dictionary"""
        alert = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.BATTERY_MAINTENANCE,
            severity=AlertSeverity.CRITICAL,
            title="Battery Alert",
            description="Battery needs replacement",
            recommended_actions=["Replace battery", "Check charging system"],
            affected_systems=["Power System"]
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict['device_id'] == "device_001"
        assert alert_dict['alert_type'] == "battery_maintenance"
        assert alert_dict['severity'] == "critical"
        assert alert_dict['status'] == "active"
        assert alert_dict['recommended_actions'] == ["Replace battery", "Check charging system"]
        assert alert_dict['affected_systems'] == ["Power System"]
        assert 'created_at' in alert_dict


class TestPredictiveAlertService:
    """Test cases for PredictiveAlertService"""

    @pytest.fixture
    def alert_service(self):
        """Create PredictiveAlertService instance"""
        return PredictiveAlertService()

    @pytest.fixture
    def mock_degrading_metrics(self):
        """Mock current metrics showing degradation signs"""
        return {
            'health_score': 45.0,
            'battery_level': 85.0,
            'temperature_max': 78.0,
            'current_mean': 9.5,
            'vibration_std': 2.1
        }

    @pytest.fixture
    def mock_critical_metrics(self):
        """Mock current metrics showing critical conditions"""
        return {
            'health_score': 25.0,
            'battery_level': 15.0,
            'temperature_max': 85.0,
            'current_mean': 12.0,
            'vibration_std': 3.5
        }

    @pytest.fixture
    def mock_degrading_trend(self):
        """Mock trend analysis showing degradation"""
        return {
            'trend_direction': 'degrading',
            'degradation_rate': -1.5,
            'confidence': 0.75,
            'projected_failure_time': datetime.now() + timedelta(hours=36),
            'slope': -2.1,
            'r_squared': 0.82,
            'data_points': 8
        }

    def test_generate_degradation_alert(self, alert_service, mock_degrading_metrics):
        """Test generation of degradation alert"""
        health_history = [
            {'timestamp': datetime.now() - timedelta(hours=24), 'health_score': 75.0},
            {'timestamp': datetime.now() - timedelta(hours=12), 'health_score': 60.0},
            {'timestamp': datetime.now() - timedelta(hours=6), 'health_score': 50.0},
            {'timestamp': datetime.now() - timedelta(hours=2), 'health_score': 45.0}
        ]
        
        with patch.object(alert_service.trend_analyzer, 'analyze_health_trends') as mock_analyze:
            mock_analyze.return_value = {
                'trend_direction': 'degrading',
                'degradation_rate': -1.2,
                'confidence': 0.8,
                'projected_failure_time': datetime.now() + timedelta(hours=24)
            }
            
            alerts = alert_service.generate_alerts_for_device(
                "device_001", health_history, mock_degrading_metrics
            )
        
        assert len(alerts) >= 1
        degradation_alert = next((a for a in alerts if a.alert_type == AlertType.PERFORMANCE_DEGRADATION), None)
        assert degradation_alert is not None
        assert degradation_alert.device_id == "device_001"
        assert degradation_alert.severity in [AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        assert degradation_alert.confidence_score == 0.8

    def test_battery_maintenance_alert(self, alert_service):
        """Test generation of battery maintenance alert"""
        health_history = [{'timestamp': datetime.now(), 'health_score': 50.0}]
        low_battery_metrics = {
            'health_score': 50.0,
            'battery_level': 15.0,  # Low battery
            'temperature_max': 70.0,
            'current_mean': 8.0,
            'vibration_std': 2.0
        }
        
        with patch.object(alert_service.trend_analyzer, 'analyze_health_trends') as mock_analyze:
            mock_analyze.return_value = {
                'trend_direction': 'stable',
                'degradation_rate': 0.0,
                'confidence': 0.6
            }
            
            alerts = alert_service.generate_alerts_for_device(
                "device_001", health_history, low_battery_metrics
            )
        
        battery_alert = next((a for a in alerts if a.alert_type == AlertType.BATTERY_MAINTENANCE), None)
        assert battery_alert is not None
        assert battery_alert.severity == AlertSeverity.HIGH
        assert "battery" in battery_alert.title.lower()
        assert "Battery Management" in battery_alert.affected_systems

    def test_thermal_stress_alert(self, alert_service):
        """Test generation of thermal stress alert"""
        health_history = [{'timestamp': datetime.now(), 'health_score': 60.0}]
        high_temp_metrics = {
            'health_score': 60.0,
            'battery_level': 80.0,
            'temperature_max': 85.0,  # High temperature
            'current_mean': 8.0,
            'vibration_std': 2.0
        }
        
        with patch.object(alert_service.trend_analyzer, 'analyze_health_trends') as mock_analyze:
            mock_analyze.return_value = {
                'trend_direction': 'degrading',
                'degradation_rate': -0.8,
                'confidence': 0.7,
                'projected_failure_time': None  # Add missing key
            }
            
            alerts = alert_service.generate_alerts_for_device(
                "device_001", health_history, high_temp_metrics
            )
        
        thermal_alert = next((a for a in alerts if a.alert_type == AlertType.THERMAL_STRESS), None)
        assert thermal_alert is not None
        assert thermal_alert.severity == AlertSeverity.MEDIUM
        assert "thermal" in thermal_alert.title.lower()
        assert "Cooling System" in thermal_alert.affected_systems

    def test_mechanical_wear_alert(self, alert_service):
        """Test generation of mechanical wear alert"""
        health_history = [{'timestamp': datetime.now(), 'health_score': 70.0}]
        high_vibration_metrics = {
            'health_score': 70.0,
            'battery_level': 80.0,
            'temperature_max': 75.0,
            'current_mean': 8.0,
            'vibration_std': 3.5  # High vibration
        }
        
        with patch.object(alert_service.trend_analyzer, 'analyze_health_trends') as mock_analyze:
            mock_analyze.return_value = {
                'trend_direction': 'stable',
                'degradation_rate': 0.0,
                'confidence': 0.5
            }
            
            alerts = alert_service.generate_alerts_for_device(
                "device_001", health_history, high_vibration_metrics
            )
        
        mechanical_alert = next((a for a in alerts if a.alert_type == AlertType.MECHANICAL_WEAR), None)
        assert mechanical_alert is not None
        assert mechanical_alert.severity == AlertSeverity.MEDIUM
        assert "mechanical" in mechanical_alert.title.lower()
        assert "Mechanical Components" in mechanical_alert.affected_systems

    def test_severity_calculation_critical(self, alert_service, mock_critical_metrics):
        """Test severity calculation for critical conditions"""
        trend_analysis = {
            'degradation_rate': -2.5,  # High degradation rate
            'confidence': 0.9,
            'projected_failure_time': datetime.now() + timedelta(hours=12)
        }
        
        severity = alert_service._calculate_severity(trend_analysis, mock_critical_metrics)
        assert severity == AlertSeverity.CRITICAL

    def test_severity_calculation_high(self, alert_service):
        """Test severity calculation for high severity conditions"""
        trend_analysis = {
            'degradation_rate': -1.2,
            'confidence': 0.8,
            'projected_failure_time': datetime.now() + timedelta(hours=36)
        }
        current_metrics = {'health_score': 50.0}
        
        severity = alert_service._calculate_severity(trend_analysis, current_metrics)
        assert severity == AlertSeverity.HIGH

    def test_alert_acknowledgment(self, alert_service):
        """Test alert acknowledgment functionality"""
        # Create a test alert
        alert = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.MEDIUM,
            title="Test Alert"
        )
        alert_service.active_alerts[alert.id] = alert
        
        # Acknowledge the alert
        success = alert_service.acknowledge_alert(alert.id, "test_user")
        
        assert success is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_at is not None
        assert alert.metadata['acknowledged_by'] == "test_user"

    def test_alert_resolution(self, alert_service):
        """Test alert resolution functionality"""
        # Create a test alert
        alert = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.BATTERY_MAINTENANCE,
            severity=AlertSeverity.HIGH,
            title="Test Alert"
        )
        alert_service.active_alerts[alert.id] = alert
        
        # Resolve the alert
        success = alert_service.resolve_alert(alert.id, "maintenance_team")
        
        assert success is True
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        assert alert.metadata['resolved_by'] == "maintenance_team"
        assert alert.id not in alert_service.active_alerts
        assert alert in alert_service.alert_history

    def test_alert_suppression(self, alert_service):
        """Test alert suppression functionality"""
        device_id = "device_001"
        alert_type = AlertType.PERFORMANCE_DEGRADATION
        
        # Suppress alerts
        success = alert_service.suppress_alerts(device_id, alert_type, suppress_hours=12)
        
        assert success is True
        suppression_key = f"{device_id}_{alert_type.value}"
        assert suppression_key in alert_service.suppression_rules
        
        # Check suppression prevents alert generation
        alert = MaintenanceAlert(
            device_id=device_id,
            alert_type=alert_type,
            severity=AlertSeverity.MEDIUM,
            title="Test Alert"
        )
        
        should_generate = alert_service._should_generate_alert(alert)
        assert should_generate is False

    def test_duplicate_alert_prevention(self, alert_service):
        """Test prevention of duplicate alerts"""
        # Create and add first alert
        alert1 = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.MEDIUM,
            title="First Alert"
        )
        alert_service.active_alerts[alert1.id] = alert1
        
        # Try to create similar alert shortly after
        alert2 = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.HIGH,
            title="Second Alert",
            created_at=alert1.created_at + timedelta(hours=2)  # Within 4-hour window
        )
        
        should_generate = alert_service._should_generate_alert(alert2)
        assert should_generate is False

    def test_get_active_alerts_filtering(self, alert_service):
        """Test filtering of active alerts"""
        # Create test alerts
        alert1 = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.HIGH,
            title="Alert 1"
        )
        alert2 = MaintenanceAlert(
            device_id="device_002",
            alert_type=AlertType.BATTERY_MAINTENANCE,
            severity=AlertSeverity.CRITICAL,
            title="Alert 2"
        )
        alert3 = MaintenanceAlert(
            device_id="device_001",
            alert_type=AlertType.THERMAL_STRESS,
            severity=AlertSeverity.MEDIUM,
            title="Alert 3"
        )
        
        alert_service.active_alerts.update({
            alert1.id: alert1,
            alert2.id: alert2,
            alert3.id: alert3
        })
        
        # Test device filtering
        device_alerts = alert_service.get_active_alerts(device_id="device_001")
        assert len(device_alerts) == 2
        assert all(a.device_id == "device_001" for a in device_alerts)
        
        # Test severity filtering
        critical_alerts = alert_service.get_active_alerts(severity=AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL
        
        # Test combined filtering
        device_high_alerts = alert_service.get_active_alerts(
            device_id="device_001", 
            severity=AlertSeverity.HIGH
        )
        assert len(device_high_alerts) == 1
        assert device_high_alerts[0] == alert1

    def test_alert_statistics(self, alert_service):
        """Test alert statistics generation"""
        # Create test alerts with different severities
        alerts = [
            MaintenanceAlert(device_id="device_001", severity=AlertSeverity.CRITICAL),
            MaintenanceAlert(device_id="device_002", severity=AlertSeverity.HIGH),
            MaintenanceAlert(device_id="device_003", severity=AlertSeverity.MEDIUM),
            MaintenanceAlert(device_id="device_004", severity=AlertSeverity.LOW)
        ]
        
        for alert in alerts:
            alert_service.active_alerts[alert.id] = alert
        
        # Add some resolved alerts to history
        resolved_alert = MaintenanceAlert(
            device_id="device_005",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.RESOLVED,
            created_at=datetime.now() - timedelta(hours=2),  # Ensure positive resolution time
            resolved_at=datetime.now()
        )
        alert_service.alert_history.append(resolved_alert)
        
        stats = alert_service.get_alert_statistics()
        
        assert stats['active_alerts'] == 4
        assert stats['total_generated'] == 5  # 4 active + 1 resolved
        assert stats['severity_breakdown']['critical'] == 1
        assert stats['severity_breakdown']['high'] == 1
        assert stats['severity_breakdown']['medium'] == 1
        assert stats['severity_breakdown']['low'] == 1
        assert stats['average_resolution_time_hours'] >= 0

    def test_low_confidence_alert_rejection(self, alert_service):
        """Test that low confidence trends don't generate alerts"""
        health_history = [{'timestamp': datetime.now(), 'health_score': 50.0}]
        metrics = {'health_score': 50.0}
        
        with patch.object(alert_service.trend_analyzer, 'analyze_health_trends') as mock_analyze:
            mock_analyze.return_value = {
                'trend_direction': 'degrading',
                'degradation_rate': -1.0,
                'confidence': 0.2,  # Low confidence
                'projected_failure_time': datetime.now() + timedelta(hours=24)
            }
            
            alerts = alert_service.generate_alerts_for_device(
                "device_001", health_history, metrics
            )
        
        # Should not generate degradation alert due to low confidence
        degradation_alerts = [a for a in alerts if a.alert_type == AlertType.PERFORMANCE_DEGRADATION]
        assert len(degradation_alerts) == 0

    def test_recommended_actions_by_severity(self, alert_service):
        """Test that recommended actions vary by severity"""
        current_metrics = {'health_score': 50.0}
        
        # Test critical severity actions
        critical_actions = alert_service._get_degradation_recommendations(
            AlertSeverity.CRITICAL, current_metrics
        )
        assert "IMMEDIATE ACTION REQUIRED" in critical_actions
        assert "Stop equipment operation" in critical_actions
        
        # Test high severity actions
        high_actions = alert_service._get_degradation_recommendations(
            AlertSeverity.HIGH, current_metrics
        )
        assert any("24-48 hours" in action for action in high_actions)
        
        # Test medium severity actions
        medium_actions = alert_service._get_degradation_recommendations(
            AlertSeverity.MEDIUM, current_metrics
        )
        assert any("next week" in action for action in medium_actions)

    def test_affected_systems_identification(self, alert_service):
        """Test identification of affected systems based on metrics"""
        metrics = {
            'battery_level': 40.0,  # Should trigger Power System
            'temperature_max': 78.0,  # Should trigger Cooling System
            'current_mean': 11.0,  # Should trigger Electrical System
            'vibration_std': 3.0  # Should trigger Mechanical System
        }
        
        affected_systems = alert_service._identify_affected_systems(metrics)
        
        assert "Power System" in affected_systems
        assert "Cooling System" in affected_systems
        assert "Electrical System" in affected_systems
        assert "Mechanical System" in affected_systems

if __name__ == "__main__":
    pytest.main([__file__])