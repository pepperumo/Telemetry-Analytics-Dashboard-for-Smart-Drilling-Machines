"""
ML Integration Test Configuration and Fixtures

Simple HTTP-based testing without backend imports.
Tests assume backend is running on localhost:8000.
"""
import pytest
import asyncio
from pathlib import Path
from typing import Generator
import httpx

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def backend_client() -> Generator[httpx.Client, None, None]:
    """HTTP client for backend API testing."""
    with httpx.Client(base_url="http://localhost:8000") as client:
        yield client

@pytest.fixture(scope="session")
def frontend_client() -> Generator[httpx.Client, None, None]:
    """HTTP client for frontend testing."""
    with httpx.Client(base_url="http://localhost:5174") as client:
        yield client

@pytest.fixture(scope="session")
def ml_service():
    """Mock ML service fixture for E2E tests."""
    class MockMLService:
        async def extract_features(self, data):
            """Mock feature extraction."""
            return {
                "consumption_stats": {"mean": 45.0, "std": 2.1},
                "battery_trends": {"declining": False, "voltage": 24.1},
                "operational_patterns": {"drilling_ratio": 0.8}
            }
        
        def get_health_scoring_status(self):
            """Mock health scoring status."""
            return {"is_trained": True, "model_metadata": {}}
    
    return MockMLService()

@pytest.fixture
def suppress_sklearn_warnings():
    """Suppress sklearn warnings in tests."""
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
    warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
    yield
    warnings.resetwarnings()

@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data for testing."""
    return {
        "device_id": "DRILL_001",
        "timestamp": "2025-08-26T10:00:00Z",
        "current_consumption": 45.2,
        "battery_voltage": 24.1,
        "operating_state": "DRILLING",
        "session_duration": 1800,
        "location": {"lat": 40.7128, "lng": -74.0060}
    }

@pytest.fixture
def ml_api_endpoints():
    """ML API endpoints for testing."""
    return {
        "health_scores": "/api/ml/health-scores",
        "alerts": "/api/ml/alerts",
        "model_status": "/api/ml/model-status",
        "health_check": "/api/ml/health",
        "statistics": "/api/ml/alerts/statistics"
    }

@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing."""
    return {
        "dashboard_load_time": 3.0,  # seconds
        "ml_component_load_time": 2.0,  # seconds
        "api_response_time": 1.0,  # seconds
        "health_score_calculation": 0.5  # seconds
    }

@pytest.fixture(scope="session")
def test_environment_check():
    """Verify test environment is properly set up."""
    checks = {
        "backend_running": False,
        "frontend_running": False,
        "test_data_available": False,
        "ml_directories_exist": False
    }
    
    # Check if backend is running
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        checks["backend_running"] = response.status_code == 200
    except:
        pass
    
    # Check if frontend is running
    try:
        response = httpx.get("http://localhost:5174", timeout=5.0)
        checks["frontend_running"] = response.status_code == 200
    except:
        pass
    
    # Check test data
    test_data_path = Path("public/data/raw_drilling_sessions.csv")
    checks["test_data_available"] = test_data_path.exists()
    
    # Check ML directories
    ml_dirs = ["data/ml/models", "data/ml/metadata", "data/ml/performance"]
    checks["ml_directories_exist"] = all(Path(d).exists() for d in ml_dirs)
    
    return checks