"""
Integration tests for ML Feature Engineering with existing system

Tests ensure the ML pipeline integrates correctly with existing DataProcessor
and doesn't impact existing functionality.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from backend.app.services.data_processor import DataProcessor
from backend.app.ml import MLService


class TestMLIntegration:
    """Integration tests for ML service with existing system"""
    
    @pytest.mark.asyncio
    async def test_ml_service_integration(self):
        """Test MLService integrates correctly with existing DataProcessor"""
        
        # Use real DataProcessor with actual data
        processor = DataProcessor()
        processor.load_data()
        
        # Create ML service
        ml_service = MLService(processor)
        
        # Initialize ML service
        success = await ml_service.initialize()
        assert success is True
        assert ml_service.initialized is True
        
        # Extract features
        features = await ml_service.extract_features()
        
        # Verify structure
        assert 'metadata' in features
        assert 'features' in features
        assert len(features['features']) > 0
        
        # Verify processing performance
        processing_time = features['metadata']['processing_time_seconds']
        assert processing_time < 30  # Under 30 second requirement
        
        # Get feature summary
        summary = ml_service.get_feature_summary(features)
        assert 'fleet_size' in summary
        assert summary['fleet_size'] > 0
    
    def test_existing_functionality_unchanged(self):
        """Test that existing DataProcessor functionality is unchanged"""
        
        # Create DataProcessor
        processor = DataProcessor()
        processor.load_data()
        
        # Test existing methods still work
        insights = processor.calculate_insights()
        assert insights.total_sessions > 0
        assert insights.total_drilling_time_hours >= 0
        
        # Test anomaly detection
        anomalies = processor.detect_anomalies()
        assert hasattr(anomalies, 'short_sessions')
        assert hasattr(anomalies, 'missing_telemetry')
        
        # Test session timeline
        timeline = processor.get_session_timeline()
        assert isinstance(timeline, list)
        
        # Test battery trends
        trends = processor.get_battery_trends()
        assert isinstance(trends, list)
    
    def test_ml_service_status(self):
        """Test ML service status reporting"""
        
        processor = DataProcessor()
        processor.load_data()
        
        ml_service = MLService(processor)
        
        # Test status before initialization
        status = ml_service.get_status()
        assert status['enabled'] is True
        assert status['initialized'] is False
        assert status['data_available'] is True
        
        # Test status after initialization
        asyncio.run(ml_service.initialize())
        status = ml_service.get_status()
        assert status['initialized'] is True
        assert status['components']['feature_engineering'] == "Initialized"
    
    @pytest.mark.asyncio
    async def test_performance_regression(self):
        """Test that ML integration doesn't slow down existing operations"""
        
        # Test without ML
        processor = DataProcessor()
        
        start_time = datetime.now()
        processor.load_data()
        insights = processor.calculate_insights()
        baseline_time = (datetime.now() - start_time).total_seconds()
        
        # Test with ML
        ml_service = MLService(processor)
        await ml_service.initialize()
        
        start_time = datetime.now()
        insights_with_ml = processor.calculate_insights()
        ml_time = (datetime.now() - start_time).total_seconds()
        
        # ML shouldn't significantly impact existing operations
        assert ml_time < baseline_time * 2  # Allow 2x slower max
        
        # Results should be identical
        assert insights.total_sessions == insights_with_ml.total_sessions
        assert insights.total_drilling_time_hours == insights_with_ml.total_drilling_time_hours
    
    def test_ml_feature_flag(self):
        """Test ML can be disabled via environment variable"""
        
        import os
        
        # Set environment variable to disable ML
        original_value = os.environ.get('ML_ENABLED', None)
        os.environ['ML_ENABLED'] = 'false'
        
        try:
            processor = DataProcessor()
            processor.load_data()
            
            ml_service = MLService(processor)
            
            # Should be disabled
            assert ml_service.enabled is False
            
            # Initialize should return False
            result = asyncio.run(ml_service.initialize())
            assert result is False
            
        finally:
            # Restore original environment
            if original_value is not None:
                os.environ['ML_ENABLED'] = original_value
            else:
                del os.environ['ML_ENABLED']
    
    @pytest.mark.asyncio
    async def test_error_handling_graceful_degradation(self):
        """Test graceful degradation when ML encounters errors"""
        
        processor = DataProcessor()
        processor.load_data()
        
        ml_service = MLService(processor)
        await ml_service.initialize()
        
        # Simulate error condition (clear data after initialization)
        processor.raw_df = None
        
        # ML should handle error gracefully
        with pytest.raises(ValueError):
            await ml_service.extract_features()
        
        # But existing functionality should still work if we restore data
        processor.load_data()
        insights = processor.calculate_insights()
        assert insights.total_sessions > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])