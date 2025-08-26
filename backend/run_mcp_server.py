#!/usr/bin/env python3
"""
Standalone FastMCP Server for Claude Desktop Integration

This script runs the MCP server independently for Claude Desktop to connect to.
It provides all 8 MCP tools with real data access.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_services():
    """Initialize the services with real data."""
    try:
        # Import services
        from app.services.data_processor import DataProcessor
        from app.services.telemetry_service import TelemetryService
        from app.mcp.server import set_mcp_services
        
        # Check if ML is enabled
        ML_ENABLED = os.getenv("ML_ENABLED", "true").lower() == "true"
        
        logger.info("Initializing services with real data...")
        
        # Initialize data processor with real data
        data_processor = DataProcessor()
        data_processor.load_data()
        logger.info("✓ Data processor initialized with real data")
        
        # Initialize telemetry service
        telemetry_service = TelemetryService()
        logger.info("✓ Telemetry service initialized")
        
        # Initialize ML service if enabled
        ml_service = None
        if ML_ENABLED:
            try:
                from app.ml.services import MLService
                ml_service = MLService()
                ml_initialized = await ml_service.initialize()
                if ml_initialized:
                    logger.info("✓ ML service initialized with real data")
                else:
                    logger.warning("⚠ ML service initialization skipped")
            except Exception as e:
                logger.warning(f"⚠ ML service not available: {e}")
        
        # Initialize MCP services with real data
        set_mcp_services(telemetry_service, data_processor, ml_service)
        logger.info("✓ MCP services initialized with real data")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return False

async def main():
    """Run the standalone FastMCP server with real data."""
    try:
        logger.info("Starting standalone FastMCP server for Claude Desktop")
        
        # Initialize services with real data first
        if not await initialize_services():
            logger.error("Failed to initialize services - exiting")
            sys.exit(1)
        
        # Import the FastMCP server and run it directly (not async)
        from app.mcp.server import mcp
        
        logger.info("Starting FastMCP server with stdio transport")
        # Note: mcp.run() creates its own event loop, so we need to run it from non-async context
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start FastMCP server: {e}")
        sys.exit(1)

def run_server():
    """Non-async wrapper to initialize and run the server."""
    # Run initialization first
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        if not loop.run_until_complete(initialize_services()):
            logger.error("Failed to initialize services - exiting")
            sys.exit(1)
        
        # Now run the MCP server (which creates its own loop)
        from app.mcp.server import mcp
        logger.info("Starting FastMCP server with stdio transport")
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Failed to start FastMCP server: {e}")
        sys.exit(1)
    finally:
        loop.close()

if __name__ == "__main__":
    run_server()