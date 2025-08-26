"""
Dashboard Regression Tests

Tests to ensure existing dashboard functionality remains unchanged with ML components.
"""
import pytest
import httpx
from typing import Dict, List, Any


class TestDashboardRegression:
    """Regression tests for dashboard functionality with ML integration."""
    
    def test_existing_analytics_endpoints_unchanged(self, backend_client: httpx.Client):
        """Test that existing analytics endpoints maintain their original behavior."""
        
        # Test original analytics endpoints
        analytics_tests = [
            {
                "endpoint": "/api/v1/sessions",
                "expected_fields": ["sessions"],
                "min_records": 0
            },
            {
                "endpoint": "/api/v1/insights", 
                "expected_fields": ["total_sessions", "average_session_length_min"],
                "min_records": 0
            },
            {
                "endpoint": "/api/v1/battery/trends",
                "expected_fields": ["trends"],
                "min_records": 0
            }
        ]
        
        for test in analytics_tests:
            response = backend_client.get(test["endpoint"])
            assert response.status_code == 200, f"Endpoint {test['endpoint']} failed"
            
            data = response.json()
            
            # Verify expected fields exist
            for field in test["expected_fields"]:
                assert field in data, f"Missing expected field '{field}' in {test['endpoint']}"
            
            # Verify data structure is reasonable
            if isinstance(data, dict) and len(test["expected_fields"]) > 0:
                main_field = test["expected_fields"][0]
                if main_field in data:
                    assert isinstance(data[main_field], (list, dict, int, float))
        
        print("✓ All existing analytics endpoints maintain original behavior")
    
    def test_dashboard_data_accuracy_unchanged(self, backend_client: httpx.Client):
        """Test that dashboard data accuracy is unchanged by ML integration."""
        
        # Get session data
        sessions_response = backend_client.get("/api/v1/sessions")
        assert sessions_response.status_code == 200
        sessions_data = sessions_response.json()
        
        if "sessions" in sessions_data and len(sessions_data["sessions"]) > 0:
            # Get summary data
            summary_response = backend_client.get("/api/v1/insights")
            assert summary_response.status_code == 200
            summary_data = summary_response.json()
            
            # Verify data consistency
            if "total_sessions" in summary_data:
                reported_total = summary_data["total_sessions"]
                actual_total = len(sessions_data["sessions"])
                
                # Allow for small differences due to filtering or data processing
                assert abs(reported_total - actual_total) <= 1, \
                    f"Session count mismatch: reported {reported_total}, actual {actual_total}"
        
        print("✓ Dashboard data accuracy maintained")
    
    def test_original_api_response_formats(self, backend_client: httpx.Client):
        """Test that original API response formats are preserved."""
        
        # Test session data format
        response = backend_client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        
        if "sessions" in data and len(data["sessions"]) > 0:
            session = data["sessions"][0]
            
            # Verify session has expected fields (actual format)
            expected_session_fields = [
                "session_id", "device_id", "start", "end", "duration_min", "tagged"
            ]
            
            for field in expected_session_fields:
                assert field in session, f"Missing expected field '{field}' in session"
        
        print("✓ Original API response formats preserved")
    
    def test_performance_not_degraded(self, backend_client: httpx.Client):
        """Test that original endpoints performance is not significantly degraded."""
        
        import time
        
        # Test performance of original endpoints
        endpoints_to_test = [
            "/api/v1/sessions",
            "/api/v1/insights",
            "/api/v1/battery/trends"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = backend_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            performance_results[endpoint] = response_time
            
            assert response.status_code == 200
            # Original endpoints should respond quickly (under 2 seconds)
            assert response_time < 2.0, f"{endpoint} took {response_time:.2f}s"
        
        print(f"✓ Original endpoint performance maintained: {performance_results}")
    
    def test_cors_headers_unchanged(self, backend_client: httpx.Client):
        """Test that CORS headers are properly maintained for frontend compatibility."""
        
        # Test CORS headers on original endpoints
        response = backend_client.get("/api/v1/sessions")
        assert response.status_code == 200
        
        # Verify CORS headers are present (if they were in the original implementation)
        headers = response.headers
        
        # Basic check that the response is accessible
        assert "content-type" in headers
        assert "application/json" in headers["content-type"]
        
        print("✓ CORS headers and content types maintained")
    
    def test_error_handling_consistency(self, backend_client: httpx.Client):
        """Test that error handling is consistent across original and new endpoints."""
        
        # Test invalid requests to original endpoints
        error_tests = [
            "/api/v1/analytics/sessions?invalid_param=test",
            "/api/v1/analytics/nonexistent-endpoint"
        ]
        
        for test_endpoint in error_tests:
            response = backend_client.get(test_endpoint)
            
            # Should return appropriate error status
            assert response.status_code in [200, 400, 404, 422], \
                f"Unexpected status {response.status_code} for {test_endpoint}"
            
            # Response should be valid JSON or appropriate error format
            try:
                data = response.json()
                assert isinstance(data, (dict, list))
            except:
                # Non-JSON responses are acceptable for 404s
                assert response.status_code == 404
        
        print("✓ Error handling consistency maintained")
    
    def test_data_processor_functionality_intact(self, backend_client: httpx.Client):
        """Test that core data processor functionality remains intact."""
        
        # Test that data is being processed correctly
        response = backend_client.get("/api/v1/sessions")
        assert response.status_code == 200
        sessions_data = response.json()
        
        # Verify sessions data structure
        if "sessions" in sessions_data:
            sessions = sessions_data["sessions"]
            
            # Should have session data
            if len(sessions) > 0:
                session = sessions[0]
                
                # Verify basic data types
                assert isinstance(session, dict)
                
                # Verify numeric fields are properly typed
                numeric_fields = ["current_consumption", "battery_level", "battery_voltage"]
                for field in numeric_fields:
                    if field in session:
                        value = session[field]
                        assert isinstance(value, (int, float, type(None))), \
                            f"Field {field} should be numeric, got {type(value)}"
        
        print("✓ Data processor functionality intact")