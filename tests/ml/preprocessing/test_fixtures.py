"""
Test fixtures for ML feature engineering tests
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from backend.app.services.data_processor import DataProcessor
from backend.app.ml.preprocessing.feature_engineering import MLFeatureService, DeviceFeatures


@pytest.fixture
def sample_telemetry_data():
    """Create sample telemetry data for testing"""
    
    # Create realistic telemetry data for 3 devices over 2 days
    start_time = datetime(2025, 7, 1, 9, 0, 0)
    data = []
    
    devices = ['device_001', 'device_002', 'device_003']
    
    for device_id in devices:
        for day in range(2):
            for hour in range(8):  # 8 hours of operation per day
                for minute in range(0, 60, 1):  # Every minute (30-second intervals)
                    timestamp = start_time + timedelta(days=day, hours=hour, minutes=minute)
                    seq = len(data) + 1
                    
                    # Simulate realistic drilling patterns
                    if minute < 15:  # First 15 min: drilling
                        current_amp = np.random.normal(6.5, 1.0)
                        battery_drain = 0.5
                    elif minute < 30:  # Next 15 min: spinning
                        current_amp = np.random.normal(3.5, 0.5)
                        battery_drain = 0.2
                    elif minute < 45:  # Next 15 min: standby
                        current_amp = np.random.normal(1.5, 0.3)
                        battery_drain = 0.1
                    else:  # Last 15 min: off
                        current_amp = np.random.normal(0.2, 0.1)
                        battery_drain = 0.05
                    
                    # Battery level decreases over time
                    base_battery = 100 - (day * 20) - (hour * 2) - (minute * battery_drain)
                    battery_level = max(10, base_battery + np.random.normal(0, 2))
                    
                    # GPS coordinates (Berlin area with some movement)
                    base_lat = 52.393297 + np.random.normal(0, 0.001)
                    base_lon = 13.265675 + np.random.normal(0, 0.001)
                    
                    # Some missing data for testing
                    if np.random.random() < 0.05:  # 5% missing GPS
                        base_lat = None
                        base_lon = None
                    
                    ble_id = "F4:12:FA:6C:9D:21" if np.random.random() > 0.1 else None  # 10% missing BLE
                    
                    data.append({
                        'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'device_id': device_id,
                        'seq': seq,
                        'current_amp': max(0, current_amp),
                        'gps_lat': base_lat,
                        'gps_lon': base_lon,
                        'battery_level': max(0, min(100, battery_level)),
                        'ble_id': ble_id
                    })
    
    return pd.DataFrame(data)


@pytest.fixture
def mock_data_processor(sample_telemetry_data):
    """Create a mock DataProcessor with sample data"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create temporary CSV file
        csv_path = Path(temp_dir) / "test_data.csv"
        sample_telemetry_data.to_csv(csv_path, index=False)
        
        # Create DataProcessor with temp data
        processor = DataProcessor(str(temp_dir))
        processor.raw_df = sample_telemetry_data.copy()
        processor.raw_df['timestamp'] = pd.to_datetime(processor.raw_df['timestamp'])
        
        yield processor


@pytest.fixture
def ml_feature_service(mock_data_processor):
    """Create MLFeatureService with mock data"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = MLFeatureService(mock_data_processor)
        # Override features directory to use temp directory
        service.features_dir = Path(temp_dir) / "features"
        service.features_dir.mkdir(exist_ok=True)
        
        yield service


@pytest.fixture
def expected_feature_structure():
    """Expected structure of extracted features"""
    return {
        'device_id': str,
        'current_mean': float,
        'current_std': float,
        'current_max': float,
        'current_min': float,
        'current_trend_slope': float,
        'battery_mean': float,
        'battery_std': float,
        'battery_min': float,
        'battery_degradation_rate': float,
        'drilling_time_hours': float,
        'spinning_time_hours': float,
        'standby_time_hours': float,
        'state_transitions': int,
        'drilling_efficiency': float,
        'total_sessions': int,
        'avg_session_duration': float,
        'tagged_sessions_ratio': float,
        'peak_usage_hour': int,
        'daily_operation_hours': float,
        'location_variance': float,
        'total_distance_km': float,
        'missing_gps_ratio': float,
        'missing_ble_ratio': float,
        'data_quality_score': float
    }


@pytest.fixture
def edge_case_data():
    """Create edge case data for testing error handling"""
    
    # Single record
    single_record = pd.DataFrame([{
        'timestamp': '2025-07-01T09:00:00Z',
        'device_id': 'single_device',
        'seq': 1,
        'current_amp': 5.0,
        'gps_lat': 52.393297,
        'gps_lon': 13.265675,
        'battery_level': 50.0,
        'ble_id': 'F4:12:FA:6C:9D:21'
    }])
    
    # All missing GPS
    missing_gps = pd.DataFrame([{
        'timestamp': f'2025-07-01T09:{i:02d}:00Z',
        'device_id': 'missing_gps_device',
        'seq': i + 1,
        'current_amp': 5.0,
        'gps_lat': None,
        'gps_lon': None,
        'battery_level': 50.0,
        'ble_id': 'F4:12:FA:6C:9D:21'
    } for i in range(10)])
    
    # All zeros current
    zero_current = pd.DataFrame([{
        'timestamp': f'2025-07-01T09:{i:02d}:00Z',
        'device_id': 'zero_current_device',
        'seq': i + 1,
        'current_amp': 0.0,
        'gps_lat': 52.393297,
        'gps_lon': 13.265675,
        'battery_level': 50.0,
        'ble_id': 'F4:12:FA:6C:9D:21'
    } for i in range(10)])
    
    return {
        'single_record': single_record,
        'missing_gps': missing_gps,
        'zero_current': zero_current
    }