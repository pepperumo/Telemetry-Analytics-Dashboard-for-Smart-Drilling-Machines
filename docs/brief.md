# Project Brief: Telemetry Analytics Dashboard for Smart Drilling Machines

*Generated on August 26, 2025*

---

## Executive Summary

The Telemetry Analytics Dashboard for Smart Drilling Machines is a comprehensive web-based analytics platform that processes and visualizes real-time telemetry data from IoT-enabled drilling equipment. The system transforms raw sensor data from retrofitted "Pods" into actionable business intelligence, enabling drilling operations to monitor equipment performance, track consumable usage through Smart Tags, detect operational anomalies, and optimize drilling efficiency across their fleet.

The platform addresses the critical need for real-time visibility into drilling operations by providing a centralized dashboard that consolidates telemetry data from multiple machines, processes it into meaningful insights, and presents it through an intuitive web interface. The solution targets drilling operation managers, equipment technicians, and fleet supervisors who need immediate access to operational metrics and anomaly detection capabilities.

## Problem Statement

Drilling operations currently lack real-time visibility into equipment performance and operational efficiency. Traditional drilling machines operate as "black boxes" with limited telemetry capabilities, making it impossible to:

- Monitor real-time equipment status and performance metrics
- Track usage of consumables and verify Smart Tag compliance
- Detect operational anomalies or equipment malfunctions proactively
- Analyze drilling patterns and optimize operational efficiency
- Maintain accurate location tracking for mobile drilling equipment
- Identify gaps in telemetry data that could indicate equipment issues

This lack of visibility results in reactive maintenance practices, suboptimal resource utilization, difficulty in compliance tracking, and potential safety risks from undetected equipment anomalies. The manual data collection and analysis processes are time-consuming and prone to human error, preventing operations teams from making data-driven decisions in real-time.

## Proposed Solution

The Telemetry Analytics Dashboard provides a comprehensive web-based solution that transforms raw IoT telemetry data into actionable operational intelligence. The solution consists of:

**Core Architecture:**
- **Backend Data Processing Engine** (FastAPI): Ingests raw telemetry data, derives operational states from current consumption patterns, detects anomalies, and provides RESTful APIs for frontend consumption
- **Frontend Analytics Dashboard** (React/TypeScript): Presents real-time and historical insights through interactive visualizations, KPI displays, and geographic mapping
- **Data Processing Pipeline**: Automatically categorizes drilling states (OFF ≈0A, STANDBY ≈0.9A, SPINNING ≈3.9A, DRILLING >5A) and identifies Smart Tag usage patterns

**Key Differentiators:**
- **Real-time State Recognition**: Automatically interprets current draw patterns to determine exact equipment operating status
- **Smart Tag Integration**: Seamlessly tracks consumable usage through BLE MAC address detection
- **Comprehensive Anomaly Detection**: Identifies short sessions, telemetry gaps, and missing GPS data
- **Geographic Intelligence**: Maps drilling activity across operational areas with GPS tracking
- **Battery Health Monitoring**: Proactive alerts for equipment power management

This solution succeeds where traditional monitoring systems fail by providing granular, real-time insights specifically tailored to drilling operations, with purpose-built analytics that understand the unique operational patterns of drilling equipment.

## Target Users

### Primary User Segment: Drilling Operations Managers

**Profile:** Mid to senior-level managers responsible for overseeing drilling fleet operations, typically with 5-15 years of experience in construction, mining, or industrial drilling operations. They manage teams of 10-50 technicians and are accountable for operational efficiency, equipment utilization, and project delivery timelines.

**Current Behaviors:** Currently rely on manual reports from field technicians, periodic equipment inspections, and reactive maintenance schedules. They spend significant time consolidating data from multiple sources and struggle with real-time visibility into fleet performance.

**Specific Needs:**
- Real-time fleet performance dashboards accessible from office or mobile
- Historical trend analysis for operational planning and resource allocation
- Anomaly alerts to enable proactive intervention before equipment failures
- Compliance reporting for Smart Tag usage and regulatory requirements

**Goals:** Maximize equipment uptime, optimize resource allocation, reduce operational costs, and ensure regulatory compliance while maintaining safety standards.

### Secondary User Segment: Field Technicians & Equipment Operators

**Profile:** Front-line operators and maintenance technicians with 2-10 years of experience directly operating or servicing drilling equipment. They work on-site and need immediate access to equipment status and performance data.

**Current Behaviors:** Perform manual equipment checks, record operational data in logbooks or basic digital forms, and communicate equipment issues through radio or phone calls to supervisors.

**Specific Needs:**
- Mobile-friendly interface for field access
- Real-time equipment status and alerts
- Historical performance data for troubleshooting
- Simple, intuitive visualizations that don't require technical analytics expertise

**Goals:** Ensure equipment operates efficiently, identify and resolve issues quickly, maintain accurate operational records, and minimize downtime.

## Goals & Success Metrics

### Business Objectives
- **Operational Efficiency**: Reduce equipment downtime by 25% through proactive anomaly detection and maintenance scheduling
- **Compliance Tracking**: Achieve 100% visibility into Smart Tag usage across all drilling sessions
- **Data-Driven Decisions**: Provide real-time operational insights to 100% of operations managers within 30 seconds of data capture
- **Cost Optimization**: Reduce manual data collection and reporting time by 80% through automated analytics
- **Fleet Utilization**: Increase productive drilling time by 15% through optimized operational state management

### User Success Metrics
- **Dashboard Adoption**: 90% of operations managers actively use dashboard daily within 3 months
- **Field Usage**: 75% of field technicians access mobile interface at least once per shift
- **Alert Response**: Average response time to anomaly alerts under 10 minutes
- **Data Accuracy**: 95% telemetry data completeness (accounting for expected 30-second intervals)
- **User Satisfaction**: Net Promoter Score (NPS) of 8+ from primary users within 6 months

### Key Performance Indicators (KPIs)
- **System Uptime**: 99.5% dashboard availability during business hours
- **Data Processing Speed**: Process and visualize telemetry data within 5 seconds of ingestion
- **Anomaly Detection Rate**: Identify 95% of equipment anomalies before they cause operational disruption
- **Session Analysis Coverage**: Successfully categorize 100% of drilling sessions (tagged vs. untagged)
- **Geographic Accuracy**: Maintain GPS location accuracy within 10 meters for 95% of readings
- **Battery Monitoring**: Alert on battery levels below 20% with 100% accuracy

## MVP Scope

### Core Features (Must Have)

- **✅ Telemetry Data Processing**: Parse raw CSV data and derive operating states (OFF/STANDBY/SPINNING/DRILLING) based on current consumption patterns (≈0A, ≈0.9A, ≈3.9A, >5A respectively)
- **✅ Session Analysis Dashboard**: Display total drilling time with date range selection, number of sessions, and average session length calculations
- **✅ Smart Tag Compliance Tracking**: Identify and categorize sessions as tagged vs. untagged based on BLE ID presence, with percentage distribution visualization
- **✅ Operating States Distribution**: Visual breakdown of time spent in each operational state across all sessions
- **✅ Battery Health Monitoring**: Real-time battery level displays with highlighting of low battery conditions (<20%)
- **✅ Geographic Session Mapping**: Interactive map showing drilling session locations across Berlin area with GPS coordinate plotting
- **✅ Anomaly Detection System**: Automated identification of very short sessions, sequence number gaps indicating missing telemetry, and missing GPS values
- **✅ Web-Based Dashboard Interface**: React frontend with responsive design providing clear visual presentation of all insights through charts, KPIs, maps, and data tables

### Out of Scope for MVP

- Real-time streaming data ingestion (current version processes static CSV files)
- Multi-user authentication and role-based access control
- Advanced predictive analytics or machine learning models
- Mobile-specific applications (responsive web interface sufficient)
- Integration with external ERP or maintenance management systems
- Advanced reporting and export capabilities
- Historical data storage beyond current dataset
- Multi-tenant or multi-site deployment capabilities

### MVP Success Criteria

The MVP is considered successful when it demonstrates:
1. **Functional Data Processing**: Successfully processes 100 drilling sessions from July 2025 dataset with accurate state derivation
2. **Complete Insight Coverage**: Displays all 7 required analytical insights (drilling time, sessions, tag compliance, states, battery, map, anomalies)
3. **Technical Reliability**: FastAPI backend serves data consistently with React frontend rendering all visualizations without errors
4. **User Validation**: Operations managers can answer key operational questions using the dashboard within 2 minutes of access

## Post-MVP Vision

### Phase 2 Features

**Real-Time Data Streaming**: Implement WebSocket connections for live telemetry ingestion, replacing batch CSV processing with continuous data flow from IoT Pods. This enables instant alerts and real-time dashboard updates.

**Advanced Analytics Engine**: Deploy machine learning models for predictive maintenance, drilling pattern optimization, and equipment lifecycle management. Include trend analysis and forecasting capabilities.

**Mobile Applications**: Native iOS/Android apps optimized for field technicians, featuring offline capability, push notifications, and camera integration for equipment documentation.

**Enhanced Anomaly Detection**: Implement AI-powered anomaly detection using historical patterns, seasonal adjustments, and cross-device correlation analysis for more sophisticated threat identification.

### Long-term Vision

**Fleet Management Platform**: Evolve into comprehensive fleet management solution supporting multiple equipment types beyond drilling machines, with centralized command center capabilities and multi-site operations management.

**Ecosystem Integration**: Connect with ERP systems, maintenance management platforms, supply chain systems, and regulatory reporting tools to create seamless operational workflows.

**Advanced Intelligence**: Implement autonomous operational recommendations, automated maintenance scheduling, predictive failure analysis, and resource optimization algorithms that learn from operational patterns.

### Expansion Opportunities

**Industry Vertical Expansion**: Adapt platform for construction equipment, mining machinery, agricultural equipment, and other IoT-enabled industrial assets with similar telemetry requirements.

**Geographic Scaling**: Multi-region deployment with localized compliance features, currency support, and region-specific operational standards.

**Partnership Ecosystem**: Integration marketplace for third-party sensors, equipment manufacturers, maintenance service providers, and industry-specific software vendors.

**Data Monetization**: Anonymized industry benchmarking, equipment performance analytics, and operational best practices as subscription services for industry stakeholders.

## Technical Considerations

### Platform Requirements
- **Target Platforms**: Web-based dashboard accessible via modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Browser/OS Support**: Cross-platform compatibility with responsive design for desktop and tablet access
- **Performance Requirements**: Dashboard load time <3 seconds, data visualization rendering <2 seconds for 100-session dataset

### Technology Preferences
- **Frontend**: React 19.1.1 with TypeScript, Vite build system, TailwindCSS for styling
- **Visualization Libraries**: Recharts for charts and analytics, React-Leaflet with Leaflet for geographic mapping
- **Backend**: FastAPI 0.104+ with Python 3.11+, Uvicorn ASGI server for high-performance async processing
- **Data Processing**: Pandas 2.0+ and NumPy 1.24+ for efficient telemetry data manipulation and analysis
- **Database**: File-based CSV processing (MVP), prepared for PostgreSQL/MongoDB transition in Phase 2

### Architecture Considerations
- **Repository Structure**: Monorepo with separate `/backend` and `/frontend` directories, shared `/public/data` for CSV files
- **Service Architecture**: RESTful API design with FastAPI backend serving React SPA frontend, stateless request handling
- **Integration Requirements**: CORS-enabled API for cross-origin requests, structured for future WebSocket integration
- **Security/Compliance**: Input validation with Pydantic models, environment-based configuration with python-dotenv, prepared for authentication middleware

## Constraints & Assumptions

### Constraints

- **Budget**: Development constrained to open-source technologies and minimal cloud infrastructure costs during MVP phase
- **Timeline**: MVP delivery focused on demonstrating core functionality with 100-session July 2025 dataset within current development cycle
- **Resources**: Single developer or small team implementation, requiring technology choices that maximize development velocity
- **Technical**: Limited to CSV file processing for MVP (no real-time streaming), GPS accuracy subject to Berlin area environmental factors and natural jitter

### Key Assumptions

- **Data Quality**: Telemetry data follows consistent 30-second interval pattern with acceptable sequence number gaps representing normal packet loss
- **Operating Environment**: Drilling machines operate in predictable current consumption patterns (0A=OFF, 0.9A=STANDBY, 3.9A=SPINNING, >5A=DRILLING)
- **User Access**: Operations managers have reliable internet connectivity and modern browser access during business hours
- **Smart Tag Reliability**: BLE MAC address detection provides sufficient accuracy for consumable tracking despite expected packet loss
- **Geographic Scope**: Berlin area GPS coordinates are representative of typical operational environments
- **Session Definition**: Continuous timestamp sequences per device_id accurately represent complete drilling sessions
- **Battery Monitoring**: Pod battery level reporting is accurate and 20% threshold is appropriate for operational alerts
- **Scalability Timeline**: Current architecture will support growth to larger datasets and real-time processing in Phase 2
- **User Adoption**: Field technicians and operations managers will embrace web-based analytics tools over manual data collection methods

## Risks & Open Questions

### Key Risks

- **Data Accuracy Risk**: Current consumption thresholds (0A, 0.9A, 3.9A, >5A) may not accurately represent all drilling machine models or operating conditions, potentially leading to incorrect state classification
- **Scalability Performance**: CSV file processing approach may not scale efficiently when dataset grows beyond 100 sessions or requires real-time processing capabilities
- **GPS Reliability**: Berlin area GPS jitter and potential signal loss in industrial environments could impact location-based analytics accuracy and reliability
- **User Adoption Resistance**: Operations teams accustomed to manual processes may resist transitioning to digital dashboard, affecting system value realization
- **Battery Threshold Accuracy**: 20% battery alert threshold may be too conservative or aggressive depending on actual Pod power consumption patterns and operational requirements
- **Smart Tag Detection Gaps**: BLE packet loss during sessions could result in incorrect categorization of tagged vs. untagged sessions, affecting compliance reporting
- **Single Point of Failure**: Monolithic architecture creates dependency risks where frontend or backend failures disable entire system functionality

### Open Questions

- How do current consumption patterns vary across different drilling machine manufacturers, models, and age of equipment?
- What is the acceptable telemetry data loss percentage before operational insights become unreliable?
- Should the system support multiple geographic regions with different GPS accuracy requirements and regulatory compliance needs?
- How frequently do drilling operations require real-time alerts vs. historical analysis, and what response time expectations exist?
- What integration requirements exist with existing fleet management, ERP, or maintenance management systems?
- Are there industry-specific compliance or regulatory reporting requirements that the system must accommodate?
- What backup and disaster recovery requirements exist for operational continuity?

### Areas Needing Further Research

- **Equipment Calibration Study**: Validate current consumption thresholds across diverse drilling equipment to ensure accurate state detection
- **User Experience Research**: Conduct interviews with operations managers and field technicians to validate dashboard design and feature priorities
- **Competitive Analysis**: Research existing industrial IoT analytics platforms to identify differentiation opportunities and industry best practices
- **Scalability Architecture**: Investigate database technologies, caching strategies, and real-time processing frameworks for Phase 2 implementation
- **Security Framework**: Define authentication, authorization, and data protection requirements for production deployment
- **Integration Landscape**: Map existing operational technology systems to plan integration strategy and data flow requirements

## Appendices

### A. Research Summary

**Current Project Analysis**: The existing codebase demonstrates a well-structured MVP implementation with FastAPI backend (main.py, data processing services) and React frontend (TypeScript components for analytics visualization). The system successfully processes the July 2025 drilling sessions dataset containing 100 sessions with telemetry captured every 30 seconds.

**Technical Architecture Review**: The monorepo structure with separate backend/frontend directories, comprehensive package dependencies (FastAPI, Pandas, React 19, Recharts, Leaflet), and test environment setup indicates production-ready development practices.

**Data Processing Capabilities**: Current implementation handles CSV parsing, derives operational states from current consumption, detects Smart Tag usage patterns, identifies anomalies, and provides geographic mapping of drilling sessions across Berlin area.

### B. Stakeholder Input

**Development Team Assessment**: Current implementation demonstrates strong technical foundation with modern technology stack, type-safe TypeScript implementation, and scalable architecture patterns suitable for Phase 2 expansion.

**Operational Requirements**: Based on project specification, the system addresses core operational needs for drilling time tracking, session analysis, Smart Tag compliance, battery monitoring, and anomaly detection.

### C. References

- Project Repository: Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines
- Dataset: Raw drilling sessions CSV (July 2025, Berlin area)
- Technology Documentation: FastAPI, React 19, Recharts, Leaflet mapping libraries
- Development Tools: Vite build system, TypeScript, TailwindCSS, ESLint

## Next Steps

### Immediate Actions

1. **Validate Current Implementation**: Test all dashboard features with the 100-session dataset to ensure complete MVP functionality
2. **User Acceptance Testing**: Present dashboard to operations managers for feedback on insights presentation and usability
3. **Performance Optimization**: Profile data processing performance and optimize visualization rendering for larger datasets
4. **Documentation Enhancement**: Complete README with setup instructions, API documentation, and operational guidelines
5. **Deployment Preparation**: Configure production environment setup, monitoring, and backup procedures

### PM Handoff

This Project Brief provides the full context for the Telemetry Analytics Dashboard for Smart Drilling Machines project. The system successfully addresses core operational visibility needs through a modern web-based analytics platform that processes IoT telemetry data into actionable business intelligence.

**For Product Manager Review**: Please start in 'PRD Generation Mode', review this brief thoroughly to work with the development team to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements. Focus on validating user personas, success metrics, and Phase 2 roadmap priorities based on operational feedback and market analysis.

**Key Validation Areas**: Confirm current consumption thresholds accuracy, validate battery alert thresholds, review anomaly detection criteria, and assess geographic expansion requirements for operational scaling.

---

*Project Brief completed on August 26, 2025 by Business Analyst Mary*
