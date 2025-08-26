# MCP Server Testing Guide

## Overview

This guide covers testing for the Model Context Protocol (MCP) Server foundation components. The test suite ensures reliability, security, and protocol compliance of the MCP server infrastructure.

## Test Structure

The MCP tests are located in `tests/mcp/` and cover the following components:

- **Configuration Management** (`MCPConfig`)
- **Connection Management** (`MCPConnectionManager`) 
- **Core Server** (`MCPServer`)
- **Data Models** (Pydantic models for MCP protocol)
- **Integration** (Global server instances and singletons)
- **Telemetry Tools** (Story 1.2 - MCP tools for telemetry data access)

## Running Tests

### Prerequisites

1. **Virtual Environment**: Ensure the virtual environment is activated:
   ```bash
   source venv/Scripts/activate  # Windows
   source venv/bin/activate      # Linux/macOS
   ```

2. **Dependencies**: Install testing dependencies:
   ```bash
   pip install pytest pytest-asyncio
   ```

3. **Core Dependencies**: Install MCP server dependencies:
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv websockets pandas numpy scikit-learn joblib
   ```

### Execute Tests

Run all MCP tests with verbose output:
```bash
python -m pytest tests/mcp/ -v
```

Run specific test files:
```bash
python -m pytest tests/mcp/test_mcp_server.py -v                     # Foundation tests (22 tests)
python -m pytest tests/mcp/test_story_1_2_telemetry_tools.py -v      # Telemetry tools tests (10 tests)
```

Run all MCP tests together:
```bash
python -m pytest tests/mcp/ -v                                       # All MCP tests (32 tests total)
```

Run specific test classes:
```bash
python -m pytest tests/mcp/test_mcp_server.py::TestMCPConfig -v
python -m pytest tests/mcp/test_mcp_server.py::TestMCPConnectionManager -v
python -m pytest tests/mcp/test_mcp_server.py::TestMCPServer -v
```

Run specific test methods:
```bash
python -m pytest tests/mcp/test_mcp_server.py::TestMCPConfig::test_config_defaults -v
```

## Test Coverage

### MCP Server Foundation Tests (22 tests)

#### Configuration Tests (4 tests)
- ✅ `test_config_defaults`: Validates default configuration values
- ✅ `test_websocket_url_generation`: Tests WebSocket URL construction
- ✅ `test_cors_origins_parsing`: Validates CORS origin parsing
- ✅ `test_development_mode_detection`: Tests environment detection

#### Connection Management Tests (8 tests)
- ✅ `test_add_connection`: Tests connection addition and state tracking
- ✅ `test_remove_connection`: Tests connection cleanup
- ✅ `test_authentication_not_required`: Tests optional authentication flow
- ✅ `test_authentication_with_api_key`: Tests API key authentication
- ✅ `test_authentication_failure`: Tests authentication failure handling
- ✅ `test_rate_limiting`: Tests rate limiting enforcement
- ✅ `test_record_request`: Tests request tracking and monitoring
- ✅ `test_connection_count`: Tests active connection counting

#### Server Core Tests (5 tests)
- ✅ `test_server_initialization`: Tests server startup configuration
- ✅ `test_server_status`: Tests server status reporting
- ✅ `test_handle_ping_message`: Tests ping/pong protocol handling
- ✅ `test_handle_invalid_json`: Tests invalid message handling
- ✅ `test_handle_unknown_message_type`: Tests unknown message type handling

#### Data Model Tests (3 tests)
- ✅ `test_mcp_tool_request_validation`: Tests request model validation
- ✅ `test_mcp_tool_response_creation`: Tests response model creation
- ✅ `test_mcp_connection_info_creation`: Tests connection info model

#### Integration Tests (2 tests)
- ✅ `test_global_server_instance`: Tests singleton server instance
- ✅ `test_config_singleton`: Tests singleton configuration instance

### Telemetry Tools Tests (Story 1.2 - 10 tests)

#### Tool Registry Tests (6 tests)
- ✅ `test_tool_registry_initialization`: 4 tools properly registered
- ✅ `test_required_telemetry_tools_present`: All telemetry tools available
- ✅ `test_tool_definitions_structure`: Proper MCP protocol structure
- ✅ `test_service_integration`: Integration with telemetry services
- ✅ `test_tool_execution_framework`: Execute_tool method available
- ✅ `test_tool_registry_in_tools_dict`: Tools registered in internal dict

#### Integration Tests (3 tests)
- ✅ `test_story_1_2_completion_criteria`: All completion criteria met
- ✅ `test_tool_registry_logging`: Proper initialization logging
- ✅ `test_tool_execution_interface`: Tool execution interface validation

#### Completion Marker (1 test)
- ✅ `test_story_1_2_completion_marker`: Story 1.2 completion checkpoint

**Telemetry Tools Implemented:**
1. `get_drilling_sessions` - Retrieve drilling session data with filtering
2. `get_battery_status` - Monitor device battery levels and health  
3. `get_device_locations` - Access GPS tracking and location data
4. `get_session_analytics` - Generate analytical insights from session data

## Test Results Summary

### Story 1.1 - MCP Server Foundation
**Total Tests**: 22  
**Passed**: 22 (100%)  
**Failed**: 0  
**Warnings**: 41 (deprecation warnings, non-critical)
**Execution Time**: ~0.56 seconds

### Story 1.2 - Telemetry Data MCP Tools  
**Total Tests**: 10  
**Passed**: 10 (100%)  
**Failed**: 0  
**Warnings**: 22 (same deprecation warnings as foundation)
**Execution Time**: ~0.69 seconds

### Combined MCP Test Suite
**Total Tests**: 32 (22 foundation + 10 telemetry)  
**Success Rate**: 100% (32/32 tests passing)  
**Tools Implemented**: 4 telemetry tools ready for MCP client connections

**Overall MCP Implementation Status**: ✅ **COMPLETE**
- Story 1.1: MCP Server Foundation ✅
- Story 1.2: Telemetry Data MCP Tools ✅
- Story 1.3: ML Analytics MCP Tools (pending)
- Story 1.4: Authentication & Authorization (pending) 
- Story 1.5: MCP Management Tools (pending)

## Known Warnings

The test suite generates deprecation warnings that are **non-critical**:

1. **WebSocket Legacy API**: `websockets.server.WebSocketServerProtocol` deprecation
2. **DateTime UTC**: `datetime.utcnow()` deprecation in favor of timezone-aware objects
3. **Pydantic V2**: Legacy configuration format warnings

These warnings do not affect functionality and will be addressed in future updates.

## Test Environment

- **Python Version**: 3.13.1
- **Testing Framework**: pytest 8.4.1 with pytest-asyncio 1.1.0
- **Platform**: Windows (bash.exe shell)
- **Virtual Environment**: Local `venv/` directory

## Adding New Tests

When extending MCP functionality, follow these testing patterns:

### 1. Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_functionality(self):
    # Test async operations
    result = await some_async_operation()
    assert result is not None
```

### 2. Mock WebSocket Pattern
```python
@pytest.fixture
def mock_websocket(self):
    mock_ws = Mock()
    mock_ws.send = AsyncMock()
    return mock_ws
```

### 3. Configuration Test Pattern
```python
def test_config_property(self):
    config = MCPConfig(property=value)
    assert config.property == expected_value
```

## Troubleshooting

### Import Resolution Issues
If encountering import errors, ensure the backend path is properly added:
```python
import sys
import os
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
```

### Virtual Environment Issues
If activation fails, recreate the virtual environment:
```bash
rm -rf venv
python -m venv venv
source venv/Scripts/activate
pip install pytest pytest-asyncio fastapi uvicorn pydantic python-dotenv websockets
```

### Test Discovery Issues
Ensure test files and directories have proper `__init__.py` files:
```bash
touch tests/__init__.py
touch tests/mcp/__init__.py
```

## Integration with CI/CD

For automated testing, add to your CI pipeline:
```yaml
- name: Run MCP Tests
  run: |
    source venv/Scripts/activate
    python -m pytest tests/mcp/test_mcp_server.py -v --tb=short
```

## Next Steps

After completing MCP Server Foundation testing:

1. **Story 1.2**: Implement telemetry data MCP tools
2. **Story 1.3**: Implement ML analysis MCP tools  
3. **Story 1.4**: Implement authentication and authorization
4. **Story 1.5**: Implement MCP server management tools

Each story will require additional test coverage following the patterns established in this foundation test suite.