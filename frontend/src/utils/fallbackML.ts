/**
 * Fallback ML calculations using raw drilling data
 * Used when ML system is unavailable to provide health insights from telemetry data
 */

import type { 
  HealthScoreResponse, 
  RiskLevel, 
  ExplanatoryFactor,
  MaintenanceAlertResponse 
} from '../types/ml';

interface TelemetryData {
  timestamp: string;
  device_id: string;
  seq: number;
  current_amp: number;
  gps_lat: number;
  gps_lon: number;
  battery_level: number;
  ble_id?: string;
}

/**
 * Calculate health score from telemetry patterns
 */
const calculateDeviceHealthFromTelemetry = (deviceData: TelemetryData[]): {
  healthScore: number;
  riskLevel: RiskLevel;
  explanatoryFactors: ExplanatoryFactor[];
} => {
  if (deviceData.length === 0) {
    return {
      healthScore: 50,
      riskLevel: 'medium',
      explanatoryFactors: []
    };
  }

  // Calculate various health indicators
  const currentAmps = deviceData.map(d => d.current_amp).filter(amp => amp > 0);
  const batteryLevels = deviceData.map(d => d.battery_level).filter(level => level > 0);
  const gpsReadings = deviceData.filter(d => d.gps_lat && d.gps_lon);
  
  // Current draw analysis
  const avgCurrent = currentAmps.reduce((sum, amp) => sum + amp, 0) / currentAmps.length || 0;
  const currentVariability = calculateVariability(currentAmps);
  
  // Battery performance analysis
  const avgBattery = batteryLevels.reduce((sum, level) => sum + level, 0) / batteryLevels.length || 0;
  const batteryDrop = Math.max(...batteryLevels, 0) - Math.min(...batteryLevels, 100);
  
  // GPS/positioning reliability
  const gpsReliability = gpsReadings.length / deviceData.length;
  const positionVariability = calculatePositionVariability(gpsReadings);
  
  // Data quality indicators
  const dataCompleteness = deviceData.filter(d => 
    d.current_amp > 0 && d.battery_level > 0 && d.gps_lat && d.gps_lon
  ).length / deviceData.length;
  
  // Calculate health score (0-100)
  let healthScore = 100;
  
  // Current draw health (30% weight)
  const currentHealth = Math.max(0, 100 - (currentVariability * 50) - Math.max(0, (avgCurrent - 5) * 10));
  healthScore -= (100 - currentHealth) * 0.3;
  
  // Battery health (25% weight)
  const batteryHealth = Math.max(0, Math.min(100, avgBattery - (batteryDrop * 2)));
  healthScore -= (100 - batteryHealth) * 0.25;
  
  // GPS reliability (20% weight)
  const gpsHealth = gpsReliability * 100;
  healthScore -= (100 - gpsHealth) * 0.2;
  
  // Data quality (15% weight)
  const dataQualityHealth = dataCompleteness * 100;
  healthScore -= (100 - dataQualityHealth) * 0.15;
  
  // Operational consistency (10% weight)
  const operationalHealth = Math.max(0, 100 - (positionVariability * 100));
  healthScore -= (100 - operationalHealth) * 0.1;
  
  healthScore = Math.max(0, Math.min(100, healthScore));
  
  // Determine risk level
  const riskLevel: RiskLevel = 
    healthScore >= 80 ? 'low' :
    healthScore >= 60 ? 'medium' :
    healthScore >= 40 ? 'high' : 'critical';
  
  // Generate explanatory factors
  const explanatoryFactors: ExplanatoryFactor[] = [
    {
      feature: 'Current Draw Stability',
      value: currentVariability,
      importance: 0.3,
      impact: currentVariability > 0.5 ? 
        'High current variability indicates potential electrical issues' :
        'Stable current draw suggests healthy electrical system'
    },
    {
      feature: 'Battery Performance',
      value: avgBattery,
      importance: 0.25,
      impact: avgBattery < 50 ? 
        'Low average battery level may indicate charging issues' :
        'Good battery performance supports reliable operation'
    },
    {
      feature: 'GPS Signal Quality',
      value: gpsReliability * 100,
      importance: 0.2,
      impact: gpsReliability < 0.8 ? 
        'Intermittent GPS signal affects positioning accuracy' :
        'Reliable GPS signal ensures accurate positioning'
    }
  ].sort((a, b) => b.importance - a.importance);
  
  return { healthScore, riskLevel, explanatoryFactors };
};

/**
 * Calculate variability (coefficient of variation)
 */
const calculateVariability = (values: number[]): number => {
  if (values.length === 0) return 0;
  
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  if (mean === 0) return 0;
  
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  
  return stdDev / mean; // Coefficient of variation
};

/**
 * Calculate position variability
 */
const calculatePositionVariability = (gpsReadings: TelemetryData[]): number => {
  if (gpsReadings.length < 2) return 0;
  
  const distances = [];
  for (let i = 1; i < gpsReadings.length; i++) {
    const prev = gpsReadings[i - 1];
    const curr = gpsReadings[i];
    
    // Simple distance calculation (not perfect for lat/lon but good enough for variability)
    const distance = Math.sqrt(
      Math.pow(curr.gps_lat - prev.gps_lat, 2) + 
      Math.pow(curr.gps_lon - prev.gps_lon, 2)
    );
    distances.push(distance);
  }
  
  return calculateVariability(distances);
};

/**
 * Load and process raw drilling data to generate health scores
 */
export const generateHealthScoresFromTelemetry = async (): Promise<HealthScoreResponse[]> => {
  try {
    // Load raw CSV data (we'll use a simple fetch since it's in public folder)
    const response = await fetch('/data/raw_drilling_sessions.csv');
    const csvText = await response.text();
    
    // Parse CSV data
    const lines = csvText.split('\n').slice(1); // Skip header
    const telemetryData: TelemetryData[] = [];
    
    for (const line of lines) {
      if (line.trim()) {
        const [timestamp, device_id, seq, current_amp, gps_lat, gps_lon, battery_level, ble_id] = line.split(',');
        
        telemetryData.push({
          timestamp: timestamp?.trim(),
          device_id: device_id?.trim(),
          seq: parseInt(seq?.trim() || '0'),
          current_amp: parseFloat(current_amp?.trim() || '0'),
          gps_lat: parseFloat(gps_lat?.trim() || '0'),
          gps_lon: parseFloat(gps_lon?.trim() || '0'),
          battery_level: parseInt(battery_level?.trim() || '0'),
          ble_id: ble_id?.trim()
        });
      }
    }
    
    // Group data by device
    const deviceGroups = telemetryData.reduce((groups, data) => {
      if (!groups[data.device_id]) {
        groups[data.device_id] = [];
      }
      groups[data.device_id].push(data);
      return groups;
    }, {} as Record<string, TelemetryData[]>);
    
    // Calculate health scores for each device
    const healthScores: HealthScoreResponse[] = [];
    
    Object.entries(deviceGroups).forEach(([deviceId, deviceData]) => {
      const { healthScore, riskLevel, explanatoryFactors } = calculateDeviceHealthFromTelemetry(deviceData);
      
      // Add some randomness to confidence interval
      const confidenceRange = 5 + Math.random() * 10;
      
      healthScores.push({
        device_id: deviceId,
        health_score: healthScore,
        confidence_interval: [
          Math.max(0, healthScore - confidenceRange),
          Math.min(100, healthScore + confidenceRange)
        ] as [number, number],
        risk_level: riskLevel,
        explanatory_factors: explanatoryFactors,
        last_calculated: new Date().toISOString()
      });
    });
    
    return healthScores.sort((a, b) => a.device_id.localeCompare(b.device_id));
    
  } catch (error) {
    console.error('Failed to generate health scores from telemetry:', error);
    return [];
  }
};

/**
 * Generate synthetic alerts based on health scores
 */
export const generateAlertsFromHealthScores = (healthScores: HealthScoreResponse[]): MaintenanceAlertResponse[] => {
  const alerts: MaintenanceAlertResponse[] = [];
  
  healthScores.forEach((device, index) => {
    // Generate alerts for devices with medium risk or higher
    if (device.risk_level !== 'low') {
      const alertTypes = ['performance_degradation', 'equipment_failure_risk', 'battery_maintenance'] as const;
      const alertType = alertTypes[index % alertTypes.length];
      
      const severity = device.risk_level === 'critical' ? 'critical' :
                      device.risk_level === 'high' ? 'high' :
                      device.risk_level === 'medium' ? 'medium' : 'low';
      
      const predictedFailureTime = device.health_score < 40 ? 
        new Date(Date.now() + (Math.random() * 72 + 24) * 60 * 60 * 1000) : // 1-3 days
        undefined;
      
      alerts.push({
        id: `fallback-alert-${device.device_id}-${index}`,
        device_id: device.device_id,
        alert_type: alertType,
        severity: severity as any,
        status: 'active',
        title: `${device.risk_level.toUpperCase()} Risk: ${device.device_id}`,
        description: `Health score of ${Math.round(device.health_score)}% indicates ${device.risk_level} risk. ${
          device.explanatory_factors[0]?.impact || 'Monitor equipment performance closely.'
        }`,
        predicted_failure_time: predictedFailureTime?.toISOString(),
        confidence_score: Math.random() * 0.3 + 0.6, // 60-90% confidence
        recommended_actions: getRecommendedActions(device.risk_level, alertType),
        affected_systems: getAffectedSystems(alertType),
        created_at: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(), // Last 24 hours
        metadata: {
          source: 'telemetry_analysis',
          health_score: device.health_score,
          risk_level: device.risk_level
        }
      });
    }
  });
  
  return alerts;
};

const getRecommendedActions = (riskLevel: RiskLevel, alertType: string): string[] => {
  const actions = [];
  
  if (riskLevel === 'critical') {
    actions.push('Schedule immediate maintenance inspection');
    actions.push('Reduce operational load until inspection');
  }
  
  if (alertType === 'battery_maintenance') {
    actions.push('Check battery charging system');
    actions.push('Inspect battery connections');
  } else if (alertType === 'performance_degradation') {
    actions.push('Review current consumption patterns');
    actions.push('Check electrical connections');
  } else if (alertType === 'equipment_failure_risk') {
    actions.push('Schedule comprehensive equipment check');
    actions.push('Monitor operational parameters closely');
  }
  
  actions.push('Update maintenance logs');
  
  return actions;
};

const getAffectedSystems = (alertType: string): string[] => {
  switch (alertType) {
    case 'battery_maintenance':
      return ['Power System', 'Charging Circuit'];
    case 'performance_degradation':
      return ['Drilling Motor', 'Electrical System'];
    case 'equipment_failure_risk':
      return ['Primary Drive', 'Control System', 'Sensors'];
    default:
      return ['General Equipment'];
  }
};