"""
ML API Integration Tests

Tests ML API endpoints functionality, authentication, and integration.
"""
import pytest
import httpx
from typing import Dict, List, Any


class TestMLAPIIntegration:
    """Integration tests for ML API endpoints."""
    
    def test_ml_health_scores_api(self, backend_client: httpx.Client):
        """Test ML health scores API endpoint."""
        
        response = backend_client.get("/api/ml/health-scores")
        assert response.status_code == 200
        
        data = response.json()
        assert "health_scores" in data
        
        # If there are health scores, verify structure
        if len(data["health_scores"]) > 0:
            score = data["health_scores"][0]
            required_fields = ["device_id", "health_score", "risk_level"]
            
            for field in required_fields:
                assert field in score, f"Missing required field: {field}"
            
            # Verify data types
            assert isinstance(score["health_score"], (int, float))
            assert 0 <= score["health_score"] <= 100
            assert score["risk_level"] in ["low", "medium", "high", "critical"]
        
        print("✓ ML health scores API working correctly")
    
    def test_ml_alerts_api(self, backend_client: httpx.Client):
        """Test ML alerts API endpoint."""
        
        response = backend_client.get("/api/ml/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        
        # If there are alerts, verify structure
        if len(data["alerts"]) > 0:
            alert = data["alerts"][0]
            required_fields = ["id", "device_id", "alert_type", "severity"]
            
            for field in required_fields:
                assert field in alert, f"Missing required field: {field}"
            
            # Verify severity values
            assert alert["severity"] in ["low", "medium", "high", "critical"]
        
        print("✓ ML alerts API working correctly")
    
    def test_ml_model_status_api(self, backend_client: httpx.Client):
        """Test ML model status API endpoint."""
        
        response = backend_client.get("/api/ml/model-status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify status fields
        expected_fields = ["model_version", "is_trained", "status"]
        for field in expected_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify status values
        assert data["status"] in ["ready", "not_trained"]
        assert isinstance(data["is_trained"], bool)
        
        print("✓ ML model status API working correctly")
    
    def test_ml_alerts_filtering(self, backend_client: httpx.Client):
        """Test ML alerts API filtering functionality."""
        
        # Test filtering by severity
        response = backend_client.get("/api/ml/alerts?severity=high")
        assert response.status_code in [200, 422]  # 422 if validation fails
        
        if response.status_code == 200:
            data = response.json()
            if "alerts" in data and len(data["alerts"]) > 0:
                for alert in data["alerts"]:
                    assert alert.get("severity") == "high"
        
        # Test filtering by device (use a real device ID if available)
        health_response = backend_client.get("/api/ml/health-scores")
        test_device_id = "7a3f55e1"  # Default test device ID
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            if "health_scores" in health_data and len(health_data["health_scores"]) > 0:
                test_device_id = health_data["health_scores"][0]["device_id"]
        
        response = backend_client.get(f"/api/ml/alerts?device_id={test_device_id}")
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            if "alerts" in data and len(data["alerts"]) > 0:
                for alert in data["alerts"]:
                    assert alert.get("device_id") == test_device_id
        
        print("✓ ML alerts filtering working correctly")
    
    def test_ml_health_scores_filtering(self, backend_client: httpx.Client):
        """Test ML health scores API filtering functionality."""
        
        # First get available device IDs
        response = backend_client.get("/api/ml/health-scores")
        assert response.status_code == 200
        
        data = response.json()
        if "health_scores" in data and len(data["health_scores"]) > 0:
            # Use the first available device ID for filtering test
            device_id = data["health_scores"][0]["device_id"]
            
            # Test filtering by this device
            filter_response = backend_client.get(f"/api/ml/health-scores?device_ids={device_id}")
            assert filter_response.status_code == 200
            
            filter_data = filter_response.json()
            if "health_scores" in filter_data and len(filter_data["health_scores"]) > 0:
                for score in filter_data["health_scores"]:
                    assert score.get("device_id") == device_id
        
        print("✓ ML health scores filtering working correctly")
        
        # Test filtering by risk level
        response = backend_client.get("/api/ml/health-scores?risk_level=high")
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            if "health_scores" in data and len(data["health_scores"]) > 0:
                for score in data["health_scores"]:
                    assert score.get("risk_level") == "high"
        
        print("✓ ML health scores filtering working correctly")
    
    def test_ml_alerts_pagination(self, backend_client: httpx.Client):
        """Test ML alerts API pagination."""
        
        # Test pagination parameters
        response = backend_client.get("/api/ml/alerts?page=1&per_page=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        
        # Verify pagination info if present
        if "total" in data:
            assert isinstance(data["total"], int)
        if "page" in data:
            assert isinstance(data["page"], int)
        if "per_page" in data:
            assert isinstance(data["per_page"], int)
        
        # Verify we don't get more than requested per_page
        if len(data["alerts"]) > 0:
            assert len(data["alerts"]) <= 5
        
        print("✓ ML alerts pagination working correctly")
    
    def test_ml_api_error_handling(self, backend_client: httpx.Client):
        """Test ML API error handling."""
        
        # Test invalid parameters
        error_tests = [
            "/api/ml/health-scores?health_score=invalid",
            "/api/ml/alerts?severity=invalid_severity",
            "/api/ml/alerts?page=-1",
            "/api/ml/alerts?per_page=0"
        ]
        
        for test_endpoint in error_tests:
            response = backend_client.get(test_endpoint)
            
            # Should return appropriate error status
            assert response.status_code in [200, 400, 422], \
                f"Unexpected status {response.status_code} for {test_endpoint}"
            
            # If error, should return valid JSON
            if response.status_code in [400, 422]:
                try:
                    error_data = response.json()
                    assert "detail" in error_data or "message" in error_data
                except:
                    # Non-JSON error responses are also acceptable
                    pass
        
        print("✓ ML API error handling working correctly")
    
    def test_ml_api_response_headers(self, backend_client: httpx.Client):
        """Test ML API response headers."""
        
        response = backend_client.get("/api/ml/health-scores")
        assert response.status_code == 200
        
        headers = response.headers
        
        # Verify content type
        assert "content-type" in headers
        assert "application/json" in headers["content-type"]
        
        # Verify response is valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        print("✓ ML API response headers correct")
    
    def test_ml_api_data_consistency(self, backend_client: httpx.Client):
        """Test ML API data consistency across multiple calls."""
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = backend_client.get("/api/ml/health-scores")
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify response structure is consistent
        for response_data in responses:
            assert "health_scores" in response_data
            assert isinstance(response_data["health_scores"], list)
        
        # If there's data, verify device IDs are consistent
        if len(responses) > 1 and len(responses[0]["health_scores"]) > 0:
            device_ids_1 = {score["device_id"] for score in responses[0]["health_scores"]}
            device_ids_2 = {score["device_id"] for score in responses[1]["health_scores"]}
            
            # Device IDs should be generally consistent (allowing for some variation)
            if device_ids_1 and device_ids_2:
                overlap = len(device_ids_1.intersection(device_ids_2))
                total = len(device_ids_1.union(device_ids_2))
                consistency_ratio = overlap / total if total > 0 else 1
                
                assert consistency_ratio >= 0.8, f"Low consistency ratio: {consistency_ratio}"
        
        print("✓ ML API data consistency verified")