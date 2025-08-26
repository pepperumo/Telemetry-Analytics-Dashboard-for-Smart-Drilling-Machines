import React, { useState, useEffect, useMemo } from 'react';
import { 
  AreaChart, 
  Area, 
  Line,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { mlApiService } from '../services/mlApi';
import { 
  formatHealthScore, 
  getRiskLevelColor,
  calculateFleetHealthSummary,
  getMostCriticalDevice
} from '../utils/mlUtils';
import { 
  generateHealthScoresFromTelemetry,
  generateAlertsFromHealthScores
} from '../utils/fallbackML';
import type { 
  HealthScoreResponse, 
  RiskLevel, 
  MaintenanceAlertResponse 
} from '../types/ml';

interface HealthScoreGaugeProps {
  device: HealthScoreResponse;
  onClick: () => void;
  isSelected: boolean;
}

const HealthScoreGauge: React.FC<HealthScoreGaugeProps> = ({ device, onClick, isSelected }) => {
  const percentage = device.health_score;
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // yellow
    if (score >= 40) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const riskColors = getRiskLevelColor(device.risk_level).split(' ');
  const bgColor = riskColors.find(c => c.includes('bg-'))?.replace('bg-', '') || 'gray-50';

  return (
    <div 
      className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'border-blue-500 shadow-lg bg-blue-50' 
          : `border-gray-200 hover:border-gray-300 bg-${bgColor}`
      }`}
      onClick={onClick}
    >
      {/* Risk level indicator */}
      <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(device.risk_level)}`}>
        {device.risk_level.toUpperCase()}
      </div>
      
      {/* Gauge */}
      <div className="flex flex-col items-center">
        <div className="relative w-24 h-24">
          <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="#e5e7eb"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke={getScoreColor(percentage)}
              strokeWidth="8"
              fill="none"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
          </svg>
          {/* Score text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg font-bold text-gray-900">{Math.round(percentage)}%</span>
          </div>
        </div>
        
        {/* Device info */}
        <div className="mt-3 text-center">
          <h4 className="font-medium text-gray-900 text-sm">{device.device_id}</h4>
          <p className="text-xs text-gray-500 mt-1">
            Updated: {new Date(device.last_calculated).toLocaleDateString()}
          </p>
        </div>
        
        {/* Confidence interval */}
        <div className="mt-2 text-xs text-gray-600 text-center">
          <span>CI: {Math.round(device.confidence_interval[0])}% - {Math.round(device.confidence_interval[1])}%</span>
        </div>
      </div>
    </div>
  );
};

interface HealthTrendChartProps {
  selectedDevice: HealthScoreResponse | null;
}

const HealthTrendChart: React.FC<HealthTrendChartProps> = ({ selectedDevice }) => {
  // Simulate historical health data for visualization
  const historicalData = useMemo(() => {
    if (!selectedDevice) return [];
    
    const baseScore = selectedDevice.health_score;
    const data = [];
    const now = new Date();
    
    // Generate 30 days of historical data
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      // Simulate score variation with some trend
      const variation = (Math.random() - 0.5) * 10;
      const trendFactor = (29 - i) * 0.5; // Slight decline over time
      const score = Math.max(0, Math.min(100, baseScore + variation - trendFactor));
      
      data.push({
        date: date.toISOString().split('T')[0],
        displayDate: date.toLocaleDateString(),
        health_score: Math.round(score),
        confidence_low: Math.round(Math.max(0, score - 5)),
        confidence_high: Math.round(Math.min(100, score + 5)),
      });
    }
    
    return data;
  }, [selectedDevice]);

  if (!selectedDevice) {
    return (
      <div className="h-80 flex items-center justify-center bg-gray-100 rounded">
        <p className="text-gray-500">Select a device to view health trends</p>
      </div>
    );
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={historicalData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => new Date(date).toLocaleDateString()}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            label={{ value: 'Health Score (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip 
            formatter={(value: number, name: string) => [
              `${value}%`, 
              name === 'health_score' ? 'Health Score' : 
              name === 'confidence_low' ? 'Lower CI' : 'Upper CI'
            ]}
            labelFormatter={(date: string) => new Date(date).toLocaleDateString()}
          />
          <Legend />
          
          {/* Confidence interval area */}
          <Area
            type="monotone"
            dataKey="confidence_high"
            stackId="1"
            stroke="none"
            fill="#3b82f6"
            fillOpacity={0.1}
          />
          <Area
            type="monotone"
            dataKey="confidence_low"
            stackId="1"
            stroke="none"
            fill="#ffffff"
            fillOpacity={1}
          />
          
          {/* Health score line */}
          <Line
            type="monotone"
            dataKey="health_score"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ r: 4 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

interface FleetHealthSummaryProps {
  healthScores: HealthScoreResponse[];
  alerts: MaintenanceAlertResponse[];
}

const FleetHealthSummary: React.FC<FleetHealthSummaryProps> = ({ healthScores, alerts }) => {
  const fleetSummary = calculateFleetHealthSummary(healthScores);
  const mostCritical = getMostCriticalDevice(healthScores);
  
  const riskData = [
    { name: 'Low Risk', count: fleetSummary.riskBreakdown.low, color: '#10b981' },
    { name: 'Medium Risk', count: fleetSummary.riskBreakdown.medium, color: '#f59e0b' },
    { name: 'High Risk', count: fleetSummary.riskBreakdown.high, color: '#f97316' },
    { name: 'Critical Risk', count: fleetSummary.riskBreakdown.critical, color: '#ef4444' },
  ].filter(item => item.count > 0);

  const activeAlertsCount = alerts.filter(alert => alert.status === 'active').length;
  const criticalAlertsCount = alerts.filter(alert => 
    alert.status === 'active' && alert.severity === 'critical'
  ).length;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Summary Stats */}
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Fleet Overview</h4>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Devices</span>
              <span className="text-xl font-semibold text-gray-900">{fleetSummary.totalDevices}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Health</span>
              <span className="text-xl font-semibold text-blue-600">
                {formatHealthScore(fleetSummary.averageHealth)}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Healthy Devices</span>
              <span className="text-xl font-semibold text-green-600">{fleetSummary.healthyDevices}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">At Risk Devices</span>
              <span className={`text-xl font-semibold ${
                fleetSummary.atRiskDevices > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {fleetSummary.atRiskDevices}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Alerts</span>
              <span className={`text-xl font-semibold ${
                activeAlertsCount > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {activeAlertsCount}
              </span>
            </div>
            
            {criticalAlertsCount > 0 && (
              <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                <span className="text-red-800 font-medium">🚨 Critical Alerts</span>
                <span className="text-xl font-bold text-red-600">{criticalAlertsCount}</span>
              </div>
            )}
          </div>
        </div>

        {/* Most Critical Device */}
        {mostCritical && (
          <div className="bg-white rounded-lg shadow-md p-6 border border-red-200">
            <h4 className="text-lg font-semibold text-red-900 mb-4">
              ⚠️ Most Critical Device
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Device ID</span>
                <span className="font-semibold">{mostCritical.device_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Health Score</span>
                <span className="font-semibold text-red-600">
                  {formatHealthScore(mostCritical.health_score)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Risk Level</span>
                <span className={`font-semibold px-2 py-1 rounded ${getRiskLevelColor(mostCritical.risk_level)}`}>
                  {mostCritical.risk_level.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Risk Distribution Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h4>
        {riskData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({name, count}) => `${name}: ${count}`}
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No devices to display
          </div>
        )}
      </div>
      
      {/* Health Score Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Health Score Distribution</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={[
                { range: '0-20%', count: healthScores.filter(d => d.health_score < 20).length, color: '#ef4444' },
                { range: '20-40%', count: healthScores.filter(d => d.health_score >= 20 && d.health_score < 40).length, color: '#f97316' },
                { range: '40-60%', count: healthScores.filter(d => d.health_score >= 40 && d.health_score < 60).length, color: '#f59e0b' },
                { range: '60-80%', count: healthScores.filter(d => d.health_score >= 60 && d.health_score < 80).length, color: '#3b82f6' },
                { range: '80-100%', count: healthScores.filter(d => d.health_score >= 80).length, color: '#10b981' },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip formatter={(value) => [`${value} devices`, 'Count']} />
              <Bar dataKey="count" fill="#3b82f6">
                {healthScores.length > 0 && (
                  <Cell fill="#ef4444" />
                )}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface ExplanatoryFactorsProps {
  device: HealthScoreResponse;
}

const ExplanatoryFactors: React.FC<ExplanatoryFactorsProps> = ({ device }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h4 className="text-lg font-semibold text-gray-900 mb-4">
        Top Contributing Factors - {device.device_id}
      </h4>
      
      <div className="space-y-4">
        {device.explanatory_factors.map((factor, index) => (
          <div key={index} className="border-l-4 border-blue-500 pl-4">
            <div className="flex justify-between items-center mb-2">
              <h5 className="font-medium text-gray-900">{factor.feature}</h5>
              <span className="text-sm font-semibold text-blue-600">
                {Math.round(factor.importance * 100)}% importance
              </span>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Current Value</span>
              <span className="text-sm font-medium text-gray-900">
                {typeof factor.value === 'number' ? factor.value.toFixed(2) : factor.value}
              </span>
            </div>
            
            <p className="text-sm text-gray-700">{factor.impact}</p>
            
            {/* Importance bar */}
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${factor.importance * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const EquipmentHealthScores: React.FC = () => {
  const [healthScores, setHealthScores] = useState<HealthScoreResponse[]>([]);
  const [alerts, setAlerts] = useState<MaintenanceAlertResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<HealthScoreResponse | null>(null);
  const [mlSystemAvailable, setMlSystemAvailable] = useState<boolean>(false);
  const [usingFallbackData, setUsingFallbackData] = useState<boolean>(false);
  const [filters, setFilters] = useState({
    riskLevel: '' as RiskLevel | '',
    minHealthScore: '',
    maxHealthScore: '',
  });

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Primary: Load health scores from real telemetry data
      console.log('Loading health scores from telemetry data...');
      const realHealthScores = await generateHealthScoresFromTelemetry();
      console.log('Health scores loaded:', realHealthScores.length, 'devices');
      const realAlerts = generateAlertsFromHealthScores(realHealthScores);
      console.log('Alerts generated:', realAlerts.length, 'alerts');
      
      // Try to enhance with ML system if available
      try {
        const healthResponse = await mlApiService.getHealthScores();
        const alertsResponse = await mlApiService.getAlerts({ status: 'active' });
        
        // ML system is available - could merge or use ML data instead
        console.log('ML system available - using ML enhanced data');
        setHealthScores(healthResponse.health_scores);
        setAlerts(alertsResponse.alerts);
        setMlSystemAvailable(true);
        setUsingFallbackData(false);
        
        // Select first device by default
        if (healthResponse.health_scores.length > 0 && !selectedDevice) {
          setSelectedDevice(healthResponse.health_scores[0]);
        }
        
      } catch (mlError) {
        console.log('ML system unavailable, using telemetry analysis as primary data source');
        
        // Use real telemetry analysis as primary data source
        setHealthScores(realHealthScores);
        setAlerts(realAlerts);
        setMlSystemAvailable(false);
        setUsingFallbackData(true);
        
        // Select first device by default
        if (realHealthScores.length > 0 && !selectedDevice) {
          setSelectedDevice(realHealthScores[0]);
        }
      }
      
    } catch (err) {
      console.error('Failed to load health data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load health scores');
      setMlSystemAvailable(false);
      setUsingFallbackData(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter health scores based on current filters
  const filteredHealthScores = useMemo(() => {
    return healthScores.filter(device => {
      if (filters.riskLevel && device.risk_level !== filters.riskLevel) return false;
      if (filters.minHealthScore && device.health_score < parseFloat(filters.minHealthScore)) return false;
      if (filters.maxHealthScore && device.health_score > parseFloat(filters.maxHealthScore)) return false;
      return true;
    });
  }, [healthScores, filters]);

  const handleDeviceSelect = (device: HealthScoreResponse) => {
    setSelectedDevice(device);
  };

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value,
    }));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading equipment health data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-red-200">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Health Data</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={loadData}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Equipment Health Scores</h2>
          <p className="text-gray-600">AI-powered health monitoring and predictive maintenance insights</p>
          {/* Data source indicator */}
          <div className="flex items-center mt-2">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium ${
              usingFallbackData 
                ? 'bg-blue-100 text-blue-800' 
                : mlSystemAvailable 
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${
                usingFallbackData 
                  ? 'bg-blue-500' 
                  : mlSystemAvailable 
                    ? 'bg-green-500'
                    : 'bg-red-500'
              }`}></div>
              <span>
                {usingFallbackData 
                  ? 'Real Telemetry Analysis' 
                  : mlSystemAvailable 
                    ? 'ML Enhanced Analysis'
                    : 'System Offline'
                }
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={loadData}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Filters</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Risk Level</label>
            <select
              value={filters.riskLevel}
              onChange={(e) => handleFilterChange('riskLevel', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Levels</option>
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
              <option value="critical">Critical Risk</option>
            </select>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Min Health Score</label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.minHealthScore}
              onChange={(e) => handleFilterChange('minHealthScore', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Max Health Score</label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.maxHealthScore}
              onChange={(e) => handleFilterChange('maxHealthScore', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="100"
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ riskLevel: '', minHealthScore: '', maxHealthScore: '' })}
              className="w-full px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Fleet Health Summary */}
      <FleetHealthSummary healthScores={filteredHealthScores} alerts={alerts} />

      {/* Device Health Gauges */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Device Health Scores ({filteredHealthScores.length} devices)
        </h3>
        
        {filteredHealthScores.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {filteredHealthScores.map((device) => (
              <HealthScoreGauge
                key={device.device_id}
                device={device}
                onClick={() => handleDeviceSelect(device)}
                isSelected={selectedDevice?.device_id === device.device_id}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No devices match the current filters
          </div>
        )}
      </div>

      {/* Selected Device Details */}
      {selectedDevice && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Health Trend Chart */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Health Trend - {selectedDevice.device_id}
            </h3>
            <HealthTrendChart selectedDevice={selectedDevice} />
          </div>

          {/* Explanatory Factors */}
          <ExplanatoryFactors device={selectedDevice} />
        </div>
      )}
    </div>
  );
};

export default EquipmentHealthScores;