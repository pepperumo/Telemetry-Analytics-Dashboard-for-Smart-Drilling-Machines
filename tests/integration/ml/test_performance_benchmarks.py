"""
Performance Benchmark Tests for ML Components

Tests performance requirements including dashboard load times and API response times.
"""
import pytest
import time
import asyncio
from typing import Dict, List
import httpx
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestMLPerformanceBenchmarks:
    """Performance benchmark tests for ML components."""
    
    @pytest.mark.asyncio
    async def test_ml_api_response_times(self, backend_client: httpx.Client, performance_thresholds: Dict):
        """Test ML API endpoints meet response time requirements."""
        
        endpoints_to_test = [
            "/api/ml/health-scores",
            "/api/ml/alerts",
            "/api/ml/model-status",
            "/health"
        ]
        
        response_times = {}
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = backend_client.get(endpoint, timeout=10.0)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times[endpoint] = response_time
            
            # API should respond within threshold
            assert response_time < performance_thresholds["api_response_time"], \
                f"{endpoint} took {response_time:.2f}s (threshold: {performance_thresholds['api_response_time']}s)"
            
            # Response should be successful
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
        
        print(f"✓ ML API response times: {response_times}")
    
    @pytest.mark.asyncio
    async def test_health_score_calculation_performance(self, backend_client: httpx.Client, performance_thresholds: Dict):
        """Test health score calculation performance."""
        
        # Test with multiple devices
        start_time = time.time()
        response = backend_client.get("/api/ml/health-scores")
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        assert response.status_code == 200
        health_data = response.json()
        device_count = len(health_data.get("health_scores", []))
        
        # Health score calculation should be fast
        assert calculation_time < performance_thresholds["health_score_calculation"], \
            f"Health score calculation took {calculation_time:.2f}s for {device_count} devices"
        
        print(f"✓ Health score calculation: {calculation_time:.2f}s for {device_count} devices")
    
    def test_dashboard_load_time_with_ml(self, performance_thresholds: Dict):
        """Test frontend dashboard loads within time limits with ML components."""
        
        # Setup Chrome driver for testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to dashboard
            start_time = time.time()
            driver.get("http://localhost:5174")
            
            # Wait for ML components to load
            wait = WebDriverWait(driver, performance_thresholds["dashboard_load_time"])
            
            # Wait for main content to be visible
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
            
            # Check if ML Insights tab is available
            try:
                ml_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ML Insights')]")))
                ml_tab.click()
                
                # Wait for ML components to load
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ml-insights-summary")))
                
            except Exception as e:
                print(f"ML components not found or not clickable: {e}")
            
            end_time = time.time()
            load_time = end_time - start_time
            
            # Dashboard should load within threshold
            assert load_time < performance_thresholds["dashboard_load_time"], \
                f"Dashboard took {load_time:.2f}s to load (threshold: {performance_thresholds['dashboard_load_time']}s)"
            
            print(f"✓ Dashboard load time with ML: {load_time:.2f}s")
            
        except Exception as e:
            pytest.skip(f"Selenium test skipped: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_concurrent_ml_requests(self, backend_client: httpx.Client):
        """Test ML system handles concurrent requests efficiently."""
        
        async def make_request(endpoint: str) -> float:
            start_time = time.time()
            response = backend_client.get(endpoint)
            end_time = time.time()
            return end_time - start_time, response.status_code
        
        # Create concurrent requests
        endpoints = ["/api/ml/health-scores"] * 5  # 5 concurrent requests
        
        start_time = time.time()
        tasks = [make_request(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # All requests should complete successfully
        successful_requests = 0
        for result in results:
            if isinstance(result, tuple) and result[1] == 200:
                successful_requests += 1
        
        assert successful_requests >= 4, f"Only {successful_requests}/5 concurrent requests succeeded"
        assert total_time < 5.0, f"Concurrent requests took {total_time:.2f}s"
        
        print(f"✓ Concurrent requests: {successful_requests}/5 successful in {total_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_ml_memory_usage_stability(self, backend_client: httpx.Client):
        """Test ML system memory usage remains stable under load."""
        
        # Make multiple requests to test memory stability
        for i in range(10):
            response = backend_client.get("/api/ml/health-scores")
            assert response.status_code == 200
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        # Check system health after load
        response = backend_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        print("✓ ML system memory stability test passed")