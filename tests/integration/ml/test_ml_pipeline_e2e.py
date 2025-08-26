"""
End-to-End ML Pipeline Integration Tests

Tests the complete ML pipeline from CSV data input to dashboard display.
"""
import pytest
import asyncio
import time
from typing import Dict, Any
import httpx


class TestMLPipelineE2E:
    """End-to-end tests for ML pipeline functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_ml_pipeline(self, backend_client: httpx.Client, ml_service):
        """Test complete pipeline: CSV -> Features -> Health Scores -> Dashboard."""
        
        # Step 1: Verify data loading
        response = backend_client.get("/api/v1/sessions")
        assert response.status_code == 200
        sessions_data = response.json()
        assert "sessions" in sessions_data, "No sessions field in response"
        
        # Step 2: Test ML health scores calculation
        response = backend_client.get("/api/ml/health-scores")
        assert response.status_code == 200
        health_scores = response.json()
        assert "health_scores" in health_scores
        assert len(health_scores["health_scores"]) > 0
        
        # Step 3: Verify health score structure
        first_score = health_scores["health_scores"][0]
        required_fields = ["device_id", "health_score", "risk_level", "confidence_interval"]
        for field in required_fields:
            assert field in first_score, f"Missing field: {field}"
        
        # Step 4: Test predictive alerts generation
        response = backend_client.get("/api/ml/alerts")
        assert response.status_code == 200
        alerts_data = response.json()
        assert "alerts" in alerts_data
        
        # Step 5: Verify ML model status
        response = backend_client.get("/api/ml/model-status")
        assert response.status_code == 200
        model_status = response.json()
        assert "model_version" in model_status
        
        print("✓ Complete ML pipeline test passed")
    
    @pytest.mark.asyncio
    async def test_ml_feature_engineering_pipeline(self, ml_service):
        """Test feature engineering pipeline produces valid features."""
        
        # Test feature extraction with sample session data
        sample_sessions = [
            {
                "device_id": "DRILL_TEST_001", 
                "session_id": "test_session_1",
                "timestamp": "2025-08-26T10:00:00Z",
                "current_consumption": 45.2,
                "battery_voltage": 24.1,
                "operating_state": "DRILLING"
            }
        ]
        
        # Call feature engineering through ML service
        features = await ml_service.extract_features(sample_sessions)
        
        # Verify features structure
        assert isinstance(features, dict)
        assert len(features) > 0, "No features extracted"
        
        # Check for expected feature categories
        expected_categories = ["consumption_stats", "battery_trends", "operational_patterns"]
        feature_found = any(category in features for category in expected_categories)
        assert feature_found, f"Expected one of {expected_categories} in features"
        
        print("✓ Feature engineering pipeline test passed")
    
    @pytest.mark.asyncio
    async def test_health_score_consistency(self, backend_client: httpx.Client):
        """Test health score calculations are consistent across calls."""
        
        # Make multiple requests for same device
        device_responses = []
        for _ in range(3):
            response = backend_client.get("/api/ml/health-scores")
            assert response.status_code == 200
            device_responses.append(response.json())
            time.sleep(0.1)  # Small delay between requests
        
        # Verify consistency (health scores shouldn't vary dramatically)
        if len(device_responses) >= 2:
            first_scores = {item["device_id"]: item["health_score"] 
                          for item in device_responses[0]["health_scores"]}
            second_scores = {item["device_id"]: item["health_score"] 
                           for item in device_responses[1]["health_scores"]}
            
            # Check that health scores are consistent (within 10% variation)
            for device_id in first_scores:
                if device_id in second_scores:
                    score_diff = abs(first_scores[device_id] - second_scores[device_id])
                    assert score_diff < 10.0, f"Health score too variable for {device_id}"
        
        print("✓ Health score consistency test passed")
    
    @pytest.mark.asyncio
    async def test_ml_system_graceful_degradation(self, backend_client: httpx.Client):
        """Test ML system handles errors gracefully."""
        
        # Test with invalid device ID
        response = backend_client.get("/api/ml/health-scores?device_id=INVALID_DEVICE")
        # Should return success with empty results or appropriate error handling
        assert response.status_code in [200, 404]
        
        # Test ML health endpoint
        response = backend_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "ml_enabled" in health_data
        
        print("✓ ML graceful degradation test passed")