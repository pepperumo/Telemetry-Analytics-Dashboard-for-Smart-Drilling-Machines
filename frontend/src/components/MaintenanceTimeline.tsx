import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';
import { mlApiService } from '../services/mlApi';
import type {
  MaintenanceAlertResponse,
  HealthScoreResponse,
  AlertSeverity,
  AlertType,
  AlertStatus
} from '../types/ml';

// Enhanced data interfaces for timeline
interface MaintenanceEvent {
  id: string;
  device_id: string;
  title: string;
  description: string;
  severity: AlertSeverity;
  alert_type: AlertType;
  status: AlertStatus;
  predicted_date: Date;
  confidence_score: number;
  recommended_actions: string[];
  affected_systems: string[];
  created_at: Date;
  acknowledged_at?: Date;
  health_score?: number;
  timeline_position: number; // Days from now
}

interface TimelineData {
  date: string;
  day_offset: number;
  critical_events: number;
  high_events: number;
  medium_events: number;
  low_events: number;
  total_events: number;
  events: MaintenanceEvent[];
}

interface MaintenanceTimelineProps {
  className?: string;
}

const MaintenanceTimeline: React.FC<MaintenanceTimelineProps> = ({ className = '' }) => {
  // State management
  const [alerts, setAlerts] = useState<MaintenanceAlertResponse[]>([]);
  const [healthScores, setHealthScores] = useState<HealthScoreResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(new Set());
  const [selectedSeverities, setSelectedSeverities] = useState<Set<AlertSeverity>>(
    new Set(['critical', 'high', 'medium', 'low'])
  );
  const [selectedTypes, setSelectedTypes] = useState<Set<AlertType>>(new Set());
  const [timeRange, setTimeRange] = useState<number>(30); // Days ahead
  const [showAcknowledged, setShowAcknowledged] = useState<boolean>(false);
  
  // Selection state for details panel
  const [selectedEvent, setSelectedEvent] = useState<MaintenanceEvent | null>(null);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load alerts and health scores in parallel
      const [alertsResponse, healthResponse] = await Promise.all([
        mlApiService.getAlerts({ 
          status: showAcknowledged ? undefined : 'active',
          per_page: 100 
        }),
        mlApiService.getHealthScores()
      ]);

      setAlerts(alertsResponse.alerts);
      setHealthScores(healthResponse.health_scores);
      
      // Auto-populate device and type filters
      const devices = new Set(alertsResponse.alerts.map(alert => alert.device_id));
      const types = new Set(alertsResponse.alerts.map(alert => alert.alert_type));
      
      setSelectedDevices(devices);
      setSelectedTypes(types);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load maintenance data');
      console.error('Failed to load maintenance data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Process alerts into timeline events
  const maintenanceEvents = useMemo(() => {
    const now = new Date();
    const healthScoreMap = new Map(
      healthScores.map(score => [score.device_id, score.health_score])
    );

    return alerts
      .filter(alert => {
        // Apply filters
        if (!selectedDevices.has(alert.device_id)) return false;
        if (!selectedSeverities.has(alert.severity)) return false;
        if (!selectedTypes.has(alert.alert_type)) return false;
        if (!showAcknowledged && alert.status === 'acknowledged') return false;
        
        return true;
      })
      .map(alert => {
        // Calculate predicted failure time (fallback to 7-30 days based on severity)
        let predictedDate: Date;
        if (alert.predicted_failure_time) {
          predictedDate = new Date(alert.predicted_failure_time);
        } else {
          // Fallback prediction based on severity
          const daysAhead = {
            critical: 3,
            high: 7,
            medium: 14,
            low: 30
          }[alert.severity];
          predictedDate = new Date(now.getTime() + daysAhead * 24 * 60 * 60 * 1000);
        }

        const timelinePosition = Math.ceil(
          (predictedDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000)
        );

        const event: MaintenanceEvent = {
          id: alert.id,
          device_id: alert.device_id,
          title: alert.title,
          description: alert.description,
          severity: alert.severity,
          alert_type: alert.alert_type,
          status: alert.status,
          predicted_date: predictedDate,
          confidence_score: alert.confidence_score,
          recommended_actions: alert.recommended_actions,
          affected_systems: alert.affected_systems,
          created_at: new Date(alert.created_at),
          acknowledged_at: alert.acknowledged_at ? new Date(alert.acknowledged_at) : undefined,
          health_score: healthScoreMap.get(alert.device_id),
          timeline_position: timelinePosition
        };

        return event;
      })
      .filter(event => event.timeline_position <= timeRange && event.timeline_position >= 0)
      .sort((a, b) => a.timeline_position - b.timeline_position);
  }, [alerts, healthScores, selectedDevices, selectedSeverities, selectedTypes, timeRange, showAcknowledged]);

  // Generate timeline chart data
  const timelineData = useMemo(() => {
    const dataMap = new Map<number, TimelineData>();
    const now = new Date();

    // Initialize all days in range
    for (let i = 0; i <= timeRange; i++) {
      const date = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
      dataMap.set(i, {
        date: date.toLocaleDateString(),
        day_offset: i,
        critical_events: 0,
        high_events: 0,
        medium_events: 0,
        low_events: 0,
        total_events: 0,
        events: []
      });
    }

    // Populate with events
    maintenanceEvents.forEach(event => {
      const dayData = dataMap.get(event.timeline_position);
      if (dayData) {
        dayData.events.push(event);
        dayData.total_events++;
        dayData[`${event.severity}_events`]++;
      }
    });

    return Array.from(dataMap.values());
  }, [maintenanceEvents, timeRange]);

  // Handle alert acknowledgment
  const handleAcknowledgeAlert = async (event: MaintenanceEvent) => {
    try {
      const success = await mlApiService.quickAcknowledgeAlert(
        event.id, 
        'Dashboard User'
      );
      
      if (success) {
        // Reload data to update status
        await loadData();
        setSelectedEvent(null);
      }
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  // Color schemes
  const severityColors = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e'
  };

  const typeIcons = {
    performance_degradation: '📉',
    equipment_failure_risk: '⚠️',
    battery_maintenance: '🔋',
    mechanical_wear: '⚙️',
    thermal_stress: '🌡️',
    electrical_anomaly: '⚡'
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Predictive Maintenance Timeline
        </h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Loading maintenance predictions...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Predictive Maintenance Timeline
        </h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center text-red-600">
            <p className="text-lg font-medium mb-2">⚠️ Error Loading Data</p>
            <p className="text-sm">{error}</p>
            <button
              onClick={loadData}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Predictive Maintenance Timeline
        </h3>
        <button
          onClick={loadData}
          className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        {/* Device Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Equipment Filter:
          </label>
          <div className="flex flex-wrap gap-2">
            {Array.from(new Set(alerts.map(alert => alert.device_id))).map(device => (
              <label key={device} className="flex items-center space-x-1 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedDevices.has(device)}
                  onChange={(e) => {
                    const newSelected = new Set(selectedDevices);
                    if (e.target.checked) {
                      newSelected.add(device);
                    } else {
                      newSelected.delete(device);
                    }
                    setSelectedDevices(newSelected);
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">{device}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Severity Filter:
          </label>
          <div className="flex flex-wrap gap-2">
            {(['critical', 'high', 'medium', 'low'] as AlertSeverity[]).map(severity => (
              <label key={severity} className="flex items-center space-x-1 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSeverities.has(severity)}
                  onChange={(e) => {
                    const newSelected = new Set(selectedSeverities);
                    if (e.target.checked) {
                      newSelected.add(severity);
                    } else {
                      newSelected.delete(severity);
                    }
                    setSelectedSeverities(newSelected);
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span 
                  className="text-sm font-medium px-2 py-1 rounded"
                  style={{ 
                    backgroundColor: severityColors[severity] + '20',
                    color: severityColors[severity]
                  }}
                >
                  {severity.toUpperCase()}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Time Range and Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Range:
          </label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Next 7 Days</option>
            <option value={14}>Next 2 Weeks</option>
            <option value={30}>Next 30 Days</option>
            <option value={60}>Next 60 Days</option>
            <option value={90}>Next 90 Days</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Options:
          </label>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showAcknowledged}
              onChange={(e) => setShowAcknowledged(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Include Acknowledged Alerts</span>
          </label>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {Object.entries(severityColors).map(([severity, color]) => {
          const count = maintenanceEvents.filter(e => e.severity === severity).length;
          return (
            <div key={severity} className="p-3 rounded-lg border-l-4" style={{ borderColor: color }}>
              <div className="text-sm font-medium text-gray-600">{severity.toUpperCase()}</div>
              <div className="text-xl font-bold" style={{ color }}>{count}</div>
            </div>
          );
        })}
      </div>

      {/* Timeline Chart */}
      <div className="h-64 mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Maintenance Events Distribution (Next {timeRange} Days)
        </h4>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 10 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis label={{ value: 'Events', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              formatter={(value: number, name: string) => [
                value,
                name.replace('_events', '').toUpperCase()
              ]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Bar dataKey="critical_events" stackId="a" fill={severityColors.critical} />
            <Bar dataKey="high_events" stackId="a" fill={severityColors.high} />
            <Bar dataKey="medium_events" stackId="a" fill={severityColors.medium} />
            <Bar dataKey="low_events" stackId="a" fill={severityColors.low} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Events List */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700">
          Upcoming Maintenance Events ({maintenanceEvents.length})
        </h4>
        
        {maintenanceEvents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg mb-2">🎉 No maintenance events scheduled</p>
            <p className="text-sm">All equipment is operating within normal parameters.</p>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto space-y-2">
            {maintenanceEvents.map(event => (
              <div
                key={event.id}
                className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border-l-4"
                style={{ borderLeftColor: severityColors[event.severity] }}
                onClick={() => setSelectedEvent(event)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{typeIcons[event.alert_type]}</span>
                      <span className="font-medium text-gray-900">{event.title}</span>
                      <span
                        className="px-2 py-1 rounded text-xs font-medium"
                        style={{
                          backgroundColor: severityColors[event.severity] + '20',
                          color: severityColors[event.severity]
                        }}
                      >
                        {event.severity.toUpperCase()}
                      </span>
                      {event.status === 'acknowledged' && (
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                          ✓ ACKNOWLEDGED
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600">
                      <div>
                        <strong>Device:</strong> {event.device_id}
                      </div>
                      <div>
                        <strong>Predicted:</strong> {event.predicted_date.toLocaleDateString()}
                        {event.timeline_position <= 3 && (
                          <span className="ml-1 text-red-600 font-medium">
                            ({event.timeline_position === 0 ? 'TODAY' : `${event.timeline_position} days`})
                          </span>
                        )}
                      </div>
                      <div>
                        <strong>Confidence:</strong> {(event.confidence_score * 100).toFixed(0)}%
                        {event.health_score && (
                          <span className="ml-2">
                            | <strong>Health:</strong> {event.health_score.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {event.status === 'active' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAcknowledgeAlert(event);
                      }}
                      className="ml-4 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Maintenance Event Details
              </h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong>Device:</strong> {selectedEvent.device_id}
                </div>
                <div>
                  <strong>Alert Type:</strong> {selectedEvent.alert_type.replace('_', ' ')}
                </div>
                <div>
                  <strong>Severity:</strong>
                  <span
                    className="ml-2 px-2 py-1 rounded text-xs font-medium"
                    style={{
                      backgroundColor: severityColors[selectedEvent.severity] + '20',
                      color: severityColors[selectedEvent.severity]
                    }}
                  >
                    {selectedEvent.severity.toUpperCase()}
                  </span>
                </div>
                <div>
                  <strong>Predicted Date:</strong> {selectedEvent.predicted_date.toLocaleString()}
                </div>
                <div>
                  <strong>Confidence:</strong> {(selectedEvent.confidence_score * 100).toFixed(0)}%
                </div>
                {selectedEvent.health_score && (
                  <div>
                    <strong>Current Health Score:</strong> {selectedEvent.health_score.toFixed(1)}%
                  </div>
                )}
              </div>

              <div>
                <strong>Description:</strong>
                <p className="text-gray-700 mt-1">{selectedEvent.description}</p>
              </div>

              {selectedEvent.recommended_actions.length > 0 && (
                <div>
                  <strong>Recommended Actions:</strong>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    {selectedEvent.recommended_actions.map((action, index) => (
                      <li key={index} className="text-gray-700">{action}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedEvent.affected_systems.length > 0 && (
                <div>
                  <strong>Affected Systems:</strong>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedEvent.affected_systems.map((system, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-4 border-t flex justify-end space-x-3">
                {selectedEvent.status === 'active' && (
                  <button
                    onClick={() => handleAcknowledgeAlert(selectedEvent)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    Acknowledge Alert
                  </button>
                )}
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaintenanceTimeline;