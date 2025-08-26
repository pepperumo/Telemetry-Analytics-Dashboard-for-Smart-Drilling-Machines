import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { SessionLocation } from '../types';

interface SessionsMapProps {
  locations: SessionLocation[];
}

const SessionsMap: React.FC<SessionsMapProps> = ({ locations }) => {
  // Berlin center coordinates
  const berlinCenter: [number, number] = [52.520008, 13.404954];
  
  if (locations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Session Locations
        </h3>
        <div className="h-96 flex items-center justify-center bg-gray-100 rounded">
          <p className="text-gray-500">No location data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Session Locations (Berlin Area)
      </h3>
      <div className="h-96 rounded overflow-hidden">
        <MapContainer
          center={berlinCenter}
          zoom={10}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {locations.map((location, index) => (
            <CircleMarker
              key={`${location.session_id}-${index}`}
              center={[location.lat, location.lon]}
              radius={8}
              fillColor={location.tagged ? '#10b981' : '#3b82f6'}
              color={location.tagged ? '#065f46' : '#1e40af'}
              weight={2}
              opacity={0.8}
              fillOpacity={0.6}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-semibold">{location.session_id}</div>
                  <div>Device: {location.device_id}</div>
                  <div>Duration: {location.duration_min.toFixed(1)} min</div>
                  <div>Tagged: {location.tagged ? 'Yes' : 'No'}</div>
                  <div>Start: {new Date(location.start).toLocaleString()}</div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded-full bg-emerald-500 border-2 border-emerald-800"></div>
          <span className="text-sm text-gray-600">Tagged Sessions</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-blue-800"></div>
          <span className="text-sm text-gray-600">Untagged Sessions</span>
        </div>
        <div className="text-sm text-gray-500">
          Total: {locations.length} sessions
        </div>
      </div>
    </div>
  );
};

export default SessionsMap;