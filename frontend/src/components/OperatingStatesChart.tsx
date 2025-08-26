import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { DashboardInsights } from '../types';

interface OperatingStatesChartProps {
  insights: DashboardInsights;
}

const COLORS = {
  'OFF': '#ef4444',      // red
  'STANDBY': '#f59e0b',  // amber
  'SPIN': '#3b82f6',     // blue
  'DRILL': '#10b981'     // emerald
};

const OperatingStatesChart: React.FC<OperatingStatesChartProps> = ({ insights }) => {
  // Calculate total operational time from drilling time and its percentage
  const drillPercentage = insights.operating_states_distribution['DRILL'] || 59.1;
  const totalOperationalTime = insights.total_drilling_time_hours / (drillPercentage / 100);
  
  // Calculate OFF time (idle time between sessions)
  const totalTimespan = insights.total_timespan_hours || 0;
  const operationalTime = insights.total_operational_time_hours || totalOperationalTime;
  const offTime = Math.max(0, totalTimespan - operationalTime);
  
  // Calculate time information for each state
  const pieData = Object.entries(insights.operating_states_distribution).map(([state, percentage]) => {
    const timeHours = (percentage / 100) * totalOperationalTime;
    
    return {
      name: state,
      value: percentage,
      timeHours: timeHours,
      displayName: `${state} (${timeHours.toFixed(1)}h)`
    };
  });

  const renderLabel = (entry: any) => {
    return `${entry.value.toFixed(1)}%`;
  };

  const customTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-medium">{data.name}</p>
          <p className="text-blue-600">{`${data.value.toFixed(1)}%`}</p>
          <p className="text-gray-600">{`${data.timeHours.toFixed(1)} hours`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Pie Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Operating States Distribution
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderLabel}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[entry.name as keyof typeof COLORS] || '#8884d8'} 
                  />
                ))}
              </Pie>
              <Tooltip content={customTooltip} />
              <Legend 
                formatter={(_, entry: any) => (
                  <span style={{ color: entry.color }}>
                    {entry.payload.displayName}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Operating States Legend */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Operating States Interpretation
        </h3>
        <div className="grid grid-cols-1 gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.OFF }}></div>
              <div>
                <p className="font-medium text-gray-900">OFF</p>
                <p className="text-sm text-gray-500">≈0 A - Machine unplugged</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-900">{offTime.toFixed(1)}h</p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.STANDBY }}></div>
              <div>
                <p className="font-medium text-gray-900">STANDBY</p>
                <p className="text-sm text-gray-500">≈0.9 A - Plugged in, switch OFF</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-900">{pieData.find(d => d.name === 'STANDBY')?.timeHours.toFixed(1) || '0.0'}h</p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.SPIN }}></div>
              <div>
                <p className="font-medium text-gray-900">SPIN</p>
                <p className="text-sm text-gray-500">≈3.9 A - Motor ON, no load</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-900">{pieData.find(d => d.name === 'SPIN')?.timeHours.toFixed(1) || '0.0'}h</p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.DRILL }}></div>
              <div>
                <p className="font-medium text-gray-900">DRILL</p>
                <p className="text-sm text-gray-500">&gt;5 A - Drilling under load</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-900">{pieData.find(d => d.name === 'DRILL')?.timeHours.toFixed(1) || '0.0'}h</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OperatingStatesChart;