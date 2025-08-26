from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.dashboard import router as dashboard_router
from app.services.data_processor import DataProcessor

# Initialize data processor
data_processor = DataProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        data_processor.load_data()
        print("Data loaded successfully")
        # Make data processor available to routes
        app.state.data_processor = data_processor
    except Exception as e:
        print(f"Error loading data: {e}")
    
    yield
    
    # Shutdown (if needed)
    print("Application shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Telemetry Analytics Dashboard API",
    description="API for Smart Drilling Machine Telemetry Analytics",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Telemetry Analytics Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)