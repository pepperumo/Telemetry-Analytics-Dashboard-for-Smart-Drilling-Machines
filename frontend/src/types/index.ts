export interface DashboardInsights {
  total_drilling_time_hours: number;
  total_sessions: number;
  average_session_length_min: number;
  tagged_sessions_percentage: number;
  operating_states_distribution: { [key: string]: number };
  low_battery_alerts: BatteryAlert[];
  session_locations: SessionLocation[];
  anomalies: AnomalySummary;
  total_operational_time_hours?: number;
  total_timespan_hours?: number;
}

export interface BatteryAlert {
  device_id: string;
  session_id: string;
  timestamp: string;
  battery_level: number;
}

export interface SessionLocation {
  session_id: string;
  device_id: string;
  lat: number;
  lon: number;
  tagged: boolean;
  duration_min: number;
  start: string;
}

export interface AnomalySummary {
  short_sessions_count: number;
  missing_telemetry_count: number;
  missing_gps_count: number;
  low_battery_count: number;
}

export interface AnomalyReport {
  short_sessions: ShortSession[];
  missing_telemetry: MissingTelemetry[];
  missing_gps: MissingGPS[];
  low_battery: LowBattery[];
}

export interface ShortSession {
  session_id: string;
  device_id: string;
  duration_min: number;
  start: string;
}

export interface MissingTelemetry {
  session_id: string;
  device_id: string;
  gaps_count: number;
  max_gap: number;
}

export interface MissingGPS {
  session_id: string;
  device_id: string;
  timestamp: string;
  seq: number;
}

export interface LowBattery {
  session_id: string;
  device_id: string;
  timestamp: string;
  battery_level: number;
}

export interface SessionTimeline {
  session_id: string;
  device_id: string;
  start: string;
  end: string;
  duration_min: number;
  tagged: boolean;
}

export interface BatteryTrend {
  timestamp: string;
  device_id: string;
  battery_level: number;
  session_id: string;
}

export interface SessionData {
  session_id: string;
  device_id: string;
  start: string;
  end: string;
  duration_min: number;
  tagged: boolean;
}

export type OperatingState = 'OFF' | 'STANDBY' | 'SPIN' | 'DRILL';