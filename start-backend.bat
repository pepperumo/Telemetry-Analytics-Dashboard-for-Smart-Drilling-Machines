@echo off

echo Starting Telemetry Analytics Dashboard Backend...

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create ML directory structure
echo Creating ML directory structure...
if not exist "..\data\ml" mkdir "..\data\ml"
if not exist "..\data\ml\models" mkdir "..\data\ml\models"
if not exist "..\data\ml\metadata" mkdir "..\data\ml\metadata"
if not exist "..\data\ml\performance" mkdir "..\data\ml\performance"
if not exist "..\data\ml\backups" mkdir "..\data\ml\backups"
if not exist "..\data\ml\features" mkdir "..\data\ml\features"

REM Initialize ML system and verify health
echo Initializing ML system...
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

REM Start the server
echo Starting FastAPI server...
python main.py

pause