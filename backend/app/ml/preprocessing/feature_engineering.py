"""
ML Feature Engineering Service

Extracts ML features from telemetry data without modifying existing DataProcessor.
Uses composition pattern for seamless integration.
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass, asdict

from app.services.data_processor import DataProcessor


@dataclass
class FeatureMetadata:
    """Metadata for feature extraction run"""
    extraction_timestamp: str
    feature_version: str
    data_rows_processed: int
    sessions_processed: int
    devices_processed: int
    processing_time_seconds: float
    features_extracted: List[str]


@dataclass
class DeviceFeatures:
    """Feature set for a single device"""
    device_id: str
    
    # Time series features
    current_mean: float
    current_std: float
    current_max: float
    current_min: float
    current_trend_slope: float
    
    # Battery health features
    battery_mean: float
    battery_std: float
    battery_min: float
    battery_degradation_rate: float
    
    # Operational state features
    drilling_time_hours: float
    spinning_time_hours: float
    standby_time_hours: float
    state_transitions: int
    drilling_efficiency: float
    
    # Session features
    total_sessions: int
    avg_session_duration: float
    tagged_sessions_ratio: float
    
    # Temporal patterns
    peak_usage_hour: int
    daily_operation_hours: float
    
    # GPS/Location features
    location_variance: float
    total_distance_km: float
    
    # Data quality indicators
    missing_gps_ratio: float
    missing_ble_ratio: float
    data_quality_score: float


class MLFeatureService:
    """
    ML Feature Engineering Service
    
    Extracts comprehensive features from telemetry data for ML models.
    Operates through composition with existing DataProcessor.
    """
    
    def __init__(self, data_processor: DataProcessor = None):
        """
        Initialize feature engineering service
        
        Args:
            data_processor: Existing DataProcessor instance
        """
        self.data_processor = data_processor
        self.feature_version = "1.0.0"
        
        # Setup feature storage
        current_dir = Path(__file__).parent.parent.parent.parent.parent
        self.features_dir = current_dir / "data" / "ml" / "features"
        self.features_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    async def extract_features(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Extract features from telemetry data
        
        Args:
            force_refresh: Force re-extraction even if cached features exist
            
        Returns:
            Dict containing features and metadata
        """
        start_time = datetime.now()
        
        try:
            # Check if we have data processor
            if not self.data_processor or not hasattr(self.data_processor, 'raw_df'):
                raise ValueError("DataProcessor not available or no data loaded")
            
            if self.data_processor.raw_df is None or self.data_processor.raw_df.empty:
                raise ValueError("No telemetry data available")
            
            # Check for cached features
            if not force_refresh:
                cached_features = await self._load_cached_features()
                if cached_features:
                    self.logger.info("Using cached features")
                    return cached_features
            
            self.logger.info("Starting feature extraction...")
            
            # Get enriched data from DataProcessor
            telemetry_df, sessions_df = self.data_processor._compute_sessions()
            
            # Extract features per device
            device_features = {}
            devices = telemetry_df['device_id'].unique()
            
            for device_id in devices:
                device_data = telemetry_df[telemetry_df['device_id'] == device_id].copy()
                device_sessions = sessions_df[sessions_df['device_id'] == device_id].copy()
                
                features = await self._extract_device_features(device_data, device_sessions)
                device_features[device_id] = features
            
            # Create metadata
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata = FeatureMetadata(
                extraction_timestamp=datetime.now().isoformat(),
                feature_version=self.feature_version,
                data_rows_processed=len(telemetry_df),
                sessions_processed=len(sessions_df),
                devices_processed=len(devices),
                processing_time_seconds=processing_time,
                features_extracted=list(DeviceFeatures.__annotations__.keys())
            )
            
            # Package results
            result = {
                "metadata": asdict(metadata),
                "features": {k: asdict(v) for k, v in device_features.items()}
            }
            
            # Cache results
            await self._cache_features(result)
            
            self.logger.info(f"Feature extraction completed in {processing_time:.2f}s for {len(devices)} devices")
            return result
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            raise
    
    async def _extract_device_features(self, device_data: pd.DataFrame, 
                                     device_sessions: pd.DataFrame) -> DeviceFeatures:
        """Extract features for a single device"""
        
        # Time series features (current consumption)
        current_values = device_data['current_amp'].dropna()
        current_mean = float(current_values.mean())
        current_std = float(current_values.std())
        current_max = float(current_values.max())
        current_min = float(current_values.min())
        
        # Current trend (slope of linear regression)
        if len(current_values) > 1:
            x = np.arange(len(current_values))
            current_trend_slope = float(np.polyfit(x, current_values, 1)[0])
        else:
            current_trend_slope = 0.0
        
        # Battery health features
        battery_values = device_data['battery_level'].dropna()
        battery_mean = float(battery_values.mean())
        battery_std = float(battery_values.std())
        battery_min = float(battery_values.min())
        
        # Battery degradation rate (slope over time)
        if len(battery_values) > 1:
            time_hours = (device_data['timestamp'].max() - device_data['timestamp'].min()).total_seconds() / 3600
            battery_degradation_rate = float((battery_values.iloc[-1] - battery_values.iloc[0]) / max(time_hours, 1))
        else:
            battery_degradation_rate = 0.0
        
        # Operational state features
        drilling_time_hours = len(device_data[device_data['current_amp'] > 4.5]) * 30 / 3600  # 30 sec intervals
        spinning_time_hours = len(device_data[(device_data['current_amp'] > 2.0) & (device_data['current_amp'] <= 4.5)]) * 30 / 3600
        standby_time_hours = len(device_data[(device_data['current_amp'] > 0.5) & (device_data['current_amp'] <= 2.0)]) * 30 / 3600
        
        # State transitions
        device_data['op_state'] = device_data['current_amp'].apply(lambda x: self._get_op_state(x))
        state_changes = int((device_data['op_state'] != device_data['op_state'].shift()).sum())
        
        # Drilling efficiency (drilling time / total operational time)
        total_operational = drilling_time_hours + spinning_time_hours + standby_time_hours
        drilling_efficiency = drilling_time_hours / max(total_operational, 0.001)
        
        # Session features
        total_sessions = len(device_sessions)
        avg_session_duration = float(device_sessions['duration_min'].mean()) if not device_sessions.empty else 0.0
        tagged_sessions_ratio = float(device_sessions['tagged'].mean()) if not device_sessions.empty else 0.0
        
        # Temporal patterns
        device_data['hour'] = device_data['timestamp'].dt.hour
        hourly_usage = device_data.groupby('hour')['current_amp'].mean()
        peak_usage_hour = int(hourly_usage.idxmax()) if not hourly_usage.empty else 12
        
        # Daily operation hours (unique hours with activity per day)
        device_data['date'] = device_data['timestamp'].dt.date
        daily_hours = float(device_data.groupby('date')['hour'].nunique().mean())
        
        # GPS/Location features
        gps_data = device_data[['gps_lat', 'gps_lon']].dropna()
        if not gps_data.empty:
            location_variance = float(gps_data.var().mean())
            
            # Approximate distance traveled
            if len(gps_data) > 1:
                lat_diff = gps_data['gps_lat'].diff().abs()
                lon_diff = gps_data['gps_lon'].diff().abs()
                # Rough approximation: 1 degree ≈ 111 km
                total_distance_km = float((lat_diff + lon_diff).sum() * 111)
            else:
                total_distance_km = 0.0
        else:
            location_variance = 0.0
            total_distance_km = 0.0
        
        # Data quality indicators
        total_records = len(device_data)
        missing_gps_ratio = float(device_data[['gps_lat', 'gps_lon']].isnull().any(axis=1).mean())
        missing_ble_ratio = float(device_data['ble_id'].isnull().mean())
        
        # Overall data quality score (0-1, higher is better)
        data_quality_score = 1.0 - (missing_gps_ratio * 0.4 + missing_ble_ratio * 0.2)
        
        return DeviceFeatures(
            device_id=device_data['device_id'].iloc[0],
            current_mean=current_mean,
            current_std=current_std,
            current_max=current_max,
            current_min=current_min,
            current_trend_slope=current_trend_slope,
            battery_mean=battery_mean,
            battery_std=battery_std,
            battery_min=battery_min,
            battery_degradation_rate=battery_degradation_rate,
            drilling_time_hours=drilling_time_hours,
            spinning_time_hours=spinning_time_hours,
            standby_time_hours=standby_time_hours,
            state_transitions=state_changes,
            drilling_efficiency=drilling_efficiency,
            total_sessions=total_sessions,
            avg_session_duration=avg_session_duration,
            tagged_sessions_ratio=tagged_sessions_ratio,
            peak_usage_hour=peak_usage_hour,
            daily_operation_hours=daily_hours,
            location_variance=location_variance,
            total_distance_km=total_distance_km,
            missing_gps_ratio=missing_gps_ratio,
            missing_ble_ratio=missing_ble_ratio,
            data_quality_score=data_quality_score
        )
    
    def _get_op_state(self, current_amp: float) -> str:
        """Get operational state from current consumption"""
        if current_amp <= 0.5:
            return "OFF"
        elif current_amp <= 2.0:
            return "STANDBY"
        elif current_amp <= 4.5:
            return "SPIN"
        else:
            return "DRILL"
    
    async def _cache_features(self, features: Dict[str, Any]) -> None:
        """Cache features to disk"""
        try:
            cache_file = self.features_dir / f"features_v{self.feature_version}.json"
            with open(cache_file, 'w') as f:
                json.dump(features, f, indent=2)
            self.logger.info(f"Features cached to {cache_file}")
        except Exception as e:
            self.logger.warning(f"Failed to cache features: {e}")
    
    async def _load_cached_features(self) -> Optional[Dict[str, Any]]:
        """Load cached features if available and recent"""
        try:
            cache_file = self.features_dir / f"features_v{self.feature_version}.json"
            if not cache_file.exists():
                return None
            
            # Check if cache is recent (less than 1 hour old)
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age > 3600:  # 1 hour
                return None
            
            with open(cache_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.warning(f"Failed to load cached features: {e}")
            return None
    
    def get_feature_summary(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics of extracted features"""
        if not features or 'features' not in features:
            return {}
        
        device_features = features['features']
        if not device_features:
            return {}
        
        # Calculate fleet-wide statistics
        all_features = list(device_features.values())
        
        summary = {
            "fleet_size": len(all_features),
            "avg_drilling_efficiency": np.mean([f['drilling_efficiency'] for f in all_features]),
            "avg_battery_health": np.mean([f['battery_mean'] for f in all_features]),
            "avg_data_quality": np.mean([f['data_quality_score'] for f in all_features]),
            "total_drilling_hours": sum([f['drilling_time_hours'] for f in all_features]),
            "devices_at_risk": len([f for f in all_features if f['battery_mean'] < 30 or f['data_quality_score'] < 0.7])
        }
        
        return summary