from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from app.api.dashboard import router as dashboard_router
from app.api.ml import router as ml_router
from app.services.data_processor import DataProcessor
from app.services.telemetry_service import TelemetryService
from app.ml.services import MLService
from app.mcp.server import set_mcp_services, get_server_status

# Load environment variables
load_dotenv()

# Configuration from environment variables
ML_ENABLED = os.getenv("ML_ENABLED", "true").lower() == "true"
ML_DEBUG = os.getenv("ML_DEBUG", "false").lower() == "true"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5174").split(",")
MCP_ENABLED = os.getenv("MCP_ENABLED", "true").lower() == "true"

# Initialize data processor
data_processor = DataProcessor()

# Initialize telemetry service 
telemetry_service = TelemetryService()

# Initialize ML service with real telemetry data (only if enabled)
ml_service = MLService() if ML_ENABLED else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        data_processor.load_data()
        print("Data loaded successfully")
        # Make data processor available to routes
        app.state.data_processor = data_processor
        
        # Initialize ML service with real telemetry data (only if enabled)
        if ML_ENABLED and ml_service:
            ml_initialized = await ml_service.initialize()
            app.state.ml_service = ml_service
            if ml_initialized:
                print("✓ ML Service initialized successfully with real telemetry data")
            else:
                print("⚠ ML Service initialization skipped or failed")
        else:
            print("ℹ ML Service disabled via configuration")
            app.state.ml_service = None
            
        # Initialize MCP server (only if enabled)
        if MCP_ENABLED:
            # Initialize MCP services for FastMCP
            set_mcp_services(telemetry_service, data_processor, ml_service)
            print("✓ MCP Server configured with FastMCP - use run_mcp_server.py for Claude Desktop")
        else:
            print("ℹ MCP Server disabled via configuration")
            
    except Exception as e:
        print(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    print("Application shutting down")
    if hasattr(app.state, 'ml_service') and app.state.ml_service:
        app.state.ml_service.shutdown()
    print("✓ Application shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title=os.getenv("APP_NAME", "Telemetry Analytics Dashboard API"),
    description="API for Smart Drilling Machine Telemetry Analytics with ML Enhancement",
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
    debug=DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])

# Include ML router only if ML is enabled
if ML_ENABLED:
    app.include_router(ml_router, prefix="/api/ml", tags=["machine-learning"])

@app.get("/")
async def root():
    return {
        "message": os.getenv("APP_NAME", "Telemetry Analytics Dashboard API"), 
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "ml_enabled": ML_ENABLED,
        "mcp_enabled": MCP_ENABLED
    }

@app.get("/health")
async def health():
    health_status = {"status": "healthy", "ml_enabled": ML_ENABLED, "mcp_enabled": MCP_ENABLED}
    
    # Add ML health check if enabled
    if ML_ENABLED and hasattr(app.state, 'ml_service') and app.state.ml_service:
        try:
            ml_health = await app.state.ml_service.get_system_health()
            health_status["ml_system"] = ml_health
        except Exception as e:
            health_status["ml_system"] = {"status": "error", "error": str(e)}
    
    # Add MCP health check if enabled
    if MCP_ENABLED:
        try:
            mcp_status = get_server_status()
            health_status["mcp_server"] = mcp_status
        except Exception as e:
            health_status["mcp_server"] = {"status": "error", "error": str(e)}
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=API_HOST, 
        port=API_PORT,
        reload=os.getenv("API_RELOAD", "false").lower() == "true"
    )