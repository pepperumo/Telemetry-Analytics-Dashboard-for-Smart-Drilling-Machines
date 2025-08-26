from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class OperatingState(str, Enum):
    OFF = "OFF"
    STANDBY = "STANDBY" 
    SPIN = "SPIN"
    DRILL = "DRILL"

class TelemetryData(BaseModel):
    timestamp: datetime
    device_id: str
    seq: int
    current_amp: float
    gps_lat: Optional[float]
    gps_lon: Optional[float]
    battery_level: int
    ble_id: Optional[str]
    op_state: Optional[OperatingState]
    session_id: Optional[str]
    session_tagged: Optional[bool]
    session_ble_id: Optional[str]

class SessionSummary(BaseModel):
    session_id: str
    device_id: str
    start: datetime
    end: datetime
    duration_s: float
    rows: int
    tagged: bool
    ble_id: Optional[str]
    duration_min: float

class DashboardInsights(BaseModel):
    total_drilling_time_hours: float
    total_sessions: int
    average_session_length_min: float
    tagged_sessions_percentage: float
    operating_states_distribution: dict
    low_battery_alerts: List[dict]
    session_locations: List[dict]
    anomalies: dict
    total_operational_time_hours: float = 0
    total_timespan_hours: float = 0

class AnomalyReport(BaseModel):
    short_sessions: List[dict]
    missing_telemetry: List[dict]
    missing_gps: List[dict]
    low_battery: List[dict]