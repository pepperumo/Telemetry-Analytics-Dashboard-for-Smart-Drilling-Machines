# ML Integration Tests

This directory contains comprehensive integration tests for the ML system components.

## Test Structure

- `test_ml_pipeline_e2e.py` - End-to-end ML pipeline tests
- `test_ml_api_integration.py` - ML API integration tests
- `test_dashboard_regression.py` - Dashboard regression tests
- `test_performance_benchmarks.py` - Performance and load time tests
- `test_feature_flags.py` - ML feature flag and graceful degradation tests
- `conftest.py` - Test configuration and fixtures

## Running Tests

```bash
# Run all ML integration tests
pytest tests/integration/ml/ -v

# Run specific test categories
pytest tests/integration/ml/test_ml_pipeline_e2e.py -v
pytest tests/integration/ml/test_performance_benchmarks.py -v

# Run with coverage
pytest tests/integration/ml/ --cov=app/ml --cov-report=html
```

## Test Requirements

- Backend server running on localhost:8000
- Frontend server running on localhost:5174
- Test data available in public/data/
- ML system initialized and healthy