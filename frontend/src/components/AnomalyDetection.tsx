import React from 'react';
import type { AnomalyReport } from '../types';

interface AnomalyDetectionProps {
  anomalies: AnomalyReport;
  anomalySummary: {
    short_sessions_count: number;
    missing_telemetry_count: number;
    missing_gps_count: number;
    low_battery_count: number;
  };
}

const AnomalyDetection: React.FC<AnomalyDetectionProps> = ({ anomalies, anomalySummary }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Anomaly Summary Cards */}
      <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Short Sessions</p>
              <p className="text-lg font-semibold text-gray-900">{anomalySummary.short_sessions_count}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Missing Telemetry</p>
              <p className="text-lg font-semibold text-gray-900">{anomalySummary.missing_telemetry_count}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Missing GPS</p>
              <p className="text-lg font-semibold text-gray-900">{anomalySummary.missing_gps_count}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Low Battery</p>
              <p className="text-lg font-semibold text-gray-900">{anomalySummary.low_battery_count}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Short Sessions */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Short Sessions (&lt; 5 minutes)
        </h3>
        {anomalies.short_sessions.length > 0 ? (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {anomalies.short_sessions.map((session, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-red-50 rounded">
                <div>
                  <p className="font-medium text-sm">{session.session_id}</p>
                  <p className="text-xs text-gray-600">{session.device_id}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">
                    {session.duration_min.toFixed(1)} min
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(session.start).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No short sessions detected</p>
        )}
      </div>

      {/* Missing Telemetry */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Missing Telemetry (Sequence Gaps)
        </h3>
        {anomalies.missing_telemetry.length > 0 ? (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {anomalies.missing_telemetry.map((session, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-yellow-50 rounded">
                <div>
                  <p className="font-medium text-sm">{session.session_id}</p>
                  <p className="text-xs text-gray-600">{session.device_id}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-yellow-600">
                    {session.gaps_count} gaps
                  </p>
                  <p className="text-xs text-gray-500">
                    Max: {session.max_gap}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No missing telemetry detected</p>
        )}
      </div>

      {/* Missing GPS */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Missing GPS Data
        </h3>
        {anomalies.missing_gps.length > 0 ? (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {anomalies.missing_gps.slice(0, 5).map((item, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-blue-50 rounded">
                <div>
                  <p className="font-medium text-sm">{item.session_id}</p>
                  <p className="text-xs text-gray-600">{item.device_id}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-blue-600">
                    Seq: {item.seq}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {anomalies.missing_gps.length > 5 && (
              <p className="text-xs text-gray-500 text-center">
                ... and {anomalies.missing_gps.length - 5} more
              </p>
            )}
          </div>
        ) : (
          <p className="text-gray-500">No missing GPS data detected</p>
        )}
      </div>

      {/* Low Battery */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Low Battery Alerts (&lt; 20%)
        </h3>
        {anomalies.low_battery.length > 0 ? (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {anomalies.low_battery.slice(0, 5).map((item, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-orange-50 rounded">
                <div>
                  <p className="font-medium text-sm">{item.session_id}</p>
                  <p className="text-xs text-gray-600">{item.device_id}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-orange-600">
                    {item.battery_level}%
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {anomalies.low_battery.length > 5 && (
              <p className="text-xs text-gray-500 text-center">
                ... and {anomalies.low_battery.length - 5} more
              </p>
            )}
          </div>
        ) : (
          <p className="text-gray-500">No low battery alerts</p>
        )}
      </div>
    </div>
  );
};

export default AnomalyDetection;