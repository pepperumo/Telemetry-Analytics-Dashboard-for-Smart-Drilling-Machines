import type {
  DashboardInsights,
  AnomalyReport,
  SessionTimeline,
  BatteryTrend,
  SessionData,
} from '../types';

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // If running in development (localhost), use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/v1';
  }
  
  // For GitHub Pages or external access, use HTTPS to avoid Mixed Content issues
  const BACKEND_IP = import.meta.env.VITE_BACKEND_IP || 'localhost';
  const USE_HTTPS = import.meta.env.VITE_USE_HTTPS === 'true';
  
  // Force HTTPS for GitHub Pages to avoid Mixed Content issues
  const protocol = 'https';  // Always use HTTPS for external access
  const apiUrl = `${protocol}://${BACKEND_IP}:8000/api/v1`;
  
  // Debug logging
  console.log('Frontend Environment Debug:');
  console.log('- Current hostname:', window.location.hostname);
  console.log('- VITE_BACKEND_IP:', import.meta.env.VITE_BACKEND_IP);
  console.log('- VITE_USE_HTTPS:', import.meta.env.VITE_USE_HTTPS);
  console.log('- Raw env object:', import.meta.env);
  console.log('- Resolved BACKEND_IP:', BACKEND_IP);
  console.log('- Using protocol:', protocol);
  console.log('- Final API URL:', apiUrl);
  
  return apiUrl;
};

const API_BASE_URL = getApiBaseUrl();

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