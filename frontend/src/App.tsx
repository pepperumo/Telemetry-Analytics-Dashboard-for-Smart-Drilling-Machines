import React, { useState, useEffect } from 'react';
import KPIDashboard from './components/KPIDashboard';
import OperatingStatesChart from './components/OperatingStatesChart';
import SessionsMap from './components/SessionsMap';
import AnomalyDetection from './components/AnomalyDetection';
import BatteryTrends from './components/BatteryTrends';
import { apiService } from './services/api';
import type { 
  DashboardInsights, 
  AnomalyReport, 
  BatteryTrend 
} from './types';

interface LoadingState {
  insights: boolean;
  anomalies: boolean;
  battery: boolean;
}

const App: React.FC = () => {
  const [insights, setInsights] = useState<DashboardInsights | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [batteryTrends, setBatteryTrends] = useState<BatteryTrend[]>([]);
  const [loading, setLoading] = useState<LoadingState>({
    insights: true,
    anomalies: true,
    battery: true
  });
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start: '2025-07-01',
    end: '2025-07-31'
  });

  const loadData = async () => {
    try {
      setError(null);
      
      // Load insights
      setLoading(prev => ({ ...prev, insights: true }));
      const insightsData = await apiService.getInsights(dateRange.start, dateRange.end);
      setInsights(insightsData);
      setLoading(prev => ({ ...prev, insights: false }));

      // Load anomalies
      setLoading(prev => ({ ...prev, anomalies: true }));
      const anomaliesData = await apiService.getAnomalies();
      setAnomalies(anomaliesData);
      setLoading(prev => ({ ...prev, anomalies: false }));

      // Load battery trends
      setLoading(prev => ({ ...prev, battery: true }));
      const batteryData = await apiService.getBatteryTrends(dateRange.start, dateRange.end);
      setBatteryTrends(batteryData.trends);
      setLoading(prev => ({ ...prev, battery: false }));

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading({
        insights: false,
        anomalies: false,
        battery: false
      });
    }
  };

  useEffect(() => {
    loadData();
  }, [dateRange]);

  const handleDateRangeChange = (field: 'start' | 'end', value: string) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200 max-w-md w-full">
          <div className="flex items-center mb-4">
            <svg className="w-8 h-8 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900">Connection Error</h2>
          </div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const isLoading = loading.insights || loading.anomalies || loading.battery;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Smart Drilling Analytics Dashboard
              </h1>
              <p className="text-gray-600">
                Telemetry insights for drilling machines in July 2025
              </p>
            </div>
            
            {/* Date Range Selector */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">From:</label>
                <input
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => handleDateRangeChange('start', e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                />
              </div>
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">To:</label>
                <input
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => handleDateRangeChange('end', e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                />
              </div>
              <button
                onClick={loadData}
                disabled={isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {isLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Loading State */}
          {isLoading && (
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Loading dashboard data...</span>
              </div>
            </div>
          )}

          {/* KPI Dashboard */}
          {insights && !loading.insights && (
            <KPIDashboard insights={insights} />
          )}

          {/* Operating States */}
          {insights && !loading.insights && (
            <OperatingStatesChart insights={insights} />
          )}

          {/* Sessions Map and Battery Trends */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {insights && !loading.insights && (
              <SessionsMap locations={insights.session_locations} />
            )}
            
            {!loading.battery && (
              <BatteryTrends trends={batteryTrends} dateRange={{ startDate: dateRange.start, endDate: dateRange.end }} />
            )}
          </div>

          {/* Anomaly Detection */}
          {anomalies && insights && !loading.anomalies && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Anomaly Detection
              </h2>
              <AnomalyDetection 
                anomalies={anomalies} 
                anomalySummary={insights.anomalies}
              />
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">
                Smart Drilling Machine Telemetry Analytics Dashboard
              </p>
              <p className="text-xs text-gray-500">
                Data processed from drilling sessions in Berlin area, July 2025
              </p>
            </div>
            <div className="text-sm text-gray-500">
              Last updated: {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
