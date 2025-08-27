/**
 * ML API Service
 * Handles all ML-related API calls including health scores, alerts, and model management
 */

import type {
  HealthScoreResponse,
  HealthScoresListResponse,
  HealthScoreFilters,
  ModelStatusResponse,
  MaintenanceAlertResponse,
  AlertsListResponse,
  AlertListParams,
  AlertAcknowledgmentRequest,
  AlertAcknowledgmentResponse,
  AlertSuppressionRequest,
  AlertSuppressionResponse,
  AlertStatisticsResponse,
  MLTrainingRequest,
  MLTrainingResponse,
  MLHealthCheckResponse,
  MLErrorResponse,
} from '../types/ml';

const ML_API_BASE_URL = 'http://localhost:8000/api/ml';

/**
 * ML API Service class following existing API patterns
 */
class MLApiService {
  /**
   * Generic fetch method with error handling
   */
  private async fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        // Try to parse error response
        let errorResponse: MLErrorResponse;
        try {
          errorResponse = await response.json();
        } catch {
          errorResponse = {
            error: 'HTTP_ERROR',
            message: `HTTP error! status: ${response.status}`,
            timestamp: new Date().toISOString(),
          };
        }
        
        throw new Error(`ML API Error: ${errorResponse.message} (${errorResponse.error})`);
      }

      return response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(`ML API request failed: ${String(error)}`);
    }
  }

  /**
   * Build URL with query parameters
   */
  private buildUrl(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(`${ML_API_BASE_URL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => url.searchParams.append(key, String(v)));
          } else {
            url.searchParams.set(key, String(value));
          }
        }
      });
    }
    
    return url.toString();
  }

  // Health Score endpoints
  
  /**
   * Get health scores for all devices or filtered subset
   */
  async getHealthScores(filters?: HealthScoreFilters): Promise<HealthScoresListResponse> {
    const url = this.buildUrl('/health-scores', filters);
    return this.fetchJson<HealthScoresListResponse>(url);
  }

  /**
   * Get health score for a specific device
   */
  async getDeviceHealthScore(deviceId: string): Promise<HealthScoreResponse> {
    const url = `${ML_API_BASE_URL}/health-scores/${encodeURIComponent(deviceId)}`;
    return this.fetchJson<HealthScoreResponse>(url);
  }

  // Model Management endpoints

  /**
   * Get ML model status and metadata
   */
  async getModelStatus(): Promise<ModelStatusResponse> {
    return this.fetchJson<ModelStatusResponse>(`${ML_API_BASE_URL}/model-status`);
  }

  /**
   * Train or retrain ML models
   */
  async trainModel(request?: MLTrainingRequest): Promise<MLTrainingResponse> {
    return this.fetchJson<MLTrainingResponse>(`${ML_API_BASE_URL}/train`, {
      method: 'POST',
      body: JSON.stringify(request || {}),
    });
  }

  // Alert Management endpoints

  /**
   * Get alerts with filtering and pagination
   */
  async getAlerts(params?: AlertListParams): Promise<AlertsListResponse> {
    const url = this.buildUrl('/alerts', params);
    return this.fetchJson<AlertsListResponse>(url);
  }

  /**
   * Generate new alerts manually
   */
  async generateAlerts(deviceId?: string): Promise<AlertsListResponse> {
    const params = deviceId ? { device_id: deviceId } : undefined;
    const url = this.buildUrl('/alerts/generate', params);
    return this.fetchJson<AlertsListResponse>(url, { method: 'POST' });
  }

  /**
   * Acknowledge a specific alert
   */
  async acknowledgeAlert(
    alertId: string, 
    request: AlertAcknowledgmentRequest
  ): Promise<AlertAcknowledgmentResponse> {
    const url = `${ML_API_BASE_URL}/alerts/${encodeURIComponent(alertId)}/acknowledge`;
    return this.fetchJson<AlertAcknowledgmentResponse>(url, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Resolve a specific alert
   */
  async resolveAlert(
    alertId: string, 
    request: AlertAcknowledgmentRequest
  ): Promise<AlertAcknowledgmentResponse> {
    const url = `${ML_API_BASE_URL}/alerts/${encodeURIComponent(alertId)}/resolve`;
    return this.fetchJson<AlertAcknowledgmentResponse>(url, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Suppress alerts for a device and alert type
   */
  async suppressAlerts(request: AlertSuppressionRequest): Promise<AlertSuppressionResponse> {
    return this.fetchJson<AlertSuppressionResponse>(`${ML_API_BASE_URL}/alerts/suppress`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get alert statistics and summary
   */
  async getAlertStatistics(): Promise<AlertStatisticsResponse> {
    return this.fetchJson<AlertStatisticsResponse>(`${ML_API_BASE_URL}/alerts/statistics`);
  }

  // Health Check endpoint

  /**
   * Check ML system health and status
   */
  async healthCheck(): Promise<MLHealthCheckResponse> {
    return this.fetchJson<MLHealthCheckResponse>(`${ML_API_BASE_URL}/health`);
  }

  // Utility methods

  /**
   * Check if ML system is available and healthy
   */
  async isMLSystemHealthy(): Promise<boolean> {
    try {
      const health = await this.healthCheck();
      return health.status === 'healthy';
    } catch {
      return false;
    }
  }

  /**
   * Get the total number of active alerts
   */
  async getActiveAlertsCount(): Promise<number> {
    try {
      const stats = await this.getAlertStatistics();
      return stats.active_alerts;
    } catch {
      return 0;
    }
  }

  /**
   * Get alerts for a specific device
   */
  async getDeviceAlerts(deviceId: string): Promise<MaintenanceAlertResponse[]> {
    try {
      const response = await this.getAlerts({ 
        device_id: deviceId, 
        status: 'active'
      });
      return response.alerts;
    } catch {
      return [];
    }
  }

  /**
   * Get high-priority alerts (high and critical severity)
   */
  async getHighPriorityAlerts(): Promise<MaintenanceAlertResponse[]> {
    try {
      const [highAlerts, criticalAlerts] = await Promise.all([
        this.getAlerts({ severity: 'high', status: 'active' }),
        this.getAlerts({ severity: 'critical', status: 'active' })
      ]);
      
      return [...criticalAlerts.alerts, ...highAlerts.alerts];
    } catch {
      return [];
    }
  }

  /**
   * Quick acknowledge with default user
   */
  async quickAcknowledgeAlert(alertId: string, acknowledgedBy: string = 'system'): Promise<boolean> {
    try {
      const response = await this.acknowledgeAlert(alertId, { acknowledged_by: acknowledgedBy });
      return response.success;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const mlApiService = new MLApiService();

// Export class for testing purposes
export { MLApiService };