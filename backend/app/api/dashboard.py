from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from datetime import datetime
import pandas as pd

from app.models.schemas import DashboardInsights, AnomalyReport
from app.services.data_processor import DataProcessor

router = APIRouter()

@router.get("/insights", response_model=DashboardInsights)
async def get_insights(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get dashboard insights"""
    try:
        data_processor = request.app.state.data_processor
        insights = data_processor.calculate_insights(start_date, end_date)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies", response_model=AnomalyReport)
async def get_anomalies(request: Request):
    """Get anomaly detection results"""
    try:
        data_processor = request.app.state.data_processor
        anomalies = data_processor.detect_anomalies()
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/timeline")
async def get_session_timeline(
    request: Request,
    device_id: Optional[str] = Query(None)
):
    """Get session timeline data"""
    try:
        data_processor = request.app.state.data_processor
        timeline = data_processor.get_session_timeline(device_id)
        return {"timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/battery/trends")
async def get_battery_trends(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get battery level trends"""
    try:
        data_processor = request.app.state.data_processor
        trends = data_processor.get_battery_trends(start_date, end_date)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_devices(request: Request):
    """Get list of available devices"""
    try:
        data_processor = request.app.state.data_processor
        if data_processor.sessions_df is not None:
            devices = data_processor.sessions_df['device_id'].unique().tolist()
            return {"devices": devices}
        return {"devices": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_sessions(
    request: Request,
    device_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get list of available sessions with metadata"""
    try:
        data_processor = request.app.state.data_processor
        if data_processor.raw_df is None:
            return {"sessions": []}
        
        # Compute sessions on-the-fly
        telemetry_df, sessions_df = data_processor._compute_sessions()
        
        # Filter by date range if provided
        if start_date and end_date:
            start_dt = pd.to_datetime(start_date, utc=True)
            end_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            
            sessions_df = sessions_df[
                (sessions_df['start'] >= start_dt) & 
                (sessions_df['start'] <= end_dt)
            ]
        
        # Filter by device if specified
        if device_id:
            sessions_df = sessions_df[sessions_df['device_id'] == device_id]
        
        sessions = []
        for _, session in sessions_df.iterrows():
            sessions.append({
                "session_id": session['session_id'],
                "device_id": session['device_id'],
                "start": session['start'].isoformat(),
                "end": session['end'].isoformat(),
                "duration_min": round(session['duration_min'], 1),
                "tagged": session['tagged']
            })
        
        return {"sessions": sorted(sessions, key=lambda x: x['start'], reverse=True)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    data_processor = request.app.state.data_processor
    return {
        "status": "healthy",
        "data_loaded": data_processor.raw_df is not None,
        "timestamp": datetime.now().isoformat()
    }