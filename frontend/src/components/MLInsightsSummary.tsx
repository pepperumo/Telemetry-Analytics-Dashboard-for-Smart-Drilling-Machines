import React, { useState, useEffect } from 'react';
import { mlApiService } from '../services/mlApi';
import type { HealthScoreResponse, MaintenanceAlertResponse } from '../types/ml';

interface MLSummaryMetrics {
  overall_health_score: number;
  devices_at_risk: number;
  active_alerts: number;
  maintenance_efficiency: number;
  cost_savings_potential: number;
  next_critical_action: {
    device_id: string;
    action: string;
    days_remaining: number;
  } | null;
}

interface MLInsightsSummaryProps {
  className?: string;
  onDrillDown?: (section: string) => void;
}

const MLInsightsSummary: React.FC<MLInsightsSummaryProps> = ({ 
  className = '', 
  onDrillDown 
}) => {
  const [metrics, setMetrics] = useState<MLSummaryMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    loadSummaryMetrics();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSummaryMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSummaryMetrics = async () => {
    try {
      setError(null);
      
      // Load health scores and alerts in parallel
      const [healthResponse, alertsResponse] = await Promise.all([
        mlApiService.getHealthScores(),
        mlApiService.getAlerts({ status: 'active', per_page: 100 })
      ]);

      // Calculate summary metrics
      const healthScores = healthResponse.health_scores;
      const alerts = alertsResponse.alerts;

      // Calculate overall health score
      const totalHealthScore = healthScores.reduce((sum, score) => sum + score.health_score, 0);
      const avgHealthScore = healthScores.length > 0 ? totalHealthScore / healthScores.length : 0;

      // Count devices at risk (health score < 70)
      const devicesAtRisk = healthScores.filter(score => score.health_score < 70).length;

      // Calculate maintenance efficiency (based on alert response times and health trends)
      const maintenanceEfficiency = calculateMaintenanceEfficiency(healthScores, alerts);

      // Calculate cost savings potential (based on health improvements possible)
      const costSavings = calculateCostSavings(healthScores);

      // Find next critical action
      const nextCriticalAction = findNextCriticalAction(alerts);

      const summaryMetrics: MLSummaryMetrics = {
        overall_health_score: Math.round(avgHealthScore),
        devices_at_risk: devicesAtRisk,
        active_alerts: alerts.length,
        maintenance_efficiency: maintenanceEfficiency,
        cost_savings_potential: costSavings,
        next_critical_action: nextCriticalAction
      };

      setMetrics(summaryMetrics);
      setLastUpdated(new Date());

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ML summary');
      console.error('Failed to load ML summary metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateMaintenanceEfficiency = (healthScores: HealthScoreResponse[], alerts: MaintenanceAlertResponse[]): number => {
    // Calculate efficiency based on health score distribution and alert severity
    const healthyDevices = healthScores.filter(score => score.health_score >= 80).length;
    const totalDevices = healthScores.length;
    const criticalAlerts = alerts.filter(alert => alert.severity === 'critical').length;
    
    if (totalDevices === 0) return 0;
    
    const healthRatio = healthyDevices / totalDevices;
    const alertPenalty = Math.min(criticalAlerts * 0.1, 0.3); // Max 30% penalty
    
    return Math.round(Math.max(0, (healthRatio - alertPenalty)) * 100);
  };

  const calculateCostSavings = (healthScores: HealthScoreResponse[]): number => {
    // Estimate cost savings based on health improvements possible
    const improvementPotential = healthScores.reduce((sum, score) => {
      const improvement = Math.max(0, 85 - score.health_score); // Target 85% health
      return sum + improvement;
    }, 0);
    
    // Rough estimate: 1% health improvement = $100 annual savings per device
    return Math.round(improvementPotential * 100);
  };

  const findNextCriticalAction = (alerts: MaintenanceAlertResponse[]) => {
    // Find the most urgent critical or high severity alert
    const urgentAlerts = alerts
      .filter(alert => alert.severity === 'critical' || alert.severity === 'high')
      .sort((a, b) => {
        // Sort by predicted failure time
        if (a.predicted_failure_time && b.predicted_failure_time) {
          return new Date(a.predicted_failure_time).getTime() - new Date(b.predicted_failure_time).getTime();
        }
        if (a.predicted_failure_time) return -1;
        if (b.predicted_failure_time) return 1;
        return 0;
      });

    if (urgentAlerts.length === 0) return null;

    const urgentAlert = urgentAlerts[0];
    const daysRemaining = urgentAlert.predicted_failure_time 
      ? Math.ceil((new Date(urgentAlert.predicted_failure_time).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
      : 7; // Default to 7 days if no prediction

    return {
      device_id: urgentAlert.device_id,
      action: urgentAlert.title,
      days_remaining: Math.max(0, daysRemaining)
    };
  };

  const getHealthScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getHealthScoreBg = (score: number): string => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    if (score >= 40) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 ML System Overview
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="p-4 bg-gray-100 rounded-lg animate-pulse">
              <div className="h-4 bg-gray-300 rounded mb-2"></div>
              <div className="h-8 bg-gray-300 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 ML System Overview
        </h3>
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️ Failed to load ML insights</div>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadSummaryMetrics}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 ML System Overview
        </h3>
        <p className="text-gray-500 text-center py-8">No ML data available</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          🤖 ML System Overview
        </h3>
        <div className="flex items-center space-x-3">
          <span className="text-xs text-gray-500">
            Updated: {lastUpdated.toLocaleTimeString()}
          </span>
          <button
            onClick={loadSummaryMetrics}
            className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
          >
            🔄
          </button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        {/* Overall Health Score */}
        <div 
          className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${getHealthScoreBg(metrics.overall_health_score)}`}
          onClick={() => onDrillDown && onDrillDown('health-scores')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Overall Health</div>
          <div className={`text-2xl font-bold ${getHealthScoreColor(metrics.overall_health_score)}`}>
            {metrics.overall_health_score}%
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {metrics.overall_health_score >= 80 ? 'Excellent' :
             metrics.overall_health_score >= 60 ? 'Good' :
             metrics.overall_health_score >= 40 ? 'Fair' : 'Poor'}
          </div>
        </div>

        {/* Devices at Risk */}
        <div 
          className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${
            metrics.devices_at_risk === 0 ? 'bg-green-50 border-green-200' :
            metrics.devices_at_risk <= 2 ? 'bg-yellow-50 border-yellow-200' :
            'bg-red-50 border-red-200'
          }`}
          onClick={() => onDrillDown && onDrillDown('health-scores')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Devices at Risk</div>
          <div className={`text-2xl font-bold ${
            metrics.devices_at_risk === 0 ? 'text-green-600' :
            metrics.devices_at_risk <= 2 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {metrics.devices_at_risk}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Health &lt; 70%
          </div>
        </div>

        {/* Active Alerts */}
        <div 
          className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${
            metrics.active_alerts === 0 ? 'bg-green-50 border-green-200' :
            metrics.active_alerts <= 3 ? 'bg-yellow-50 border-yellow-200' :
            'bg-red-50 border-red-200'
          }`}
          onClick={() => onDrillDown && onDrillDown('maintenance')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Active Alerts</div>
          <div className={`text-2xl font-bold ${
            metrics.active_alerts === 0 ? 'text-green-600' :
            metrics.active_alerts <= 3 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {metrics.active_alerts}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Require attention
          </div>
        </div>

        {/* Maintenance Efficiency */}
        <div 
          className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${
            metrics.maintenance_efficiency >= 80 ? 'bg-green-50 border-green-200' :
            metrics.maintenance_efficiency >= 60 ? 'bg-yellow-50 border-yellow-200' :
            'bg-orange-50 border-orange-200'
          }`}
          onClick={() => onDrillDown && onDrillDown('maintenance')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Maintenance Efficiency</div>
          <div className={`text-2xl font-bold ${
            metrics.maintenance_efficiency >= 80 ? 'text-green-600' :
            metrics.maintenance_efficiency >= 60 ? 'text-yellow-600' :
            'text-orange-600'
          }`}>
            {metrics.maintenance_efficiency}%
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Proactive ratio
          </div>
        </div>

        {/* Cost Savings Potential */}
        <div 
          className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200 cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => onDrillDown && onDrillDown('patterns')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Cost Savings</div>
          <div className="text-2xl font-bold text-blue-600">
            ${metrics.cost_savings_potential.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Annual potential
          </div>
        </div>

        {/* Next Critical Action */}
        <div 
          className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md transition-shadow ${
            !metrics.next_critical_action ? 'bg-green-50 border-green-200' :
            metrics.next_critical_action.days_remaining <= 1 ? 'bg-red-50 border-red-200' :
            metrics.next_critical_action.days_remaining <= 3 ? 'bg-orange-50 border-orange-200' :
            'bg-yellow-50 border-yellow-200'
          }`}
          onClick={() => onDrillDown && onDrillDown('maintenance')}
        >
          <div className="text-sm font-medium text-gray-700 mb-1">Next Critical Action</div>
          {metrics.next_critical_action ? (
            <>
              <div className={`text-lg font-bold ${
                metrics.next_critical_action.days_remaining <= 1 ? 'text-red-600' :
                metrics.next_critical_action.days_remaining <= 3 ? 'text-orange-600' :
                'text-yellow-600'
              }`}>
                {metrics.next_critical_action.days_remaining === 0 ? 'Today' :
                 metrics.next_critical_action.days_remaining === 1 ? 'Tomorrow' :
                 `${metrics.next_critical_action.days_remaining} days`}
              </div>
              <div className="text-xs text-gray-600 mt-1" title={metrics.next_critical_action.action}>
                {metrics.next_critical_action.device_id}
              </div>
            </>
          ) : (
            <>
              <div className="text-lg font-bold text-green-600">All Clear</div>
              <div className="text-xs text-gray-600 mt-1">No urgent actions</div>
            </>
          )}
        </div>
      </div>

      {/* Next Critical Action Details */}
      {metrics.next_critical_action && (
        <div className={`p-4 rounded-lg border-l-4 ${
          metrics.next_critical_action.days_remaining <= 1 ? 'bg-red-50 border-red-400' :
          metrics.next_critical_action.days_remaining <= 3 ? 'bg-orange-50 border-orange-400' :
          'bg-yellow-50 border-yellow-400'
        }`}>
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-gray-900 mb-1">
                🚨 Priority Action Required
              </h4>
              <p className="text-sm text-gray-700 mb-2">
                <strong>{metrics.next_critical_action.device_id}:</strong> {metrics.next_critical_action.action}
              </p>
              <p className="text-xs text-gray-600">
                {metrics.next_critical_action.days_remaining === 0 ? 
                  'Action required today to prevent equipment failure' :
                  `${metrics.next_critical_action.days_remaining} days remaining before predicted failure`
                }
              </p>
            </div>
            <div className={`px-3 py-1 rounded text-sm font-medium ${
              metrics.next_critical_action.days_remaining <= 1 ? 'bg-red-100 text-red-800' :
              metrics.next_critical_action.days_remaining <= 3 ? 'bg-orange-100 text-orange-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {metrics.next_critical_action.days_remaining <= 1 ? 'URGENT' :
               metrics.next_critical_action.days_remaining <= 3 ? 'HIGH' : 'MEDIUM'}
            </div>
          </div>
        </div>
      )}

      {/* System Status Indicator */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              metrics.overall_health_score >= 80 && metrics.active_alerts === 0 ? 'bg-green-400' :
              metrics.overall_health_score >= 60 && metrics.active_alerts <= 3 ? 'bg-yellow-400' :
              'bg-red-400'
            }`}></div>
            <span className="text-gray-600">
              ML System Status: {
                metrics.overall_health_score >= 80 && metrics.active_alerts === 0 ? 'Optimal' :
                metrics.overall_health_score >= 60 && metrics.active_alerts <= 3 ? 'Monitoring' :
                'Attention Required'
              }
            </span>
          </div>
          <span className="text-gray-500">
            Auto-refresh: 30s
          </span>
        </div>
      </div>
    </div>
  );
};

export default MLInsightsSummary;