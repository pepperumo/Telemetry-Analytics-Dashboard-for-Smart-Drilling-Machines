/**
 * TypeScript interfaces for ML API endpoints
 * These types match the backend Pydantic models for type safety
 */

// Enums matching backend enums
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

export type AlertType = 
  | 'performance_degradation'
  | 'equipment_failure_risk'
  | 'battery_maintenance'
  | 'mechanical_wear'
  | 'thermal_stress'
  | 'electrical_anomaly';

export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'suppressed';

// Core ML interfaces
export interface ExplanatoryFactor {
  feature: string;
  value: number;
  importance: number;
  impact: string;
}

export interface HealthScoreResponse {
  device_id: string;
  health_score: number;
  confidence_interval: [number, number];
  risk_level: RiskLevel;
  explanatory_factors: ExplanatoryFactor[];
  last_calculated: string; // ISO datetime string
}

export interface HealthScoresListResponse {
  health_scores: HealthScoreResponse[];
  total_devices: number;
  average_health_score: number;
  at_risk_devices: number;
  filters_applied: Record<string, any>;
}

export interface ModelPerformanceMetrics {
  r2_score: number;
  rmse: number;
  cross_val_score: number;
  feature_count: number;
  training_samples: number;
}

export interface ModelStatusResponse {
  model_version: string;
  training_date: string; // ISO datetime string
  is_trained: boolean;
  performance_metrics?: ModelPerformanceMetrics;
  feature_importance_top_10: Array<Record<string, any>>;
  status: string;
  last_prediction_time?: string; // ISO datetime string
}

// Alert interfaces
export interface MaintenanceAlertResponse {
  id: string;
  device_id: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  description: string;
  predicted_failure_time?: string; // ISO datetime string
  confidence_score: number;
  recommended_actions: string[];
  affected_systems: string[];
  created_at: string; // ISO datetime string
  acknowledged_at?: string; // ISO datetime string
  resolved_at?: string; // ISO datetime string
  metadata: Record<string, any>;
}

export interface AlertsListResponse {
  alerts: MaintenanceAlertResponse[];
  total_count: number;
  page: number;
  per_page: number;
  has_next: boolean;
}

// Request interfaces
export interface HealthScoreFilters {
  device_ids?: string[];
  min_health_score?: number;
  max_health_score?: number;
  risk_levels?: RiskLevel[];
  start_date?: string; // YYYY-MM-DD format
  end_date?: string; // YYYY-MM-DD format
}

export interface AlertFilters {
  device_id?: string;
  severity?: AlertSeverity;
  status?: AlertStatus;
  alert_type?: AlertType;
  created_after?: string; // ISO datetime string
  created_before?: string; // ISO datetime string;
}

export interface AlertAcknowledgmentRequest {
  acknowledged_by: string;
  notes?: string;
}

export interface AlertAcknowledgmentResponse {
  success: boolean;
  message: string;
  alert?: MaintenanceAlertResponse;
}

export interface AlertSuppressionRequest {
  device_id: string;
  alert_type: AlertType;
  suppress_hours?: number;
  reason?: string;
}

export interface AlertSuppressionResponse {
  success: boolean;
  message: string;
}

export interface AlertStatisticsResponse {
  active_alerts: number;
  total_generated: number;
  severity_breakdown: Record<string, number>;
  average_resolution_time_hours: number;
  suppression_rules_active: number;
  training_time_seconds: number;
}

export interface MLTrainingRequest {
  force_retrain?: boolean;
}

export interface MLTrainingResponse {
  status: string;
  message: string;
  model_metadata?: ModelStatusResponse;
}

// Pagination interfaces
export interface PaginationParams {
  page?: number;
  per_page?: number;
}

export interface AlertListParams extends AlertFilters, PaginationParams {
  // Combines alert filters with pagination
}

// Error response interface
export interface MLErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// Health check response
export interface MLHealthCheckResponse {
  status: string;
  is_trained: boolean;
  model_version?: string;
  timestamp: string;
}