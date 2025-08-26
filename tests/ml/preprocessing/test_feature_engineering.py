"""
Unit tests for ML Feature Engineering Service

Tests cover feature extraction accuracy, performance, error handling,
and integration with existing DataProcessor.
"""

import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from backend.app.services.data_processor import DataProcessor
from backend.app.ml.preprocessing.feature_engineering import MLFeatureService, DeviceFeatures, FeatureMetadata
from .test_fixtures import (
    sample_telemetry_data, mock_data_processor, ml_feature_service,
    expected_feature_structure, edge_case_data
)


class TestMLFeatureService:
    """Test cases for MLFeatureService"""
    
    @pytest.mark.asyncio
    async def test_feature_extraction_basic(self, ml_feature_service):
        """Test basic feature extraction functionality"""
        
        # Extract features
        result = await ml_feature_service.extract_features()
        
        # Validate structure
        assert 'metadata' in result
        assert 'features' in result
        assert isinstance(result['metadata'], dict)
        assert isinstance(result['features'], dict)
        
        # Check metadata
        metadata = result['metadata']
        assert 'extraction_timestamp' in metadata
        assert 'feature_version' in metadata
        assert 'processing_time_seconds' in metadata
        assert metadata['data_rows_processed'] > 0
        assert metadata['devices_processed'] == 3  # From fixture
        
        # Check features
        features = result['features']
        assert len(features) == 3  # 3 devices in fixture
        
        for device_id, device_features in features.items():
            assert device_features['device_id'] == device_id
            assert isinstance(device_features['current_mean'], float)
            assert isinstance(device_features['drilling_time_hours'], float)
            assert isinstance(device_features['data_quality_score'], float)
            assert 0 <= device_features['data_quality_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_feature_types_and_ranges(self, ml_feature_service):
        """Test that all features have correct types and reasonable ranges"""
        
        result = await ml_feature_service.extract_features()
        features = result['features']
        
        for device_id, device_features in features.items():
            # Current consumption features
            assert device_features['current_mean'] >= 0
            assert device_features['current_std'] >= 0
            assert device_features['current_max'] >= device_features['current_min']
            
            # Battery features
            assert 0 <= device_features['battery_mean'] <= 100
            assert 0 <= device_features['battery_min'] <= 100
            assert device_features['battery_std'] >= 0
            
            # Time features
            assert device_features['drilling_time_hours'] >= 0
            assert device_features['spinning_time_hours'] >= 0
            assert device_features['standby_time_hours'] >= 0
            
            # Efficiency (0-1 ratio)
            assert 0 <= device_features['drilling_efficiency'] <= 1
            
            # Sessions
            assert device_features['total_sessions'] >= 0
            assert device_features['avg_session_duration'] >= 0
            
            # Temporal features
            assert 0 <= device_features['peak_usage_hour'] <= 23
            assert device_features['daily_operation_hours'] >= 0
            
            # Data quality ratios (0-1)
            assert 0 <= device_features['missing_gps_ratio'] <= 1
            assert 0 <= device_features['missing_ble_ratio'] <= 1
            assert 0 <= device_features['data_quality_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, ml_feature_service):
        """Test that feature extraction meets performance requirements"""
        
        start_time = datetime.now()
        result = await ml_feature_service.extract_features()
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within 30 seconds (requirement)
        assert processing_time < 30
        
        # Metadata should track processing time accurately
        metadata_time = result['metadata']['processing_time_seconds']
        assert abs(processing_time - metadata_time) < 1  # Within 1 second
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, ml_feature_service):
        """Test feature caching and loading"""
        
        # First extraction (no cache)
        result1 = await ml_feature_service.extract_features(force_refresh=True)
        time1 = result1['metadata']['processing_time_seconds']
        
        # Second extraction (should use cache)
        result2 = await ml_feature_service.extract_features()
        
        # Results should be identical
        assert result1['features'] == result2['features']
        
        # Cached version should be available
        assert ml_feature_service.features_dir.exists()
        cache_files = list(ml_feature_service.features_dir.glob("*.json"))
        assert len(cache_files) > 0
    
    @pytest.mark.asyncio
    async def test_integration_with_data_processor(self, mock_data_processor):
        """Test integration with existing DataProcessor"""
        
        # Create service with real DataProcessor
        service = MLFeatureService(mock_data_processor)
        
        # Should initialize without error
        assert service.data_processor is not None
        
        # Should extract features successfully
        result = await service.extract_features()
        assert 'features' in result
        assert len(result['features']) > 0
        
        # Should not modify original DataProcessor
        assert mock_data_processor.raw_df is not None
        assert len(mock_data_processor.raw_df) > 0
    
    def test_operational_state_classification(self, ml_feature_service):
        """Test operational state classification logic"""
        
        # Test state boundaries
        assert ml_feature_service._get_op_state(0.0) == "OFF"
        assert ml_feature_service._get_op_state(0.5) == "OFF"
        assert ml_feature_service._get_op_state(1.0) == "STANDBY"
        assert ml_feature_service._get_op_state(2.0) == "STANDBY"
        assert ml_feature_service._get_op_state(3.0) == "SPIN"
        assert ml_feature_service._get_op_state(4.5) == "SPIN"
        assert ml_feature_service._get_op_state(5.0) == "DRILL"
        assert ml_feature_service._get_op_state(10.0) == "DRILL"
    
    @pytest.mark.asyncio
    async def test_error_handling_no_data_processor(self):
        """Test error handling when no DataProcessor is provided"""
        
        service = MLFeatureService(None)
        
        with pytest.raises(ValueError, match="DataProcessor not available"):
            await service.extract_features()
    
    @pytest.mark.asyncio
    async def test_error_handling_empty_data(self, mock_data_processor):
        """Test error handling with empty data"""
        
        # Clear the data
        mock_data_processor.raw_df = pd.DataFrame()
        
        service = MLFeatureService(mock_data_processor)
        
        with pytest.raises(ValueError, match="No telemetry data available"):
            await service.extract_features()
    
    def test_feature_summary_calculation(self, ml_feature_service):
        """Test feature summary statistics calculation"""
        
        # Mock features data
        mock_features = {
            'metadata': {'devices_processed': 2},
            'features': {
                'device_001': {
                    'drilling_efficiency': 0.8,
                    'battery_mean': 75.0,
                    'data_quality_score': 0.9,
                    'drilling_time_hours': 5.0
                },
                'device_002': {
                    'drilling_efficiency': 0.6,
                    'battery_mean': 25.0,  # Below 30 threshold
                    'data_quality_score': 0.9,
                    'drilling_time_hours': 3.0
                }
            }
        }
        
        summary = ml_feature_service.get_feature_summary(mock_features)
        
        assert summary['fleet_size'] == 2
        assert summary['avg_drilling_efficiency'] == 0.7  # (0.8 + 0.6) / 2
        assert summary['avg_battery_health'] == 50.0  # (75 + 25) / 2
        assert summary['total_drilling_hours'] == 8.0  # 5 + 3
        assert summary['devices_at_risk'] == 1  # device_002 has battery < 30


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_single_record_device(self, edge_case_data):
        """Test feature extraction with single record"""
        
        # Create DataProcessor with single record
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as temp_dir:
            processor = DataProcessor(str(temp_dir))
            processor.raw_df = edge_case_data['single_record'].copy()
            processor.raw_df['timestamp'] = pd.to_datetime(processor.raw_df['timestamp'])
            
            service = MLFeatureService(processor)
            service.features_dir = Path(temp_dir) / "features"
            service.features_dir.mkdir(exist_ok=True)
            
            result = await service.extract_features()
            
            # Should handle single record gracefully
            assert len(result['features']) == 1
            device_features = list(result['features'].values())[0]
            
            # Trend slope should be 0 for single record
            assert device_features['current_trend_slope'] == 0.0
            assert device_features['battery_degradation_rate'] == 0.0
    
    @pytest.mark.asyncio
    async def test_missing_gps_data(self, edge_case_data):
        """Test handling of missing GPS data"""
        
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as temp_dir:
            processor = DataProcessor(str(temp_dir))
            processor.raw_df = edge_case_data['missing_gps'].copy()
            processor.raw_df['timestamp'] = pd.to_datetime(processor.raw_df['timestamp'])
            
            service = MLFeatureService(processor)
            service.features_dir = Path(temp_dir) / "features"
            service.features_dir.mkdir(exist_ok=True)
            
            result = await service.extract_features()
            
            device_features = list(result['features'].values())[0]
            
            # Should handle missing GPS gracefully
            assert device_features['missing_gps_ratio'] == 1.0  # All GPS missing
            assert device_features['location_variance'] == 0.0
            assert device_features['total_distance_km'] == 0.0
    
    @pytest.mark.asyncio
    async def test_zero_current_data(self, edge_case_data):
        """Test handling of all-zero current data"""
        
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as temp_dir:
            processor = DataProcessor(str(temp_dir))
            processor.raw_df = edge_case_data['zero_current'].copy()
            processor.raw_df['timestamp'] = pd.to_datetime(processor.raw_df['timestamp'])
            
            service = MLFeatureService(processor)
            service.features_dir = Path(temp_dir) / "features"
            service.features_dir.mkdir(exist_ok=True)
            
            result = await service.extract_features()
            
            device_features = list(result['features'].values())[0]
            
            # Should handle zero current gracefully
            assert device_features['current_mean'] == 0.0
            assert device_features['drilling_time_hours'] == 0.0
            assert device_features['spinning_time_hours'] == 0.0
            assert device_features['standby_time_hours'] == 0.0
            assert device_features['drilling_efficiency'] == 0.0


class TestPerformanceAndRegression:
    """Performance and regression tests"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self):
        """Test performance with larger dataset"""
        
        # Create larger dataset (simulating 100 sessions requirement)
        large_data = []
        for device in range(5):  # 5 devices
            for session in range(20):  # 20 sessions each
                for minute in range(60):  # 1 hour sessions
                    large_data.append({
                        'timestamp': f'2025-07-01T{session:02d}:{minute:02d}:00Z',
                        'device_id': f'device_{device:03d}',
                        'seq': len(large_data) + 1,
                        'current_amp': np.random.normal(5.0, 2.0),
                        'gps_lat': 52.393297 + np.random.normal(0, 0.001),
                        'gps_lon': 13.265675 + np.random.normal(0, 0.001),
                        'battery_level': np.random.uniform(20, 100),
                        'ble_id': 'F4:12:FA:6C:9D:21'
                    })
        
        df = pd.DataFrame(large_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as temp_dir:
            processor = DataProcessor(str(temp_dir))
            processor.raw_df = df
            
            service = MLFeatureService(processor)
            service.features_dir = Path(temp_dir) / "features"
            service.features_dir.mkdir(exist_ok=True)
            
            start_time = datetime.now()
            result = await service.extract_features()
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Should complete within 30 seconds (requirement)
            assert processing_time < 30
            
            # Should process all devices
            assert len(result['features']) == 5
            
            # Should maintain data quality
            for device_features in result['features'].values():
                assert device_features['data_quality_score'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])