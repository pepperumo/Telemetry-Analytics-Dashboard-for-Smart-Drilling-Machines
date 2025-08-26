"""
Unified Telemetry Service for Real Data Processing
Replaces mock data with actual telemetry analysis across all components
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from app.models.schemas import OperatingState
from app.models.ml_schemas import HealthScoreResponse, RiskLevel, ExplanatoryFactor, MaintenanceAlertResponse

logger = logging.getLogger(__name__)


@dataclass
class TelemetryRecord:
    """Individual telemetry data point"""
    timestamp: datetime
    device_id: str
    seq: int
    current_amp: float
    gps_lat: float
    gps_lon: float
    battery_level: int
    ble_id: Optional[str] = None


@dataclass
class DeviceHealthMetrics:
    """Health metrics calculated from real telemetry data"""
    device_id: str
    health_score: float
    risk_level: RiskLevel
    current_stability: float
    battery_performance: float
    location_consistency: float
    explanatory_factors: List[ExplanatoryFactor]
    last_updated: datetime


class TelemetryService:
    """
    Unified service for processing real telemetry data
    Replaces all mock data generation with actual data analysis
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize with data directory containing CSV files"""
        if data_dir is None:
            # Default to project root data directory
            current_dir = Path(__file__).parent.parent.parent.parent
            self.data_dir = current_dir / "public" / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Dict[str, Any] = {}
        self.health_cache: Dict[str, DeviceHealthMetrics] = {}
        self.cache_timestamp: Optional[datetime] = None
        
        logger.info(f"TelemetryService initialized with data_dir: {self.data_dir}")
    
    def load_telemetry_data(self, force_reload: bool = False) -> bool:
        """
        Load telemetry data from CSV files
        
        Args:
            force_reload: Force reload even if data already loaded
            
        Returns:
            bool: True if data loaded successfully
        """
        if self.raw_data is not None and not force_reload:
            return True
            
        try:
            csv_files = list(self.data_dir.glob("*drilling_sessions*.csv"))
            
            if not csv_files:
                logger.error(f"No drilling session CSV files found in {self.data_dir}")
                return False
                
            # Load the main CSV file
            csv_file = csv_files[0]  # Use first found file
            logger.info(f"Loading telemetry data from {csv_file}")
            
            self.raw_data = pd.read_csv(csv_file)
            
            # Validate and clean data
            if not self._validate_and_clean_data():
                return False
                
            logger.info(f"Loaded {len(self.raw_data)} telemetry records from {len(self.raw_data['device_id'].unique())} devices")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load telemetry data: {e}")
            return False
    
    def _validate_and_clean_data(self) -> bool:
        """Validate and clean loaded telemetry data"""
        if self.raw_data is None:
            return False
            
        try:
            # Convert timestamp to datetime
            self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
            
            # Ensure numeric fields are properly typed
            self.raw_data['current_amp'] = pd.to_numeric(self.raw_data['current_amp'], errors='coerce')
            self.raw_data['battery_level'] = pd.to_numeric(self.raw_data['battery_level'], errors='coerce')
            self.raw_data['gps_lat'] = pd.to_numeric(self.raw_data['gps_lat'], errors='coerce')
            self.raw_data['gps_lon'] = pd.to_numeric(self.raw_data['gps_lon'], errors='coerce')
            
            # Remove rows with invalid data
            initial_count = len(self.raw_data)
            self.raw_data = self.raw_data.dropna(subset=['timestamp', 'device_id', 'current_amp'])
            
            cleaned_count = len(self.raw_data)
            if cleaned_count < initial_count:
                logger.info(f"Cleaned data: removed {initial_count - cleaned_count} invalid records")
                
            return cleaned_count > 0
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False
    
    def get_device_list(self) -> List[str]:
        """Get list of all devices in telemetry data"""
        if not self.load_telemetry_data():
            return []
            
        return sorted(self.raw_data['device_id'].unique().tolist())
    
    def get_device_data(self, device_id: str) -> pd.DataFrame:
        """Get all telemetry data for a specific device"""
        if not self.load_telemetry_data():
            return pd.DataFrame()
            
        return self.raw_data[self.raw_data['device_id'] == device_id].copy()
    
    def calculate_device_health_metrics(self, device_id: str, force_recalculate: bool = False) -> Optional[DeviceHealthMetrics]:
        """
        Calculate comprehensive health metrics for a device using real telemetry data
        
        Args:
            device_id: Device identifier
            force_recalculate: Force recalculation even if cached
            
        Returns:
            DeviceHealthMetrics or None if calculation fails
        """
        # Check cache
        if not force_recalculate and device_id in self.health_cache:
            cached = self.health_cache[device_id]
            # Use cache if less than 5 minutes old
            if datetime.now() - cached.last_updated < timedelta(minutes=5):
                return cached
                
        device_data = self.get_device_data(device_id)
        if device_data.empty:
            return None
            
        try:
            # Calculate current stability (lower variability = higher stability)
            current_values = device_data['current_amp'].dropna()
            if len(current_values) > 1:
                current_stability = max(0, 100 - (np.std(current_values) / np.mean(current_values) * 100))
            else:
                current_stability = 50
                
            # Calculate battery performance
            battery_values = device_data['battery_level'].dropna()
            if len(battery_values) > 0:
                avg_battery = np.mean(battery_values)
                battery_drop = max(battery_values) - min(battery_values) if len(battery_values) > 1 else 0
                # Good battery performance = high average, low drop
                battery_performance = max(0, avg_battery - battery_drop * 2)
            else:
                battery_performance = 50
                
            # Calculate location consistency (GPS reliability)
            gps_data = device_data.dropna(subset=['gps_lat', 'gps_lon'])
            location_consistency = (len(gps_data) / len(device_data)) * 100 if len(device_data) > 0 else 0
            
            # Calculate overall health score (weighted average)
            health_score = (
                current_stability * 0.4 +
                battery_performance * 0.4 + 
                location_consistency * 0.2
            )
            
            # Determine risk level
            if health_score >= 80:
                risk_level = RiskLevel.LOW
            elif health_score >= 60:
                risk_level = RiskLevel.MEDIUM
            elif health_score >= 40:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
                
            # Create explanatory factors
            explanatory_factors = [
                ExplanatoryFactor(
                    feature="Current Draw Stability",
                    value=round(current_stability, 1),
                    importance=0.4,
                    impact="positive" if current_stability > 70 else "negative"
                ),
                ExplanatoryFactor(
                    feature="Battery Performance",
                    value=round(battery_performance, 1),
                    importance=0.4,
                    impact="positive" if battery_performance > 70 else "negative"
                ),
                ExplanatoryFactor(
                    feature="GPS Reliability",
                    value=round(location_consistency, 1),
                    importance=0.2,
                    impact="positive" if location_consistency > 80 else "negative"
                )
            ]
            
            # Create and cache metrics
            metrics = DeviceHealthMetrics(
                device_id=device_id,
                health_score=health_score,
                risk_level=risk_level,
                current_stability=current_stability,
                battery_performance=battery_performance,
                location_consistency=location_consistency,
                explanatory_factors=explanatory_factors,
                last_updated=datetime.now()
            )
            
            self.health_cache[device_id] = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate health metrics for {device_id}: {e}")
            return None
    
    def get_all_health_scores(self, force_recalculate: bool = False) -> List[HealthScoreResponse]:
        """
        Get health scores for all devices using real telemetry analysis
        
        Args:
            force_recalculate: Force recalculation of all health scores
            
        Returns:
            List of HealthScoreResponse objects
        """
        if not self.load_telemetry_data():
            return []
            
        health_scores = []
        devices = self.get_device_list()
        
        for device_id in devices:
            metrics = self.calculate_device_health_metrics(device_id, force_recalculate)
            if metrics:
                # Add some confidence range based on data quality
                data_count = len(self.get_device_data(device_id))
                confidence_range = max(5, 15 - (data_count / 100))  # More data = higher confidence
                
                health_scores.append(HealthScoreResponse(
                    device_id=device_id,
                    health_score=round(metrics.health_score, 1),
                    confidence_interval=[
                        max(0, metrics.health_score - confidence_range),
                        min(100, metrics.health_score + confidence_range)
                    ],
                    risk_level=metrics.risk_level,
                    explanatory_factors=metrics.explanatory_factors,
                    last_calculated=metrics.last_updated
                ))
                
        return sorted(health_scores, key=lambda x: x.device_id)
    
    def generate_maintenance_alerts(self, health_scores: List[HealthScoreResponse]) -> List[MaintenanceAlertResponse]:
        """
        Generate maintenance alerts based on real health analysis
        
        Args:
            health_scores: List of health scores from real data analysis
            
        Returns:
            List of maintenance alerts
        """
        alerts = []
        
        for health_score in health_scores:
            # Only generate alerts for devices with issues
            if health_score.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                
                # Determine alert details based on explanatory factors
                primary_issue = self._identify_primary_issue(health_score)
                
                # Create alert based on primary issue and risk level
                alert = self._create_maintenance_alert(health_score, primary_issue)
                if alert:
                    alerts.append(alert)
                    
        return alerts
    
    def _identify_primary_issue(self, health_score: HealthScoreResponse) -> str:
        """Identify the primary issue from explanatory factors"""
        # Find the factor with highest importance and negative impact
        negative_factors = [f for f in health_score.explanatory_factors if f.impact == "negative"]
        
        if not negative_factors:
            return "general_degradation"
            
        # Sort by importance and return the most important issue
        primary_factor = max(negative_factors, key=lambda x: x.importance)
        
        if "Current" in primary_factor.feature:
            return "electrical_performance"
        elif "Battery" in primary_factor.feature:
            return "battery_maintenance"
        elif "GPS" in primary_factor.feature:
            return "communication_issues"
        else:
            return "general_degradation"
    
    def _create_maintenance_alert(self, health_score: HealthScoreResponse, issue_type: str) -> Optional[MaintenanceAlertResponse]:
        """Create a maintenance alert based on health score and issue type"""
        try:
            from app.models.ml_schemas import AlertType, AlertSeverity, AlertStatus
            
            # Map issue types to alert details
            alert_configs = {
                "electrical_performance": {
                    "type": AlertType.PERFORMANCE_DEGRADATION,
                    "title": "Electrical Performance Degradation",
                    "description": "Current draw patterns indicate potential electrical issues",
                    "actions": ["Check electrical connections", "Inspect motor windings", "Verify power supply"]
                },
                "battery_maintenance": {
                    "type": AlertType.BATTERY_MAINTENANCE,
                    "title": "Battery Maintenance Required",
                    "description": "Battery performance is below optimal levels",
                    "actions": ["Check battery connections", "Test battery capacity", "Replace if necessary"]
                },
                "communication_issues": {
                    "type": AlertType.EQUIPMENT_FAILURE_RISK,
                    "title": "Communication System Issues", 
                    "description": "GPS/communication reliability is compromised",
                    "actions": ["Check antenna connections", "Verify GPS module", "Test communication range"]
                },
                "general_degradation": {
                    "type": AlertType.EQUIPMENT_FAILURE_RISK,
                    "title": "General Equipment Degradation",
                    "description": "Multiple systems showing degraded performance",
                    "actions": ["Comprehensive equipment inspection", "Check all systems", "Schedule maintenance"]
                }
            }
            
            config = alert_configs.get(issue_type, alert_configs["general_degradation"])
            
            # Map risk level to severity
            severity_map = {
                RiskLevel.MEDIUM: AlertSeverity.MEDIUM,
                RiskLevel.HIGH: AlertSeverity.HIGH,
                RiskLevel.CRITICAL: AlertSeverity.CRITICAL
            }
            
            severity = severity_map.get(health_score.risk_level, AlertSeverity.MEDIUM)
            
            # Calculate predicted failure time based on health score
            if health_score.health_score < 30:
                failure_time = datetime.now() + timedelta(hours=24)  # 1 day
            elif health_score.health_score < 50:
                failure_time = datetime.now() + timedelta(hours=72)  # 3 days
            else:
                failure_time = datetime.now() + timedelta(days=7)   # 1 week
                
            return MaintenanceAlertResponse(
                id=f"alert_{health_score.device_id}_{int(datetime.now().timestamp())}",
                device_id=health_score.device_id,
                alert_type=config["type"],
                severity=severity,
                status=AlertStatus.ACTIVE,
                title=config["title"],
                description=config["description"],
                predicted_failure_time=failure_time,
                confidence_score=min(0.95, (100 - health_score.health_score) / 100),
                recommended_actions=config["actions"],
                affected_systems=[f.feature for f in health_score.explanatory_factors if f.impact == "negative"],
                created_at=datetime.now(),
                acknowledged_at=None,
                resolved_at=None,
                metadata={
                    "health_score": health_score.health_score,
                    "risk_level": health_score.risk_level.value,
                    "analysis_based": "real_telemetry_data"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create maintenance alert for {health_score.device_id}: {e}")
            return None
    
    def get_operating_states_timeline(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Get operating states timeline from real current draw data"""
        if not self.load_telemetry_data():
            return {}
            
        data = self.raw_data if device_id is None else self.get_device_data(device_id)
        
        # Classify operating states based on current draw
        def classify_state(current_amp: float) -> str:
            if pd.isna(current_amp) or current_amp <= 0:
                return "unknown"
            elif current_amp < 2.0:
                return "idle"
            elif current_amp < 5.0:
                return "low_power"
            elif current_amp < 8.0:
                return "normal_operation"
            else:
                return "high_power"
                
        data = data.copy()
        data['operating_state'] = data['current_amp'].apply(classify_state)
        
        # Calculate state distribution
        state_counts = data['operating_state'].value_counts().to_dict()
        total_records = len(data)
        
        state_percentages = {
            state: (count / total_records * 100) if total_records > 0 else 0
            for state, count in state_counts.items()
        }
        
        return {
            "state_distribution": state_percentages,
            "total_records": total_records,
            "timeline_data": data[['timestamp', 'device_id', 'current_amp', 'operating_state']].to_dict('records')
        }
    
    def get_anomaly_detection_results(self) -> Dict[str, Any]:
        """Detect anomalies in real telemetry data"""
        if not self.load_telemetry_data():
            return {}
            
        anomalies = {
            "low_battery": [],
            "high_current": [],
            "missing_gps": [],
            "communication_gaps": []
        }
        
        # Low battery anomalies
        low_battery = self.raw_data[self.raw_data['battery_level'] < 20]
        anomalies["low_battery"] = low_battery[['device_id', 'timestamp', 'battery_level']].to_dict('records')
        
        # High current anomalies (potential overload)
        high_current = self.raw_data[self.raw_data['current_amp'] > 10]
        anomalies["high_current"] = high_current[['device_id', 'timestamp', 'current_amp']].to_dict('records')
        
        # Missing GPS data
        missing_gps = self.raw_data[self.raw_data['gps_lat'].isna() | self.raw_data['gps_lon'].isna()]
        anomalies["missing_gps"] = missing_gps[['device_id', 'timestamp', 'seq']].to_dict('records')
        
        # Communication gaps (sequence number jumps)
        for device_id in self.raw_data['device_id'].unique():
            device_data = self.raw_data[self.raw_data['device_id'] == device_id].sort_values('seq')
            seq_diffs = device_data['seq'].diff()
            gaps = device_data[seq_diffs > 1]
            
            for _, gap in gaps.iterrows():
                anomalies["communication_gaps"].append({
                    "device_id": device_id,
                    "timestamp": gap['timestamp'],
                    "gap_size": int(seq_diffs.loc[gap.name])
                })
                
        return anomalies
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of loaded telemetry data"""
        if not self.load_telemetry_data():
            return {}
            
        return {
            "total_records": len(self.raw_data),
            "devices_count": len(self.raw_data['device_id'].unique()),
            "date_range": {
                "start": self.raw_data['timestamp'].min().isoformat(),
                "end": self.raw_data['timestamp'].max().isoformat()
            },
            "data_quality": {
                "complete_records": len(self.raw_data.dropna()),
                "missing_gps": len(self.raw_data[self.raw_data['gps_lat'].isna()]),
                "zero_current": len(self.raw_data[self.raw_data['current_amp'] <= 0])
            }
        }