# ML System User Guide

## Overview

The Machine Learning (ML) system provides intelligent health scoring and predictive maintenance insights for drilling equipment based on real telemetry data analysis. This guide explains how to use the ML features in the Telemetry Analytics Dashboard.

## What the ML System Does

The ML system analyzes telemetry data from your drilling equipment to:

1. **Calculate Health Scores**: Provides a 0-100 health score for each drilling device
2. **Generate Predictive Alerts**: Identifies potential maintenance needs before equipment fails
3. **Explain Health Factors**: Shows which specific metrics are affecting equipment health
4. **Track Health Trends**: Monitors equipment condition over time

## Health Score Calculation

### Understanding Health Scores

Health scores range from 0-100, where:
- **90-100**: Excellent condition
- **70-89**: Good condition  
- **50-69**: Requires attention
- **30-49**: Maintenance recommended
- **0-29**: Critical condition

### Health Score Components

The ML system calculates health scores using three weighted factors:

| Factor | Weight | Description | What It Measures |
|--------|--------|-------------|------------------|
| **Current Stability** | 40% | Electrical consistency during operations | Motor wear, electrical issues |
| **Battery Performance** | 40% | Battery health and degradation patterns | Battery capacity, charging efficiency |
| **GPS Reliability** | 20% | Location tracking consistency | Antenna issues, connectivity problems |

### Example Health Score Breakdown

```
Device 7a3f55e1: Health Score 55.9%
├── Current Stability: 64.5% (Negative impact - 40% weight)
│   └── High variability in current draw detected
├── Battery Performance: 25.4% (Negative impact - 40% weight)  
│   └── Battery voltage dropping faster than normal
└── GPS Reliability: 100.0% (Positive impact - 20% weight)
    └── GPS signal consistently strong
```

## Using the ML Dashboard

### Accessing ML Features

1. Open the Telemetry Analytics Dashboard
2. Navigate to the ML sections in the main dashboard
3. ML data is integrated alongside existing analytics

### Health Scores Display

The health scores are shown in several places:
- **Overview Cards**: Summary of equipment health status
- **Health Trends Charts**: Historical health score progression
- **Device Detail Views**: Detailed breakdown by equipment

### Interpreting Alerts

Predictive maintenance alerts provide:
- **Severity Level**: LOW, MEDIUM, HIGH, CRITICAL
- **Predicted Issue**: Type of maintenance needed
- **Timeframe**: When maintenance should be performed
- **Recommended Actions**: Specific steps to take
- **Confidence Level**: How certain the prediction is

### Example Alert

```
🔴 HIGH Severity Alert
Device: device_001
Issue: Battery replacement needed
Timeframe: 48-72 hours
Confidence: 87%

Recommended Actions:
✓ Schedule battery replacement
✓ Monitor charging patterns  
✓ Check current consumption trends
```

## Practical Usage Scenarios

### Scenario 1: Daily Operations Monitoring

**Use Case**: Daily check of equipment status

**Steps**:
1. Review health score overview on main dashboard
2. Identify devices with scores below 70%
3. Check explanatory factors for problematic devices
4. Review any new alerts generated

**Action Items**:
- Devices 70-89%: Monitor trends
- Devices 50-69%: Plan maintenance within 1-2 weeks
- Devices below 50%: Schedule immediate inspection

### Scenario 2: Maintenance Planning

**Use Case**: Weekly maintenance scheduling

**Steps**:
1. Review predictive alerts by severity level
2. Check health trend charts for declining equipment
3. Cross-reference with operational schedules
4. Prioritize based on alert confidence and business impact

**Planning Guidelines**:
- **Critical Alerts**: Schedule within 24 hours
- **High Alerts**: Schedule within 48-72 hours  
- **Medium Alerts**: Plan within 1-2 weeks
- **Low Alerts**: Monitor and include in routine maintenance

### Scenario 3: Equipment Performance Analysis

**Use Case**: Understanding equipment degradation patterns

**Steps**:
1. Select specific device for detailed analysis
2. Review health score history over time
3. Examine explanatory factors trends
4. Correlate with operational data and maintenance history

**Analysis Questions**:
- Which factor contributes most to health decline?
- Are there seasonal or usage patterns?
- How effective were previous maintenance actions?
- What's the expected lifespan based on current trends?

## Understanding ML Predictions

### Confidence Levels

ML predictions include confidence scores:
- **90-100%**: Very high confidence - immediate action recommended
- **80-89%**: High confidence - plan action soon
- **70-79%**: Moderate confidence - monitor closely
- **60-69%**: Lower confidence - validate with manual inspection
- **Below 60%**: Low confidence - treat as early warning only

### Prediction Accuracy

The ML system provides:
- **Explanatory Factors**: Why a prediction was made
- **Historical Context**: Recent health score trends
- **Data Quality Indicators**: How reliable the input data is

### When to Trust Predictions

Trust ML predictions when:
✅ Confidence level is above 70%
✅ Health trend shows consistent decline
✅ Multiple factors point to same issue
✅ Prediction aligns with operational observations

Use caution when:
⚠️ Confidence level is below 70%
⚠️ Conflicting signals from different factors
⚠️ Limited historical data available
⚠️ Recent maintenance or configuration changes

## Troubleshooting and FAQ

### Common Questions

**Q: Why is my health score fluctuating daily?**
A: Daily fluctuations (±5-10%) are normal due to operational variations. Focus on weekly trends rather than daily changes.

**Q: A device shows good health but failed unexpectedly. Why?**
A: The ML system can't predict all failure modes. It focuses on gradual degradation patterns, not sudden mechanical failures or external factors.

**Q: How often are health scores updated?**
A: Health scores are calculated on-demand when you access the dashboard, using the latest available telemetry data.

**Q: Can I ignore low-confidence alerts?**
A: Low-confidence alerts (below 70%) should be treated as early warnings. Use them to guide manual inspections rather than immediate action.

### Troubleshooting Issues

**Problem: Health scores not updating**
- Check if telemetry data is being received
- Verify backend ML service is running
- Check system logs for ML processing errors

**Problem: All health scores showing as 0**
- May indicate insufficient historical data
- Check if feature engineering pipeline is working
- Verify ML models are properly loaded

**Problem: Alerts not generating**
- Check if health scores are being calculated
- Verify alert thresholds are properly configured
- Review ML service logs for alert generation errors

## Best Practices

### For Daily Operations

1. **Morning Health Check**: Review overnight health score changes and new alerts
2. **Trend Monitoring**: Focus on weekly trends rather than daily fluctuations
3. **Alert Prioritization**: Address high-confidence, high-severity alerts first
4. **Documentation**: Record maintenance actions taken based on ML recommendations

### For Maintenance Planning

1. **Proactive Scheduling**: Use 70% health score as trigger for maintenance planning
2. **Confidence Validation**: Validate low-confidence predictions with manual inspection
3. **Historical Analysis**: Review health trends before and after maintenance
4. **Preventive Action**: Address declining trends before they become critical

### For Long-term Equipment Management

1. **Performance Tracking**: Monitor equipment health over months/years
2. **Maintenance Effectiveness**: Evaluate if maintenance improves health scores
3. **Replacement Planning**: Use consistent health decline as input for replacement decisions
4. **Data Quality**: Ensure consistent telemetry data collection for accurate predictions

## Data Privacy and Security

The ML system:
- Processes only technical telemetry data (current, battery, GPS)
- Does not collect or process personal information
- Stores feature data locally within your system
- Follows same security protocols as existing dashboard data

All ML predictions and health scores are derived from your equipment's operational data and remain within your local system infrastructure.