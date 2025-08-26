import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os

from app.models.schemas import (
    TelemetryData, SessionSummary, DashboardInsights, 
    AnomalyReport, OperatingState
)

class DataProcessor:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to the public/data directory relative to the backend folder
            current_dir = Path(__file__).parent.parent.parent.parent  # Go up to project root
            self.data_dir = current_dir / "public" / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.raw_df = None
        self.session_gap_seconds = 30  # 30-second telemetry interval
        
    def load_data(self):
        """Load raw CSV file and process it"""
        try:
            # Load raw telemetry data
            raw_path = self.data_dir / "raw_drilling_sessions.csv"
            if raw_path.exists():
                self.raw_df = pd.read_csv(raw_path)
                self.raw_df['timestamp'] = pd.to_datetime(self.raw_df['timestamp'])
                print(f"Loaded {len(self.raw_df)} raw telemetry records")
            else:
                raise FileNotFoundError(f"Raw data file not found: {raw_path}")
                
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def derive_operating_state(self, current_amp: float) -> OperatingState:
        """Derive operating state from current draw"""
        if current_amp <= 0.5:
            return OperatingState.OFF
        elif current_amp <= 2.0:
            return OperatingState.STANDBY
        elif current_amp <= 4.5:
            return OperatingState.SPIN
        else:
            return OperatingState.DRILL
    
    def _assign_sessions(self, device_data: pd.DataFrame) -> pd.DataFrame:
        """Assign session IDs based on time gaps"""
        device_data = device_data.sort_values('timestamp').copy()
        device_data['time_diff'] = device_data['timestamp'].diff().dt.total_seconds().fillna(0)
        
        # Create session breaks where time gap > session_gap_seconds
        session_breaks = device_data['time_diff'] > self.session_gap_seconds
        device_data['session_local_id'] = session_breaks.cumsum()
        device_data['session_id'] = device_data['device_id'].astype(str) + '_' + device_data['session_local_id'].astype(str)
        
        return device_data
    
    def _compute_sessions(self) -> pd.DataFrame:
        """Compute session summaries from raw data"""
        if self.raw_df is None:
            return pd.DataFrame()
        
        # Assign sessions to each device
        enriched_data = []
        for device_id in self.raw_df['device_id'].unique():
            device_data = self.raw_df[self.raw_df['device_id'] == device_id].copy()
            device_sessions = self._assign_sessions(device_data)
            enriched_data.append(device_sessions)
        
        df = pd.concat(enriched_data, ignore_index=True)
        
        # Add derived fields
        df['op_state'] = df['current_amp'].apply(lambda x: self.derive_operating_state(x).value)
        
        # Determine if sessions are tagged
        def clean_ble_tags(series):
            valid = series.dropna()
            valid = valid[valid.astype(str).str.strip() != '']
            valid = valid[valid.astype(str) != 'nan']
            return valid.unique() if len(valid) > 0 else []

        session_ble = df.groupby('session_id')['ble_id'].apply(clean_ble_tags)
        session_tagged = session_ble.apply(lambda arr: len(arr) > 0)
        session_ble_id = session_ble.apply(lambda arr: arr[0] if len(arr) > 0 else None)

        df = df.merge(session_tagged.rename('session_tagged'), left_on='session_id', right_index=True, how='left')
        df = df.merge(session_ble_id.rename('session_ble_id'), left_on='session_id', right_index=True, how='left')
        
        # Compute session summaries
        session_summary = (
            df.groupby('session_id').agg({
                'device_id': 'first',
                'timestamp': ['min', 'max'],
                'seq': 'count',
                'session_tagged': 'first',
                'session_ble_id': 'first'
            })
        )
        
        # Flatten column names
        session_summary.columns = ['device_id', 'start', 'end', 'rows', 'tagged', 'ble_id']
        
        # Calculate duration as timestamp difference (not sum of time diffs)
        session_summary['duration_s'] = (session_summary['end'] - session_summary['start']).dt.total_seconds()
        session_summary['duration_min'] = session_summary['duration_s'] / 60.0
        
        session_summary = session_summary.reset_index()
        
        return df, session_summary
    
    def detect_anomalies(self) -> AnomalyReport:
        """Detect various anomalies in the data"""
        anomalies = AnomalyReport(
            short_sessions=[],
            missing_telemetry=[],
            missing_gps=[],
            low_battery=[]
        )
        
        if self.raw_df is None:
            return anomalies
        
        # Compute sessions on-the-fly
        telemetry_df, sessions_df = self._compute_sessions()
        
        # Very short sessions (< 5 minutes)
        short_sessions = sessions_df[sessions_df['duration_min'] < 5]
        anomalies.short_sessions = [
            {
                "session_id": row['session_id'],
                "device_id": row['device_id'],
                "duration_min": row['duration_min'],
                "start": row['start'].isoformat()
            }
            for _, row in short_sessions.iterrows()
        ]
        
        # Missing GPS values
        missing_gps = self.raw_df[
            self.raw_df['gps_lat'].isna() | 
            self.raw_df['gps_lon'].isna()
        ]
        
        if not missing_gps.empty:
            # Add session info to missing GPS records
            missing_with_sessions = missing_gps.merge(
                telemetry_df[['timestamp', 'session_id']], 
                on='timestamp', 
                how='left'
            )
            
            anomalies.missing_gps = [
                {
                    "session_id": row['session_id'] if pd.notna(row['session_id']) else 'unknown',
                    "device_id": row['device_id'],
                    "timestamp": row['timestamp'].isoformat(),
                    "seq": row['seq']
                }
                for _, row in missing_with_sessions.head(10).iterrows()
            ]
        
        # Low battery levels (< 20%)
        low_battery = self.raw_df[self.raw_df['battery_level'] < 20]
        if not low_battery.empty:
            # Add session info to low battery records
            low_with_sessions = low_battery.merge(
                telemetry_df[['timestamp', 'session_id']], 
                on='timestamp', 
                how='left'
            )
            
            anomalies.low_battery = [
                {
                    "session_id": row['session_id'] if pd.notna(row['session_id']) else 'unknown',
                    "device_id": row['device_id'],
                    "timestamp": row['timestamp'].isoformat(),
                    "battery_level": row['battery_level']
                }
                for _, row in low_with_sessions.head(10).iterrows()
            ]
        
        # Missing telemetry (sequence gaps)
        for session_id in telemetry_df['session_id'].unique():
            if pd.isna(session_id):
                continue
                
            session_data = telemetry_df[
                telemetry_df['session_id'] == session_id
            ].sort_values('seq')
            
            if len(session_data) > 1:
                seq_values = session_data['seq'].values
                gaps = []
                
                for i in range(1, len(seq_values)):
                    if seq_values[i] - seq_values[i-1] > 1:
                        gap_size = seq_values[i] - seq_values[i-1] - 1
                        gaps.append(gap_size)
                
                if gaps:
                    anomalies.missing_telemetry.append({
                        "session_id": session_id,
                        "device_id": session_data.iloc[0]['device_id'],
                        "gaps_count": len(gaps),
                        "max_gap": int(max(gaps))
                    })
        
        return anomalies
    
    def calculate_insights(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> DashboardInsights:
        """Calculate key insights for the dashboard"""
        
        if self.raw_df is None:
            return DashboardInsights(
                total_drilling_time_hours=0,
                total_sessions=0,
                average_session_length_min=0,
                tagged_sessions_percentage=0,
                operating_states_distribution={},
                low_battery_alerts=[],
                session_locations=[],
                anomalies={}
            )
        
        # Compute sessions and enriched data on-the-fly
        telemetry_df, sessions_df = self._compute_sessions()
        
        # Filter data by date range if provided
        filtered_df = self.raw_df.copy()
        filtered_sessions = sessions_df.copy()
        
        if start_date and end_date:
            start_dt = pd.to_datetime(start_date, utc=True)
            end_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            
            filtered_df = filtered_df[
                (filtered_df['timestamp'] >= start_dt) & 
                (filtered_df['timestamp'] <= end_dt)
            ]
            
            filtered_sessions = filtered_sessions[
                (filtered_sessions['start'] >= start_dt) & 
                (filtered_sessions['start'] <= end_dt)
            ]
        
        # Calculate metrics
        total_drilling_time_hours = 0
        total_sessions = 0
        average_session_length_min = 0
        tagged_sessions_percentage = 0
        
        if not filtered_sessions.empty:
            # Calculate actual drilling time (only when operating state = DRILL)
            drilling_records = filtered_df[filtered_df['current_amp'] > 4.5]  # DRILL state
            if not drilling_records.empty:
                # Each telemetry record represents 30 seconds of operation
                total_drilling_time_hours = len(drilling_records) * 30 / 3600
            
            total_sessions = len(filtered_sessions)
            average_session_length_min = filtered_sessions['duration_min'].mean()
            tagged_sessions_percentage = (filtered_sessions['tagged'].sum() / total_sessions) * 100
        
        # Operating states distribution - Option 2: Operational Time Only (excluding OFF)
        operating_states_distribution = {}
        if not filtered_df.empty:
            # Compute operating states for filtered data
            filtered_df['op_state'] = filtered_df['current_amp'].apply(lambda x: self.derive_operating_state(x).value)
            state_counts = filtered_df['op_state'].value_counts()
            total_readings = len(filtered_df)
            
            # Only include operational states (exclude OFF time between sessions)
            for state, count in state_counts.items():
                time_hours = count * 30 / 3600  # 30 seconds per record
                percentage = (count / total_readings) * 100
                operating_states_distribution[state] = percentage
        
        # Low battery alerts
        low_battery_alerts = []
        if not filtered_df.empty:
            low_battery = filtered_df[filtered_df['battery_level'] < 25]
            if not low_battery.empty:
                # Add session info
                low_with_sessions = low_battery.merge(
                    telemetry_df[['timestamp', 'session_id']], 
                    on='timestamp', 
                    how='left'
                )
                
                low_battery_alerts = [
                    {
                        "device_id": row['device_id'],
                        "session_id": row['session_id'] if pd.notna(row['session_id']) else 'unknown',
                        "timestamp": row['timestamp'].isoformat(),
                        "battery_level": row['battery_level']
                    }
                    for _, row in low_with_sessions.head(5).iterrows()
                ]
        
        # Session locations for map
        session_locations = []
        if not filtered_sessions.empty:
            for _, session in filtered_sessions.iterrows():
                session_telemetry = filtered_df[
                    filtered_df['timestamp'].between(session['start'], session['end'])
                ]
                
                if not session_telemetry.empty:
                    # Get first valid GPS coordinates
                    valid_gps = session_telemetry.dropna(subset=['gps_lat', 'gps_lon'])
                    if not valid_gps.empty:
                        first_point = valid_gps.iloc[0]
                        session_locations.append({
                            "session_id": session['session_id'],
                            "device_id": session['device_id'],
                            "lat": first_point['gps_lat'],
                            "lon": first_point['gps_lon'],
                            "tagged": session['tagged'],
                            "duration_min": session['duration_min'],
                            "start": session['start'].isoformat()
                        })
        
        # Anomalies
        anomalies_report = self.detect_anomalies()
        anomalies = {
            "short_sessions_count": len(anomalies_report.short_sessions),
            "missing_telemetry_count": len(anomalies_report.missing_telemetry),
            "missing_gps_count": len(anomalies_report.missing_gps),
            "low_battery_count": len(anomalies_report.low_battery)
        }
        
        return DashboardInsights(
            total_drilling_time_hours=round(total_drilling_time_hours, 2),
            total_sessions=total_sessions,
            average_session_length_min=round(average_session_length_min, 2),
            tagged_sessions_percentage=round(tagged_sessions_percentage, 2),
            operating_states_distribution=operating_states_distribution,
            low_battery_alerts=low_battery_alerts,
            session_locations=session_locations,
            anomalies=anomalies,
            # Add total operational time for OFF time calculation
            total_operational_time_hours=round(len(filtered_df) * 30 / 3600, 2) if not filtered_df.empty else 0,
            # Add total timespan for complete OFF time calculation
            total_timespan_hours=round((filtered_df['timestamp'].max() - filtered_df['timestamp'].min()).total_seconds() / 3600, 2) if not filtered_df.empty else 0
        )
    
    def get_session_timeline(self, device_id: Optional[str] = None) -> List[Dict]:
        """Get timeline data for sessions"""
        
        if self.raw_df is None:
            return []
        
        # Compute sessions on-the-fly
        telemetry_df, sessions_df = self._compute_sessions()
        
        # Filter by device if specified
        if device_id:
            sessions_df = sessions_df[sessions_df['device_id'] == device_id]
        
        timeline = []
        for _, session in sessions_df.iterrows():
            timeline.append({
                "session_id": session['session_id'],
                "device_id": session['device_id'],
                "start": session['start'].isoformat(),
                "end": session['end'].isoformat(),
                "duration_min": session['duration_min'],
                "tagged": session['tagged']
            })
        
        return sorted(timeline, key=lambda x: x['start'])
    
    def get_battery_trends(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[Dict]:
        """Get battery level trends over time"""
        
        if self.raw_df is None:
            return []
        
        # Compute sessions and telemetry data on-the-fly
        telemetry_df, sessions_df = self._compute_sessions()
        
        # Get all battery data
        battery_data = telemetry_df[['timestamp', 'device_id', 'battery_level', 'session_id']].copy()
        
        # Filter by date range if provided
        if start_date and end_date:
            start_dt = pd.to_datetime(start_date, utc=True)
            end_dt = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            
            battery_data = battery_data[
                (battery_data['timestamp'] >= start_dt) & 
                (battery_data['timestamp'] <= end_dt)
            ]
        
        trends = []
        for _, row in battery_data.iterrows():
            trends.append({
                "timestamp": row['timestamp'].isoformat(),
                "device_id": row['device_id'],
                "battery_level": row['battery_level'],
                "session_id": row['session_id']
            })
        
        return sorted(trends, key=lambda x: x['timestamp'])