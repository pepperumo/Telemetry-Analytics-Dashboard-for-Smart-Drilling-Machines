#!/bin/bash

echo "Starting Telemetry Analytics Dashboard Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create ML directory structure
echo "Creating ML directory structure..."
mkdir -p "../data/ml"
mkdir -p "../data/ml/models"
mkdir -p "../data/ml/metadata"
mkdir -p "../data/ml/performance"
mkdir -p "../data/ml/backups"
mkdir -p "../data/ml/features"

# Initialize ML system and verify health
echo "Initializing ML system..."
python -c "
import asyncio
import sys
import os
sys.path.append('.')
from app.ml.services import MLService

async def verify_ml_health():
    try:
        ml_service = MLService()
        await ml_service._initialize_components()
        print('✓ ML system initialized successfully')
        return True
    except Exception as e:
        print(f'⚠ ML system initialization warning: {e}')
        print('  Application will start but ML features may be limited')
        return False

result = asyncio.run(verify_ml_health())
"

# Start the server
echo "Starting FastAPI server..."
python main.py