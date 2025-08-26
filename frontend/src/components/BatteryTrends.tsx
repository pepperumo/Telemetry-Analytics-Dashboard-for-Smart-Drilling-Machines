import React, { useState, useMemo, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import type { BatteryTrend, SessionData } from '../types';
import { apiService } from '../services/api';

interface BatteryTrendsProps {
  trends: BatteryTrend[];
  dateRange?: { startDate: string; endDate: string };
}

const BatteryTrends: React.FC<BatteryTrendsProps> = ({ trends, dateRange }) => {
  // Get unique devices from trends data
  const availableDevices = useMemo(() => {
    const devices = [...new Set(trends.map(trend => trend.device_id))].sort();
    return devices;
  }, [trends]);

  // State for selected devices (all selected by default)
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(
    new Set(availableDevices)
  );

  // State for sessions and session selection
  const [availableSessions, setAvailableSessions] = useState<SessionData[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>('all');
  const [sessionViewMode, setSessionViewMode] = useState<'exact' | 'context'>('exact');
  const [loadingSessions, setLoadingSessions] = useState<boolean>(false);

  // Load sessions when selected devices change
  useEffect(() => {
    const loadSessions = async () => {
      if (selectedDevices.size === 0) {
        setAvailableSessions([]);
        return;
      }

      setLoadingSessions(true);
      try {
        // If single device selected, filter sessions by device
        const deviceId = selectedDevices.size === 1 ? Array.from(selectedDevices)[0] : undefined;
        const response = await apiService.getSessions(deviceId, dateRange);
        setAvailableSessions(response.sessions);
        setSelectedSession('all'); // Reset to "all sessions" when devices change
      } catch (error) {
        console.error('Failed to load sessions:', error);
        setAvailableSessions([]);
      } finally {
        setLoadingSessions(false);
      }
    };

    loadSessions();
  }, [selectedDevices, dateRange]);

  // Filter trends based on selected devices and session
  const filteredTrends = useMemo(() => {
    let filtered = trends.filter(trend => selectedDevices.has(trend.device_id));
    
    // If a specific session is selected, filter by session time range
    if (selectedSession !== 'all') {
      const session = availableSessions.find(s => s.session_id === selectedSession);
      if (session) {
        const sessionStart = new Date(session.start).getTime();
        const sessionEnd = new Date(session.end).getTime();
        
        if (sessionViewMode === 'exact') {
          // Show only the exact session data
          filtered = filtered.filter(trend => {
            const trendTime = new Date(trend.timestamp).getTime();
            return trendTime >= sessionStart && trendTime <= sessionEnd;
          });
        } else {
          // Show session + context (24 hours before and after)
          const contextMs = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
          const contextStart = sessionStart - contextMs;
          const contextEnd = sessionEnd + contextMs;
          
          filtered = filtered.filter(trend => {
            const trendTime = new Date(trend.timestamp).getTime();
            return trendTime >= contextStart && trendTime <= contextEnd;
          });
        }
      }
    }
    
    return filtered;
  }, [trends, selectedDevices, selectedSession, sessionViewMode, availableSessions]);

  // Get sessions that overlap with the current context view
  const contextSessions = useMemo(() => {
    if (selectedSession === 'all' || sessionViewMode === 'exact') return [];
    
    const mainSession = availableSessions.find(s => s.session_id === selectedSession);
    if (!mainSession) return [];
    
    const contextMs = 24 * 60 * 60 * 1000; // 24 hours
    const contextStart = new Date(mainSession.start).getTime() - contextMs;
    const contextEnd = new Date(mainSession.end).getTime() + contextMs;
    
    return availableSessions.filter(session => {
      const sessionStart = new Date(session.start).getTime();
      const sessionEnd = new Date(session.end).getTime();
      
      // Include sessions that overlap with the context period
      return (sessionStart >= contextStart && sessionStart <= contextEnd) ||
             (sessionEnd >= contextStart && sessionEnd <= contextEnd) ||
             (sessionStart <= contextStart && sessionEnd >= contextEnd);
    });
  }, [availableSessions, selectedSession, sessionViewMode]);
  const chartData = useMemo(() => {
    // Group trends by device
    const deviceTrends: { [deviceId: string]: BatteryTrend[] } = {};
    
    filteredTrends.forEach(trend => {
      if (!deviceTrends[trend.device_id]) {
        deviceTrends[trend.device_id] = [];
      }
      deviceTrends[trend.device_id].push(trend);
    });

    // Process each device separately and combine into unified timeline
    const allDataPoints: any[] = [];
    
    Object.entries(deviceTrends).forEach(([deviceId, trends]) => {
      // Sort trends for this device by timestamp
      const sortedTrends = trends.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      // Use all data points - no sampling
      sortedTrends.forEach(trend => {
        const timestamp = new Date(trend.timestamp);
        
        allDataPoints.push({
          timestamp: timestamp.getTime(),
          displayTime: timestamp.toLocaleString(),
          deviceId: deviceId,
          battery_level: trend.battery_level,
          [deviceId]: trend.battery_level
        });
      });
    });

    // Group by precise timestamp to preserve all data points
    const timePointMap = new Map<number, any>();
    
    allDataPoints.forEach(point => {
      const timeKey = point.timestamp; // Use precise millisecond timestamp
      
      if (!timePointMap.has(timeKey)) {
        timePointMap.set(timeKey, {
          timestamp: point.timestamp,
          displayTime: point.displayTime
        });
      }
      
      const timePoint = timePointMap.get(timeKey);
      timePoint[point.deviceId] = point.battery_level;
    });

    // Convert to array and sort by timestamp
    return Array.from(timePointMap.values()).sort((a, b) => a.timestamp - b.timestamp);
  }, [filteredTrends]);

  // Get devices that have data in the chart
  const devices = useMemo(() => {
    const deviceSet = new Set<string>();
    chartData.forEach(dataPoint => {
      availableDevices.forEach(deviceId => {
        if (dataPoint[deviceId] !== undefined) {
          deviceSet.add(deviceId);
        }
      });
    });
    return Array.from(deviceSet);
  }, [chartData, availableDevices]);
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  // Handle device selection
  const handleDeviceToggle = (deviceId: string) => {
    const newSelected = new Set(selectedDevices);
    if (newSelected.has(deviceId)) {
      newSelected.delete(deviceId);
    } else {
      newSelected.add(deviceId);
    }
    setSelectedDevices(newSelected);
  };

  const handleSelectAll = () => {
    setSelectedDevices(new Set(availableDevices));
  };

  const handleSelectNone = () => {
    setSelectedDevices(new Set());
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Battery Level Trends
      </h3>

      {/* Controls */}
      <div className="mb-6">
        {/* Device Selection */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-700">Select Devices:</h4>
            <div className="space-x-2">
              <button
                onClick={handleSelectAll}
                className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
              >
                All
              </button>
              <button
                onClick={handleSelectNone}
                className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                None
              </button>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {availableDevices.map((deviceId, index) => (
              <label
                key={deviceId}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedDevices.has(deviceId)}
                  onChange={() => handleDeviceToggle(deviceId)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span
                  className="flex items-center space-x-1 text-sm font-medium"
                  style={{ color: colors[index % colors.length] }}
                >
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: colors[index % colors.length] }}
                  ></span>
                  <span>{deviceId}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Session Selection */}
        <div className="p-4 bg-gray-50 rounded-lg mt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-700">Select Session:</h4>
            {loadingSessions && (
              <span className="text-xs text-gray-500">Loading sessions...</span>
            )}
          </div>
          
          <select
            value={selectedSession}
            onChange={(e) => setSelectedSession(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={loadingSessions || availableSessions.length === 0}
          >
            <option value="all">All Sessions (Full Timeline)</option>
            {availableSessions.map((session) => (
              <option key={session.session_id} value={session.session_id}>
                {session.device_id} - {new Date(session.start).toLocaleDateString()} {new Date(session.start).toLocaleTimeString()} 
                ({session.duration_min} min) {session.tagged ? '🏷️' : ''}
              </option>
            ))}
          </select>
          
          {/* Session View Mode */}
          {selectedSession !== 'all' && (
            <div className="mt-3">
              <label className="text-sm font-medium text-gray-700 mb-2 block">View Mode:</label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="exact"
                    checked={sessionViewMode === 'exact'}
                    onChange={(e) => setSessionViewMode(e.target.value as 'exact' | 'context')}
                    className="mr-2"
                  />
                  <span className="text-sm">Session Only (Flat Battery)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="context"
                    checked={sessionViewMode === 'context'}
                    onChange={(e) => setSessionViewMode(e.target.value as 'exact' | 'context')}
                    className="mr-2"
                  />
                  <span className="text-sm">Session + Context (48-Hour View)</span>
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {sessionViewMode === 'exact' 
                  ? 'Shows only the drilling session data where battery stays flat'
                  : 'Shows 24 hours before/after session to see full charging cycles and other sessions'
                }
              </p>
            </div>
          )}
          
          {availableSessions.length === 0 && !loadingSessions && selectedDevices.size > 0 && (
            <p className="text-xs text-gray-500 mt-2">No sessions found for selected devices</p>
          )}
        </div>
      </div>
      
      {chartData.length > 0 ? (
        <div className="h-80 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                type="number"
                scale="time"
                domain={['dataMin', 'dataMax']}
                tickFormatter={(timestamp) => {
                  const date = new Date(timestamp);
                  // Show more detailed time format for session view
                  return selectedSession !== 'all' 
                    ? date.toLocaleTimeString() 
                    : date.toLocaleDateString();
                }}
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                label={{ value: 'Battery Level (%)', angle: -90, position: 'insideLeft' }}
                domain={
                  selectedSession !== 'all' && sessionViewMode === 'exact'
                    ? ['dataMin - 1', 'dataMax + 1'] // Tight zoom for session-only view
                    : selectedSession !== 'all' 
                    ? ['dataMin - 5', 'dataMax + 5'] // Moderate zoom for context view
                    : [0, 100] // Full range for timeline view
                }
              />
              <Tooltip 
                formatter={(value: number, name: string) => [`${value}%`, `Device ${name}`]}
                labelFormatter={(timestamp: number) => new Date(timestamp).toLocaleString()}
              />
              <Legend />
              
              {/* Session boundary lines for context view */}
              {selectedSession !== 'all' && sessionViewMode === 'context' && 
                contextSessions.map((session, index) => {
                  const isMainSession = session.session_id === selectedSession;
                  const sessionStart = new Date(session.start).getTime();
                  const sessionEnd = new Date(session.end).getTime();
                  
                  return [
                    <ReferenceLine 
                      key={`${session.session_id}-start`}
                      x={sessionStart} 
                      stroke={isMainSession ? "#22c55e" : "#94a3b8"} 
                      strokeWidth={isMainSession ? 2 : 1}
                      strokeDasharray={isMainSession ? "5 5" : "2 2"} 
                      label={{ 
                        value: isMainSession ? "Main Session Start" : `Session ${index + 1} Start`, 
                        position: "top",
                        style: { fontSize: isMainSession ? 12 : 10, fontWeight: isMainSession ? 'bold' : 'normal' }
                      }}
                    />,
                    <ReferenceLine 
                      key={`${session.session_id}-end`}
                      x={sessionEnd} 
                      stroke={isMainSession ? "#ef4444" : "#94a3b8"} 
                      strokeWidth={isMainSession ? 2 : 1}
                      strokeDasharray={isMainSession ? "5 5" : "2 2"} 
                      label={{ 
                        value: isMainSession ? "Main Session End" : `Session ${index + 1} End`, 
                        position: "bottom",
                        style: { fontSize: isMainSession ? 12 : 10, fontWeight: isMainSession ? 'normal' : 'normal' }
                      }}
                    />
                  ];
                }).flat()
              }
              
              {devices.map((device) => (
                <Line
                  key={device}
                  type={selectedSession !== 'all' ? "linear" : "monotone"}
                  dataKey={device}
                  stroke={colors[availableDevices.indexOf(device) % colors.length]}
                  strokeWidth={2}
                  dot={selectedSession !== 'all' ? { r: 3 } : false}
                  connectNulls={true}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-80 flex items-center justify-center bg-gray-100 rounded">
          <p className="text-gray-500">
            {selectedDevices.size === 0 
              ? "No devices selected. Please select at least one device to view battery trends." 
              : "No battery data available for the selected devices and time period."}
          </p>
        </div>
      )}

      {/* Simple Stats */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm font-medium text-blue-800">Data Points</div>
            <div className="text-lg font-bold text-blue-900">{chartData.length}</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-sm font-medium text-green-800">Selected Devices</div>
            <div className="text-lg font-bold text-green-900">{selectedDevices.size}</div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="text-sm font-medium text-purple-800">View Mode</div>
            <div className="text-lg font-bold text-purple-900">
              {selectedSession === 'all' 
                ? 'Timeline' 
                : sessionViewMode === 'exact' 
                ? 'Session' 
                : 'Session + Context'
              }
            </div>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg">
            <div className="text-sm font-medium text-yellow-800">Battery Range</div>
            <div className="text-lg font-bold text-yellow-900">
              {(() => {
                const allBatteryValues: number[] = [];
                chartData.forEach(dataPoint => {
                  devices.forEach(deviceId => {
                    if (dataPoint[deviceId] !== undefined) {
                      allBatteryValues.push(dataPoint[deviceId]);
                    }
                  });
                });
                if (allBatteryValues.length === 0) return 'No data';
                return `${Math.min(...allBatteryValues).toFixed(0)}% - ${Math.max(...allBatteryValues).toFixed(0)}%`;
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Session Info */}
      {selectedSession !== 'all' && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h4 className="text-sm font-medium text-blue-800 mb-2">
            {sessionViewMode === 'exact' ? 'Session Details' : 'Context View: Sessions in 48-Hour Period'}
          </h4>
          {sessionViewMode === 'exact' ? (
            (() => {
              const session = availableSessions.find(s => s.session_id === selectedSession);
              if (!session) return <p className="text-blue-700">Session not found</p>;
              
              return (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="font-medium text-blue-800">Device:</span>
                    <span className="ml-2 text-blue-700">{session.device_id}</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-800">Duration:</span>
                    <span className="ml-2 text-blue-700">{session.duration_min} minutes</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-800">Tagged:</span>
                    <span className="ml-2 text-blue-700">{session.tagged ? 'Yes 🏷️' : 'No'}</span>
                  </div>
                  <div className="md:col-span-3">
                    <span className="font-medium text-blue-800">Time Range:</span>
                    <span className="ml-2 text-blue-700">
                      {new Date(session.start).toLocaleString()} - {new Date(session.end).toLocaleString()}
                    </span>
                  </div>
                </div>
              );
            })()
          ) : (
            <div className="space-y-3">
              <div className="text-sm text-blue-700 mb-3">
                Showing {contextSessions.length} sessions within 24 hours before and after the main session:
              </div>
              <div className="grid gap-3">
                {contextSessions.map((session, index) => {
                  const isMainSession = session.session_id === selectedSession;
                  return (
                    <div 
                      key={session.session_id}
                      className={`p-3 rounded border-l-4 ${
                        isMainSession 
                          ? 'bg-green-50 border-green-400' 
                          : 'bg-gray-50 border-gray-300'
                      }`}
                    >
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-2 text-sm">
                        <div>
                          <span className="font-medium">
                            {isMainSession ? '🎯 Main Session' : `📍 Session ${index + 1}`}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Device:</span> {session.device_id}
                        </div>
                        <div>
                          <span className="text-gray-600">Duration:</span> {session.duration_min} min
                        </div>
                        <div>
                          {session.tagged ? '🏷️ Tagged' : '📍 Untagged'}
                        </div>
                        <div className="md:col-span-4 text-xs text-gray-600">
                          {new Date(session.start).toLocaleString()} - {new Date(session.end).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BatteryTrends;