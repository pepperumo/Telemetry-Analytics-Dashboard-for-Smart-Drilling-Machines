/**
 * ML API Integration utilities
 * Helper functions for integrating ML API with existing frontend components
 */

import { mlApiService } from '../services/mlApi';
import type { 
  HealthScoreResponse, 
  MaintenanceAlertResponse, 
  AlertSeverity,
  RiskLevel 
} from '../types/ml';

/**
 * Format health score for display
 */
export const formatHealthScore = (score: number): string => {
  return `${Math.round(score)}%`;
};

/**
 * Get risk level color for UI styling
 */
export const getRiskLevelColor = (riskLevel: RiskLevel): string => {
  switch (riskLevel) {
    case 'low':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'high':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

/**
 * Get alert severity color for UI styling
 */
export const getAlertSeverityColor = (severity: AlertSeverity): string => {
  switch (severity) {
    case 'low':
      return 'text-blue-600 bg-blue-50 border-blue-200';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'high':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

/**
 * Format confidence score for display
 */
export const formatConfidenceScore = (confidence: number): string => {
  return `${Math.round(confidence * 100)}%`;
};

/**
 * Get the most critical device based on health scores
 */
export const getMostCriticalDevice = (healthScores: HealthScoreResponse[]): HealthScoreResponse | null => {
  if (healthScores.length === 0) return null;
  
  // Sort by health score ascending (lowest score = most critical)
  const sorted = [...healthScores].sort((a, b) => a.health_score - b.health_score);
  return sorted[0];
};

/**
 * Get devices by risk level
 */
export const getDevicesByRiskLevel = (
  healthScores: HealthScoreResponse[], 
  riskLevel: RiskLevel
): HealthScoreResponse[] => {
  return healthScores.filter(device => device.risk_level === riskLevel);
};

/**
 * Calculate fleet health summary
 */
export const calculateFleetHealthSummary = (healthScores: HealthScoreResponse[]) => {
  if (healthScores.length === 0) {
    return {
      averageHealth: 0,
      totalDevices: 0,
      riskBreakdown: { low: 0, medium: 0, high: 0, critical: 0 },
      healthyDevices: 0,
      atRiskDevices: 0,
    };
  }

  const averageHealth = healthScores.reduce((sum, device) => sum + device.health_score, 0) / healthScores.length;
  
  const riskBreakdown = healthScores.reduce((acc, device) => {
    acc[device.risk_level] = (acc[device.risk_level] || 0) + 1;
    return acc;
  }, { low: 0, medium: 0, high: 0, critical: 0 } as Record<RiskLevel, number>);
  
  const healthyDevices = riskBreakdown.low;
  const atRiskDevices = riskBreakdown.medium + riskBreakdown.high + riskBreakdown.critical;

  return {
    averageHealth,
    totalDevices: healthScores.length,
    riskBreakdown,
    healthyDevices,
    atRiskDevices,
  };
};

/**
 * Sort alerts by priority (severity + creation time)
 */
export const sortAlertsByPriority = (alerts: MaintenanceAlertResponse[]): MaintenanceAlertResponse[] => {
  const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 } as const;
  
  return [...alerts].sort((a, b) => {
    // First sort by severity (descending)
    const severityDiff = severityOrder[b.severity] - severityOrder[a.severity];
    if (severityDiff !== 0) return severityDiff;
    
    // Then by creation time (newest first)
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
};

/**
 * Group alerts by device
 */
export const groupAlertsByDevice = (alerts: MaintenanceAlertResponse[]): Record<string, MaintenanceAlertResponse[]> => {
  return alerts.reduce((acc, alert) => {
    if (!acc[alert.device_id]) {
      acc[alert.device_id] = [];
    }
    acc[alert.device_id].push(alert);
    return acc;
  }, {} as Record<string, MaintenanceAlertResponse[]>);
};

/**
 * Check if ML system is available and show loading states appropriately
 */
export const useMLSystemStatus = () => {
  // This would typically be a React hook, but for now just return the service
  return {
    checkMLHealth: mlApiService.isMLSystemHealthy,
    getActiveAlertsCount: mlApiService.getActiveAlertsCount,
  };
};

/**
 * Format time until predicted failure
 */
export const formatTimeUntilFailure = (predictedFailureTime?: string): string => {
  if (!predictedFailureTime) return 'Unknown';
  
  const now = new Date();
  const failureTime = new Date(predictedFailureTime);
  const diffMs = failureTime.getTime() - now.getTime();
  
  if (diffMs <= 0) return 'Overdue';
  
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  
  if (diffDays > 0) {
    return `${diffDays} day${diffDays === 1 ? '' : 's'}${diffHours > 0 ? ` ${diffHours}h` : ''}`;
  } else {
    return `${diffHours} hour${diffHours === 1 ? '' : 's'}`;
  }
};

/**
 * Check if an alert is urgent (critical severity or failure within 24 hours)
 */
export const isAlertUrgent = (alert: MaintenanceAlertResponse): boolean => {
  if (alert.severity === 'critical') return true;
  
  if (alert.predicted_failure_time) {
    const now = new Date();
    const failureTime = new Date(alert.predicted_failure_time);
    const hoursUntilFailure = (failureTime.getTime() - now.getTime()) / (1000 * 60 * 60);
    return hoursUntilFailure <= 24;
  }
  
  return false;
};