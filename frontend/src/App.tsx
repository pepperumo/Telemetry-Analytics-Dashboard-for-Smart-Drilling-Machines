import React, { useState, useEffect, Suspense, lazy } from 'react';
import KPIDashboard from './components/KPIDashboard';
import OperatingStatesChart from './components/OperatingStatesChart';
import SessionsMap from './components/SessionsMap';
import AnomalyDetection from './components/AnomalyDetection';
import BatteryTrends from './components/BatteryTrends';

// Lazy load ML components for better performance
const EquipmentHealthScores = lazy(() => import('./components/EquipmentHealthScores'));
const MaintenanceTimeline = lazy(() => import('./components/MaintenanceTimeline'));
const PatternAnalysisCharts = lazy(() => import('./components/PatternAnalysisCharts'));
const MLInsightsSummary = lazy(() => import('./components/MLInsightsSummary'));
import { apiService } from './services/api';
import { mlApiService } from './services/mlApi';
import type { 
  DashboardInsights, 
  AnomalyReport, 
  BatteryTrend 
} from './types';

interface LoadingState {
  insights: boolean;
  anomalies: boolean;
  battery: boolean;
  mlHealth: boolean;
}

type DashboardView = 'analytics' | 'ml-insights';
type MLSection = 'overview' | 'health-scores' | 'maintenance' | 'patterns';

const App: React.FC = () => {
  const [insights, setInsights] = useState<DashboardInsights | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [batteryTrends, setBatteryTrends] = useState<BatteryTrend[]>([]);
  const [mlSystemHealthy, setMlSystemHealthy] = useState<boolean>(false);
  const [loading, setLoading] = useState<LoadingState>({
    insights: true,
    anomalies: true,
    battery: true,
    mlHealth: true
  });
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<DashboardView>('analytics');
  const [currentMLSection, setCurrentMLSection] = useState<MLSection>('overview');
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

      // Check ML system health
      setLoading(prev => ({ ...prev, mlHealth: true }));
      try {
        const mlHealthy = await mlApiService.isMLSystemHealthy();
        setMlSystemHealthy(mlHealthy);
      } catch (mlError) {
        console.warn('ML system not available:', mlError);
        setMlSystemHealthy(false);
      }
      setLoading(prev => ({ ...prev, mlHealth: false }));

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading({
        insights: false,
        anomalies: false,
        battery: false,
        mlHealth: false
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

  const handleMLDrillDown = (section: string) => {
    switch (section) {
      case 'health-scores':
        setCurrentMLSection('health-scores');
        break;
      case 'maintenance':
        setCurrentMLSection('maintenance');
        break;
      case 'patterns':
        setCurrentMLSection('patterns');
        break;
      default:
        setCurrentMLSection('overview');
        break;
    }
  };

  // ML Component Loading Fallback
  const MLComponentLoader = () => (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="animate-pulse">
        <div className="h-6 bg-gray-300 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          <div className="h-32 bg-gray-300 rounded"></div>
        </div>
      </div>
    </div>
  );

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

  const isLoading = loading.insights || loading.anomalies || loading.battery || loading.mlHealth;

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
              <div className="flex items-center space-x-4">
                <p className="text-gray-600">
                  Telemetry insights for drilling machines in July 2025
                </p>
                {/* ML System Status Indicator */}
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium ${
                  mlSystemHealthy 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    mlSystemHealthy ? 'bg-green-400' : 'bg-yellow-400'
                  }`}></div>
                  <span>
                    ML System {mlSystemHealthy ? 'Active' : 'Unavailable'}
                  </span>
                </div>
              </div>
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
        
        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 border-b border-gray-200">
            <button
              onClick={() => setCurrentView('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                currentView === 'analytics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Analytics Dashboard
            </button>
            <button
              onClick={() => setCurrentView('ml-insights')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                currentView === 'ml-insights'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🤖 ML Insights
              {mlSystemHealthy && (
                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Loading State */}
        {isLoading && (
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading dashboard data...</span>
            </div>
          </div>
        )}

        {/* Analytics Dashboard View */}
        {currentView === 'analytics' && (
          <div className="space-y-8">
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
        )}

        {/* ML Insights Dashboard View */}
        {currentView === 'ml-insights' && (
          <div className="space-y-8">
            {/* ML Dashboard Header */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    🤖 Machine Learning Insights
                  </h2>
                  <p className="text-gray-600 mt-2">
                    AI-powered equipment health monitoring, predictive maintenance, and operational optimization
                  </p>
                </div>
                <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                  mlSystemHealthy 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <div className={`w-3 h-3 rounded-full ${
                    mlSystemHealthy ? 'bg-green-500' : 'bg-yellow-500'
                  }`}></div>
                  <span className={`font-medium ${
                    mlSystemHealthy ? 'text-green-800' : 'text-yellow-800'
                  }`}>
                    ML System {mlSystemHealthy ? 'Online' : 'Limited Mode'}
                  </span>
                </div>
              </div>
            </div>

            {/* ML Insights Summary */}
            {currentMLSection === 'overview' && !loading.mlHealth && (
              <Suspense fallback={<MLComponentLoader />}>
                <MLInsightsSummary onDrillDown={handleMLDrillDown} />
              </Suspense>
            )}

            {/* Section Navigation */}
            {currentMLSection !== 'overview' && (
              <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setCurrentMLSection('overview')}
                    className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
                  >
                    ← Back to ML Overview
                  </button>
                  <div className="text-sm text-gray-600">
                    {currentMLSection === 'health-scores' && 'Equipment Health Analysis'}
                    {currentMLSection === 'maintenance' && 'Predictive Maintenance'}
                    {currentMLSection === 'patterns' && 'Pattern Analysis'}
                  </div>
                </div>
              </div>
            )}

            {/* Equipment Health Scores */}
            {(currentMLSection === 'overview' || currentMLSection === 'health-scores') && !loading.mlHealth && (
              <Suspense fallback={<MLComponentLoader />}>
                <EquipmentHealthScores />
              </Suspense>
            )}

            {/* Maintenance Timeline */}
            {(currentMLSection === 'overview' || currentMLSection === 'maintenance') && !loading.mlHealth && (
              <Suspense fallback={<MLComponentLoader />}>
                <MaintenanceTimeline />
              </Suspense>
            )}

            {/* Pattern Analysis Charts */}
            {(currentMLSection === 'overview' || currentMLSection === 'patterns') && !loading.mlHealth && (
              <Suspense fallback={<MLComponentLoader />}>
                <PatternAnalysisCharts />
              </Suspense>
            )}

            {/* ML System Information - Only in overview */}
            {currentMLSection === 'overview' && (
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-3">
                  💡 About ML Insights
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <h4 className="font-medium mb-2">🎯 Health Scoring</h4>
                    <p>Real-time equipment health analysis using electrical current patterns, battery performance, and GPS reliability metrics.</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">🔮 Predictive Maintenance</h4>
                    <p>AI-powered maintenance timeline predicting equipment issues before they occur, with actionable recommendations.</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">📊 Pattern Analysis</h4>
                    <p>Operational efficiency insights identifying optimal drilling parameters and energy usage patterns.</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">⚡ Real-time Processing</h4>
                    <p>Live analysis of 3,900+ telemetry records generating immediate insights for equipment optimization.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
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
