"""
Test configuration and fixtures
"""
import warnings
import pytest

# Suppress sklearn warnings that are expected in test environments
@pytest.fixture(autouse=True)
def suppress_sklearn_warnings():
    """Suppress sklearn warnings that are expected with small test datasets"""
    warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
    warnings.filterwarnings('ignore', message=r'.*R\^2 score is not well-defined.*')