import type {
  DashboardInsights,
  AnomalyReport,
  SessionTimeline,
  BatteryTrend,
  SessionData,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  private async fetchJson<T>(url: string): Promise<T> {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  async getInsights(startDate?: string, endDate?: string): Promise<DashboardInsights> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const url = `${API_BASE_URL}/insights${params.toString() ? `?${params.toString()}` : ''}`;
    return this.fetchJson<DashboardInsights>(url);
  }

  async getAnomalies(): Promise<AnomalyReport> {
    return this.fetchJson<AnomalyReport>(`${API_BASE_URL}/anomalies`);
  }

  async getSessionTimeline(deviceId?: string): Promise<{ timeline: SessionTimeline[] }> {
    const params = new URLSearchParams();
    if (deviceId) params.append('device_id', deviceId);
    
    const url = `${API_BASE_URL}/sessions/timeline${params.toString() ? `?${params.toString()}` : ''}`;
    return this.fetchJson<{ timeline: SessionTimeline[] }>(url);
  }

  async getBatteryTrends(startDate?: string, endDate?: string): Promise<{ trends: BatteryTrend[] }> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const url = `${API_BASE_URL}/battery/trends${params.toString() ? `?${params.toString()}` : ''}`;
    return this.fetchJson<{ trends: BatteryTrend[] }>(url);
  }

  async getDevices(): Promise<{ devices: string[] }> {
    return this.fetchJson<{ devices: string[] }>(`${API_BASE_URL}/devices`);
  }

  async getSessions(deviceId?: string, dateRange?: { startDate: string; endDate: string }): Promise<{ sessions: SessionData[] }> {
    const params = new URLSearchParams();
    if (deviceId) params.append('device_id', deviceId);
    if (dateRange) {
      params.append('start_date', dateRange.startDate);
      params.append('end_date', dateRange.endDate);
    }
    
    const url = `${API_BASE_URL}/sessions${params.toString() ? `?${params.toString()}` : ''}`;
    return this.fetchJson<{ sessions: SessionData[] }>(url);
  }

  async healthCheck(): Promise<{ status: string; data_loaded: boolean; timestamp: string }> {
    return this.fetchJson<{ status: string; data_loaded: boolean; timestamp: string }>(`${API_BASE_URL}/health`);
  }
}

export const apiService = new ApiService();