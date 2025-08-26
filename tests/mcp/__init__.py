"""
Tests __init__.py for MCP module tests.

Ensures proper path resolution and imports for MCP testing.
"""
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)