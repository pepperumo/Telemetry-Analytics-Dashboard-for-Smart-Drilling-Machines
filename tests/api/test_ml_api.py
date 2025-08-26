"""
Tests for ML API endpoints
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import json

from main import app
from app.ml.services import MLService
from app.services.data_processor import DataProcessor


class TestMLAPI:
    """Test ML API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ml_service(self):
        """Create mock ML service"""
        ml_service = Mock(spec=MLService)
        
        # Mock health scores response (async)
        ml_service.calculate_health_scores = AsyncMock(return_value={
            'status': 'success',
            'health_scores': {
                'device_001': {
                    'health_score': 95.5,
                    'confidence_interval': (92.1, 98.9),
                    'explanatory_factors': [
                        {'feature': 'current_mean', 'value': 8.5, 'importance': 0.45, 'impact': 'Normal current levels'},
                        {'feature': 'temperature_max', 'value': 75.2, 'importance': 0.35, 'impact': 'Optimal temperature'},
                        {'feature': 'battery_level', 'value': 85.0, 'importance': 0.20, 'impact': 'Good battery health'}
                    ]
                },
                'device_002': {
                    'health_score': 78.3,
                    'confidence_interval': (74.1, 82.5),
                    'explanatory_factors': [
                        {'feature': 'current_mean', 'value': 12.3, 'importance': 0.50, 'impact': 'High current draw'},
                        {'feature': 'temperature_max', 'value': 82.5, 'importance': 0.30, 'impact': 'Elevated temperature'},
                        {'feature': 'vibration_std', 'value': 3.2, 'importance': 0.20, 'impact': 'Moderate vibration'}
                    ]
                }
            }
        })
        
        # Mock model status response (async)
        ml_service.get_health_scoring_status = AsyncMock(return_value={
            'is_trained': True,
            'model_metadata': {
                'model_version': '1.0.0',
                'training_date': datetime.now(),
                'r2_score': 0.85,
                'rmse': 5.2,
                'cross_val_score': 0.82,
                'feature_count': 25,
                'training_samples': 100,
                'feature_importance_top_10': [
                    {'feature': 'current_mean', 'importance': 0.25},
                    {'feature': 'temperature_max', 'importance': 0.20}
                ]
            }
        })
        
        # Mock training response (async)
        ml_service.train_health_scoring_model = AsyncMock(return_value={
            'status': 'success',
            'message': 'Model trained successfully'
        })
        
        return ml_service
    
    @pytest.fixture(autouse=True)
    def setup_app_state(self, mock_ml_service):
        """Setup app state with mock services"""
        app.state.ml_service = mock_ml_service
        app.state.data_processor = Mock(spec=DataProcessor)
        yield
        # Cleanup
        if hasattr(app.state, 'ml_service'):
            delattr(app.state, 'ml_service')
        if hasattr(app.state, 'data_processor'):
            delattr(app.state, 'data_processor')
    
    def test_health_scores_endpoint_basic(self, client, mock_ml_service):
        """Test basic health scores endpoint"""
        response = client.get("/api/ml/health-scores")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'health_scores' in data
        assert 'total_devices' in data
        assert 'average_health_score' in data
        assert 'at_risk_devices' in data
        
        assert data['total_devices'] == 2
        assert len(data['health_scores']) == 2
        
        # Check first device
        device_score = data['health_scores'][0]
        assert 'device_id' in device_score
        assert 'health_score' in device_score
        assert 'confidence_interval' in device_score
        assert 'risk_level' in device_score
        assert 'explanatory_factors' in device_score
        
        mock_ml_service.calculate_health_scores.assert_called_once()
    
    def test_health_scores_with_filters(self, client, mock_ml_service):
        """Test health scores endpoint with filters"""
        response = client.get(
            "/api/ml/health-scores?device_ids=device_001&min_health_score=90&page=1&page_size=10"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return device_001 (health score 95.5 > 90)
        assert data['total_devices'] == 1
        assert data['health_scores'][0]['device_id'] == 'device_001'
        assert data['health_scores'][0]['health_score'] >= 90
        
        assert 'filters_applied' in data
        filters = data['filters_applied']
        assert 'device_ids' in filters
        assert 'min_health_score' in filters
    
    def test_health_scores_risk_level_filter(self, client, mock_ml_service):
        """Test health scores filtering by risk level"""
        response = client.get("/api/ml/health-scores?risk_levels=medium")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return device_002 (health score 78.3 = medium risk)
        assert data['total_devices'] == 1
        assert data['health_scores'][0]['device_id'] == 'device_002'
        assert data['health_scores'][0]['risk_level'] == 'medium'
    
    def test_health_scores_pagination(self, client, mock_ml_service):
        """Test health scores pagination"""
        response = client.get("/api/ml/health-scores?page=1&page_size=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['total_devices'] == 2  # Total devices
        assert len(data['health_scores']) == 1  # But only 1 returned due to pagination
    
    def test_model_status_endpoint(self, client, mock_ml_service):
        """Test model status endpoint"""
        response = client.get("/api/ml/model-status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'model_version' in data
        assert 'training_date' in data
        assert 'is_trained' in data
        assert 'performance_metrics' in data
        assert 'feature_importance_top_10' in data
        assert 'status' in data
        
        assert data['is_trained'] == True
        assert data['status'] == 'ready'
        
        # Check performance metrics
        metrics = data['performance_metrics']
        assert 'r2_score' in metrics
        assert 'rmse' in metrics
        assert 'cross_val_score' in metrics
        assert 'feature_count' in metrics
        assert 'training_samples' in metrics
        
        mock_ml_service.get_health_scoring_status.assert_called_once()
    
    def test_model_status_untrained(self, client, mock_ml_service):
        """Test model status when model is not trained"""
        # Override mock to return untrained status
        async def mock_get_untrained_status():
            return {
                'is_trained': False,
                'model_metadata': None
            }
        
        mock_ml_service.get_health_scoring_status = mock_get_untrained_status
        
        response = client.get("/api/ml/model-status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['is_trained'] == False
        assert data['status'] == 'not_trained'
        assert data['performance_metrics'] is None
    
    def test_train_model_endpoint(self, client, mock_ml_service):
        """Test model training endpoint"""
        response = client.post("/api/ml/train", json={"force_retrain": False})
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'status' in data
        assert 'message' in data
        assert 'model_metadata' in data
        assert 'training_time_seconds' in data
        
        assert data['status'] == 'success'
        assert isinstance(data['training_time_seconds'], float)
        
        mock_ml_service.train_health_scoring_model.assert_called_once()
    
    def test_train_model_with_force_retrain(self, client, mock_ml_service):
        """Test model training with force retrain"""
        response = client.post("/api/ml/train", json={"force_retrain": True})
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
    
    def test_health_check_endpoint(self, client, mock_ml_service):
        """Test ML health check endpoint"""
        response = client.get("/api/ml/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'status' in data
        assert 'timestamp' in data
        assert 'ml_service' in data
        assert 'health_scoring' in data
        assert 'feature_engineering' in data
        
        assert data['status'] == 'healthy'
        assert data['ml_service'] == 'available'
    
    def test_ml_service_unavailable(self, client):
        """Test API behavior when ML service is unavailable"""
        # Remove ML service from app state
        if hasattr(app.state, 'ml_service'):
            delattr(app.state, 'ml_service')
        
        response = client.get("/api/ml/health-scores")
        
        assert response.status_code == 503
        assert 'ML service not available' in response.json()['detail']
    
    def test_ml_service_error_handling(self, client, mock_ml_service):
        """Test error handling when ML service fails"""
        # Make ML service raise an exception
        async def mock_error():
            raise Exception("ML service error")
        
        mock_ml_service.calculate_health_scores = mock_error
        
        response = client.get("/api/ml/health-scores")
        
        assert response.status_code == 500
        assert 'Internal server error' in response.json()['detail']
    
    def test_invalid_query_parameters(self, client, mock_ml_service):
        """Test API validation with invalid parameters"""
        # Test invalid health score range
        response = client.get("/api/ml/health-scores?min_health_score=150")
        assert response.status_code == 422  # Validation error
        
        # Test invalid page number
        response = client.get("/api/ml/health-scores?page=0")
        assert response.status_code == 422
        
        # Test invalid page size
        response = client.get("/api/ml/health-scores?page_size=150")
        assert response.status_code == 422
    
    def test_risk_level_mapping(self, client, mock_ml_service):
        """Test risk level mapping logic"""
        # Test different health scores and their risk levels
        test_scores = [
            (95.0, 'low'),     # >= 80
            (75.0, 'medium'),  # 60-79
            (45.0, 'high'),    # 40-59
            (25.0, 'critical') # < 40
        ]
        
        for score, expected_risk in test_scores:
            async def mock_scores_for_test():
                return {
                    'status': 'success',
                    'health_scores': {
                        'test_device': {
                            'health_score': score,
                            'confidence_interval': (score-5, score+5),
                            'explanatory_factors': []
                        }
                    }
                }
            
            mock_ml_service.calculate_health_scores = mock_scores_for_test
            
            response = client.get("/api/ml/health-scores")
            assert response.status_code == 200
            
            data = response.json()
            assert data['health_scores'][0]['risk_level'] == expected_risk