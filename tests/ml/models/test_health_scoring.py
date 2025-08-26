"""
Unit tests for Health Scoring Service

Tests cover health scoring model training, prediction, and integration
with the ML feature engineering pipeline.
"""

import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from unittest.mock import Mock, patch

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from backend.app.services.data_processor import DataProcessor
from backend.app.ml.models.health_scoring import HealthScoringService, HealthScore, ModelMetadata
from backend.app.ml.services import MLService


class TestHealthScoringService:
    """Test cases for HealthScoringService"""
    
    @pytest.fixture
    def sample_features_data(self):
        """Create sample features data for testing"""
        return {
            'features': {
                'device_001': {
                    'current_mean': 8.5,
                    'current_std': 2.1,
                    'current_max': 12.3,
                    'voltage_mean': 24.2,
                    'voltage_std': 0.8,
                    'power_mean': 205.7,
                    'power_max': 297.5,
                    'temperature_mean': 28.5,
                    'temperature_max': 35.2,
                    'vibration_mean': 0.3,
                    'vibration_max': 0.8,
                    'speed_mean': 2400.0,
                    'speed_std': 150.0,
                    'pressure_mean': 12.5,
                    'pressure_max': 18.7,
                    'flow_rate_mean': 45.2,
                    'torque_mean': 85.3,
                    'torque_max': 120.5,
                    'battery_level_mean': 85.2,
                    'battery_level_min': 68.5,
                    'operational_efficiency': 0.92,
                    'data_quality_score': 0.98,
                    'session_count': 12,
                    'total_runtime_hours': 24.5
                },
                'device_002': {
                    'current_mean': 15.2,
                    'current_std': 4.3,
                    'current_max': 22.1,
                    'voltage_mean': 23.8,
                    'voltage_std': 1.2,
                    'power_mean': 361.8,
                    'power_max': 525.6,
                    'temperature_mean': 45.2,
                    'temperature_max': 62.8,
                    'vibration_mean': 0.8,
                    'vibration_max': 1.5,
                    'speed_mean': 2200.0,
                    'speed_std': 250.0,
                    'pressure_mean': 15.8,
                    'pressure_max': 24.3,
                    'flow_rate_mean': 52.7,
                    'torque_mean': 112.8,
                    'torque_max': 165.2,
                    'battery_level_mean': 65.5,
                    'battery_level_min': 42.3,
                    'operational_efficiency': 0.78,
                    'data_quality_score': 0.94,
                    'session_count': 18,
                    'total_runtime_hours': 35.7
                },
                'device_003': {
                    'current_mean': 6.8,
                    'current_std': 1.5,
                    'current_max': 9.2,
                    'voltage_mean': 24.5,
                    'voltage_std': 0.5,
                    'power_mean': 166.6,
                    'power_max': 225.4,
                    'temperature_mean': 22.8,
                    'temperature_max': 28.5,
                    'vibration_mean': 0.2,
                    'vibration_max': 0.4,
                    'speed_mean': 2500.0,
                    'speed_std': 100.0,
                    'pressure_mean': 10.2,
                    'pressure_max': 14.5,
                    'flow_rate_mean': 38.9,
                    'torque_mean': 72.5,
                    'torque_max': 95.8,
                    'battery_level_mean': 92.8,
                    'battery_level_min': 88.2,
                    'operational_efficiency': 0.96,
                    'data_quality_score': 0.99,
                    'session_count': 8,
                    'total_runtime_hours': 16.3
                }
            },
            'metadata': {
                'extraction_time': datetime.now().isoformat()
            }
        }
    
    @pytest.fixture
    def health_scoring_service(self):
        """Create HealthScoringService instance for testing"""
        return HealthScoringService(model_storage_path="data/ml/models/test")
    
    @pytest.mark.asyncio
    async def test_synthetic_health_score_calculation(self, health_scoring_service):
        """Test synthetic health score calculation logic"""
        
        # Test healthy equipment
        healthy_features = {
            'battery_level_mean': 90.0,
            'battery_level_min': 85.0,
            'temperature_mean': 25.0,
            'temperature_max': 30.0,
            'vibration_mean': 0.2,
            'vibration_max': 0.4,
            'current_mean': 8.0,
            'current_std': 1.5,
            'operational_efficiency': 0.95
        }
        
        healthy_score = health_scoring_service._calculate_synthetic_health_score(healthy_features)
        assert 0.8 <= healthy_score <= 1.0, f"Healthy equipment should have high score, got {healthy_score}"
        
        # Test unhealthy equipment
        unhealthy_features = {
            'battery_level_mean': 40.0,
            'battery_level_min': 25.0,
            'temperature_mean': 70.0,
            'temperature_max': 85.0,
            'vibration_mean': 1.2,
            'vibration_max': 2.0,
            'current_mean': 20.0,
            'current_std': 8.0,
            'operational_efficiency': 0.5
        }
        
        unhealthy_score = health_scoring_service._calculate_synthetic_health_score(unhealthy_features)
        assert 0.0 <= unhealthy_score <= 0.6, f"Unhealthy equipment should have low score, got {unhealthy_score}"
    
    @pytest.mark.asyncio
    async def test_model_training(self, health_scoring_service, sample_features_data):
        """Test health scoring model training"""
        
        # Train model
        model_metadata = await health_scoring_service.train_model(sample_features_data)
        
        # Verify training results
        assert isinstance(model_metadata, ModelMetadata)
        assert model_metadata.model_version == "1.0.0"
        assert model_metadata.feature_count == 24
        assert model_metadata.training_samples == 3
        assert isinstance(model_metadata.training_date, datetime)
        
        # Verify models are trained
        assert health_scoring_service.primary_model is not None
        assert health_scoring_service.backup_model is not None
        assert health_scoring_service.scaler is not None
        assert health_scoring_service.feature_names is not None
        assert len(health_scoring_service.feature_names) == 24
    
    @pytest.mark.asyncio
    async def test_health_score_calculation(self, health_scoring_service, sample_features_data):
        """Test health score calculation for devices"""
        
        # Train model first
        await health_scoring_service.train_model(sample_features_data)
        
        # Calculate health scores
        health_scores = await health_scoring_service.calculate_health_scores(sample_features_data)
        
        # Verify results
        assert len(health_scores) == 3
        assert 'device_001' in health_scores
        assert 'device_002' in health_scores
        assert 'device_003' in health_scores
        
        for device_id, health_score in health_scores.items():
            assert isinstance(health_score, HealthScore)
            assert health_score.device_id == device_id
            assert 0 <= health_score.health_score <= 100
            assert health_score.risk_level in ['low', 'medium', 'high', 'critical']
            assert len(health_score.confidence_interval) == 2
            assert health_score.confidence_interval[0] <= health_score.confidence_interval[1]
            assert len(health_score.explanatory_factors) <= 3
            assert health_score.model_version == "1.0.0"
    
    def test_risk_level_determination(self, health_scoring_service):
        """Test risk level determination based on health scores"""
        
        assert health_scoring_service._determine_risk_level(0.1) == 'critical'
        assert health_scoring_service._determine_risk_level(0.3) == 'high'
        assert health_scoring_service._determine_risk_level(0.6) == 'medium'
        assert health_scoring_service._determine_risk_level(0.9) == 'low'
    
    def test_feature_impact_interpretation(self, health_scoring_service):
        """Test feature impact interpretation"""
        
        # Battery features
        assert "critical" in health_scoring_service._interpret_feature_impact('battery_level_mean', 30.0).lower()
        assert "good" in health_scoring_service._interpret_feature_impact('battery_level_mean', 90.0).lower()
        
        # Temperature features
        assert "concerning" in health_scoring_service._interpret_feature_impact('temperature_max', 70.0).lower()
        assert "normal" in health_scoring_service._interpret_feature_impact('temperature_mean', 25.0).lower()
        
        # Vibration features
        assert "mechanical" in health_scoring_service._interpret_feature_impact('vibration_max', 1.5).lower()
        assert "normal" in health_scoring_service._interpret_feature_impact('vibration_mean', 0.2).lower()
    
    @pytest.mark.asyncio
    async def test_model_persistence(self, health_scoring_service, sample_features_data):
        """Test model saving and loading"""
        
        # Train and save model
        await health_scoring_service.train_model(sample_features_data)
        await health_scoring_service.save_models()
        
        # Create new service instance and load models
        new_service = HealthScoringService(model_storage_path="data/ml/models/test")
        loaded = await new_service.load_models()
        
        assert loaded == True
        assert new_service.primary_model is not None
        assert new_service.scaler is not None
        assert new_service.feature_names is not None
        assert len(new_service.feature_names) == 24
    
    def test_model_status(self, health_scoring_service):
        """Test model status reporting"""
        
        status = health_scoring_service.get_model_status()
        
        assert isinstance(status, dict)
        assert 'model_loaded' in status
        assert 'model_version' in status
        assert 'feature_count' in status
        assert status['model_version'] == "1.0.0"
        assert status['feature_count'] == 0  # No model loaded initially


class TestMLServiceHealthScoring:
    """Test health scoring integration with MLService"""
    
    @pytest.fixture
    def mock_data_processor(self):
        """Create mock DataProcessor for testing"""
        processor = Mock(spec=DataProcessor)
        
        # Create sample telemetry data with more devices for meaningful R² calculation
        sample_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=200, freq='h'),
            'device_id': (['device_001'] * 35 + ['device_002'] * 30 + ['device_003'] * 25 + 
                         ['device_004'] * 30 + ['device_005'] * 25 + ['device_006'] * 20 + 
                         ['device_007'] * 20 + ['device_008'] * 15),
            'current_amp': np.random.normal(10, 3, 200),
            'voltage': np.random.normal(24, 1, 200),
            'temperature': np.random.normal(30, 5, 200),
            'vibration': np.random.normal(0.5, 0.2, 200),
            'speed': np.random.normal(2500, 200, 200),
            'pressure': np.random.normal(12, 3, 200),
            'flow_rate': np.random.normal(45, 8, 200),
            'torque': np.random.normal(80, 15, 200),
            'battery_level': np.random.normal(80, 15, 200),
            'gps_lat': np.random.uniform(40.0, 41.0, 200),
            'gps_lon': np.random.uniform(-74.0, -73.0, 200),
            'session_id': np.random.randint(1, 40, 200),
            'ble_id': ['ble_' + str(i) for i in range(200)],
            'op_state': ['drilling'] * 100 + ['spinning'] * 60 + ['standby'] * 40
        })
        
        # Create session data to match DataProcessor output (more devices)
        sessions_data = pd.DataFrame({
            'session_id': list(range(1, 13)),
            'device_id': ['device_001', 'device_001', 'device_002', 'device_002', 'device_003', 'device_003',
                         'device_004', 'device_005', 'device_006', 'device_007', 'device_008', 'device_008'],
            'start_time': pd.date_range('2024-01-01', periods=12, freq='D'),
            'end_time': pd.date_range('2024-01-01 12:00:00', periods=12, freq='D'),
            'duration_min': [12.0, 8.5, 10.2, 15.3, 6.8, 14.2, 9.7, 11.1, 13.5, 7.9, 16.2, 10.8],
            'avg_current': [8.5, 9.2, 15.1, 14.8, 6.9, 12.3, 10.7, 8.1, 13.9, 7.2, 16.5, 11.4],
            'max_temperature': [35.2, 32.1, 62.8, 58.3, 28.5, 45.7, 38.9, 30.6, 55.1, 27.8, 68.2, 42.3],
            'total_distance': [25.3, 18.7, 42.1, 38.9, 15.2, 32.6, 28.4, 20.1, 39.7, 16.8, 45.2, 30.9],
            'avg_battery': [85.2, 82.5, 65.8, 68.2, 91.3, 78.9, 83.1, 89.7, 71.4, 93.2, 62.5, 80.6],
            'tagged': [True, False, True, False, True, True, False, True, False, True, True, False]
        })
        
        processor.raw_df = sample_data
        processor.load_data.return_value = None
        processor._compute_sessions.return_value = (sample_data, sessions_data)
        
        return processor
    
    @pytest.mark.asyncio
    async def test_ml_service_health_scoring_integration(self, mock_data_processor):
        """Test full ML service integration with health scoring"""
        
        # Initialize ML service
        ml_service = MLService(mock_data_processor)
        success = await ml_service.initialize()
        
        assert success == True
        assert hasattr(ml_service, 'health_scoring_service')
        assert ml_service.health_scoring_service is not None
        
        # Train health scoring model
        training_result = await ml_service.train_health_scoring_model()
        
        assert training_result['status'] == 'success'
        assert 'model_metadata' in training_result
        assert 'message' in training_result
        
        # Calculate health scores
        health_scores = await ml_service.calculate_health_scores()
        
        assert 'health_scores' in health_scores
        assert 'total_devices' in health_scores
        assert health_scores['total_devices'] == 8  # Updated to match our 8 devices
        
        # Check health scoring status
        status = ml_service.get_health_scoring_status()
        
        assert status['model_loaded'] == True
        assert status['feature_count'] == 24
        assert 'performance_metrics' in status
    
    @pytest.mark.asyncio 
    async def test_health_scoring_error_handling(self, mock_data_processor):
        """Test error handling in health scoring"""
        
        ml_service = MLService(mock_data_processor)
        
        # Test before initialization
        with pytest.raises(RuntimeError):
            await ml_service.train_health_scoring_model()
        
        with pytest.raises(RuntimeError):
            await ml_service.calculate_health_scores()
        
        # Initialize service
        await ml_service.initialize()
        
        # Test with empty features
        with patch.object(ml_service, 'extract_features') as mock_extract:
            mock_extract.return_value = {'features': {}}
            
            with pytest.raises(ValueError):
                await ml_service.train_health_scoring_model()
    
    @pytest.mark.asyncio
    async def test_health_scoring_performance(self, mock_data_processor):
        """Test health scoring performance requirements"""
        
        ml_service = MLService(mock_data_processor)
        await ml_service.initialize()
        
        # Train model
        start_time = datetime.now()
        training_result = await ml_service.train_health_scoring_model()
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Verify training completes within reasonable time (30s requirement)
        assert training_time < 30.0, f"Training took {training_time}s, should be under 30s"
        
        # Calculate health scores
        start_time = datetime.now()
        health_scores = await ml_service.calculate_health_scores()
        calculation_time = (datetime.now() - start_time).total_seconds()
        
        # Verify calculation completes quickly
        assert calculation_time < 5.0, f"Health score calculation took {calculation_time}s, should be under 5s"
        
        # Verify all devices have scores
        assert len(health_scores['health_scores']) == 8  # Updated to match our 8 devices