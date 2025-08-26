"""
MCP (Model Context Protocol) Module

Provides FastMCP-based server implementation for drilling analytics.
Supports both backward compatibility with existing interfaces and 
direct FastMCP integration for Claude Desktop.
"""

__version__ = "1.0.0"
__author__ = "Telemetry Analytics Dashboard Team"

from .server import (
    MCPServer,
    get_mcp_server,
    start_mcp_server,
    stop_mcp_server,
    get_fastmcp_server,
    get_server_status,
    set_mcp_services,
    run_mcp_server_stdio,
    mcp
)

# Backward compatibility exports
__all__ = [
    "MCPServer",
    "get_mcp_server", 
    "start_mcp_server",
    "stop_mcp_server",
    "get_fastmcp_server",
    "get_server_status",
    "set_mcp_services",
    "run_mcp_server_stdio",
    "mcp"
]