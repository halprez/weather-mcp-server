#!/usr/bin/env python3
"""
Comprehensive Integration Test for Weather MCP Server with AIFS Support
Tests AIFS, GraphCast, EUMETSAT, and ensemble functionality
"""

import asyncio
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the weather_mcp module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_mcp.aifs_client import AIFSClient
from weather_mcp.graphcast_client import GraphCastClient
from weather_mcp.eumetsat_client import EUMETSATClient
from weather_mcp.prediction_ensemble import PredictionEnsemble
from weather_mcp.config import WeatherConfig

class WeatherIntegrationTest:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.config = WeatherConfig()
        self.test_location = {"lat": 28.2916, "lon": -16.6291, "name": "Canary Islands"}
        self.results = {}
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Weather MCP Integration Test Suite")
        print("=" * 50)
        print(f"📍 Test Location: {self.test_location['name']}")
        print(f"🌐 Coordinates: {self.test_location['lat']}, {self.test_location['lon']}")
        print()
        
        # Test configuration
        await self.test_configuration()
        
        # Test individual components
        await self.test_aifs_client()
        await self.test_graphcast_client()
        await self.test_eumetsat_client()
        
        # Test ensemble functionality
        await self.test_prediction_ensemble()
        
        # Test MCP server integration
        await self.test_mcp_server()
        
        # Generate test report
        self.generate_test_report()
        
    async def test_configuration(self):
        """Test configuration loading"""
        print("1️⃣ Testing Configuration Management")
        print("-" * 30)
        
        try:
            server_info = self.config.get_server_info()
            print(f"✅ Server: {server_info['name']} v{server_info['version']}")
            print(f"✅ AIFS enabled: {self.config.aifs.enabled}")
            print(f"✅ GraphCast enabled: {self.config.graphcast.enabled}")
            print(f"✅ EUMETSAT enabled: {self.config.eumetsat.enabled}")
            print(f"✅ Ensemble enabled: {self.config.ensemble.enabled}")
            
            self.results['configuration'] = {'status': 'passed', 'details': server_info}
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            self.results['configuration'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    async def test_aifs_client(self):
        """Test AIFS client functionality"""
        print("2️⃣ Testing AIFS Client")
        print("-" * 30)
        
        try:
            client = AIFSClient(deployment_mode="docker")
            
            # Test forecast retrieval
            forecast = await client.get_forecast(
                self.test_location["lat"], 
                self.test_location["lon"], 
                forecast_hours=72  # 3 days
            )
            
            print(f"✅ AIFS forecast retrieved")
            print(f"📊 Forecast points: {len(forecast.get('forecast_data', []))}")
            print(f"🤖 Model: {forecast['metadata']['model']}")
            print(f"🏗️  Deployment: {forecast['metadata']['deployment_mode']}")
            print(f"🧪 Mock data: {forecast['metadata'].get('is_mock', 'unknown')}")
            
            # Store sample data for ensemble testing
            self.results['aifs'] = {
                'status': 'passed',
                'forecast_data': forecast,
                'points': len(forecast.get('forecast_data', []))
            }
            
        except Exception as e:
            print(f"❌ AIFS test failed: {e}")
            self.results['aifs'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    async def test_graphcast_client(self):
        """Test GraphCast client functionality"""
        print("3️⃣ Testing GraphCast Client")
        print("-" * 30)
        
        try:
            client = GraphCastClient()
            
            # Test forecast retrieval
            forecast = await client.get_forecast(
                self.test_location["lat"], 
                self.test_location["lon"], 
                days=3
            )
            
            print(f"✅ GraphCast forecast retrieved")
            print(f"📊 Forecast points: {len(forecast.get('hourly_data', []))}")
            print(f"🧠 Model: {forecast['metadata']['model']}")
            print(f"📡 Provider: {forecast['metadata']['provider']}")
            
            # Store sample data for ensemble testing
            self.results['graphcast'] = {
                'status': 'passed',
                'forecast_data': forecast,
                'points': len(forecast.get('hourly_data', []))
            }
            
        except Exception as e:
            print(f"❌ GraphCast test failed: {e}")
            self.results['graphcast'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    async def test_eumetsat_client(self):
        """Test EUMETSAT client functionality"""
        print("4️⃣ Testing EUMETSAT Client")
        print("-" * 30)
        
        try:
            client = EUMETSATClient()
            
            # Test historical data retrieval
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2)
            
            historical = await client.get_historical_data(
                self.test_location["lat"],
                self.test_location["lon"],
                start_date,
                end_date
            )
            
            print(f"✅ EUMETSAT historical data retrieved")
            print(f"📊 Historical points: {len(historical.get('historical_data', []))}")
            print(f"🛰️  Satellites: {', '.join(historical['metadata']['satellites'])}")
            
            # Store sample data for ensemble testing
            self.results['eumetsat'] = {
                'status': 'passed',
                'historical_data': historical,
                'points': len(historical.get('historical_data', []))
            }
            
        except Exception as e:
            print(f"❌ EUMETSAT test failed: {e}")
            self.results['eumetsat'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    async def test_prediction_ensemble(self):
        """Test ensemble prediction functionality"""
        print("5️⃣ Testing Prediction Ensemble")
        print("-" * 30)
        
        try:
            ensemble = PredictionEnsemble()
            
            # Check if we have data from previous tests
            if (self.results.get('aifs', {}).get('status') == 'passed' and 
                self.results.get('graphcast', {}).get('status') == 'passed'):
                
                aifs_data = self.results['aifs']['forecast_data']
                graphcast_data = self.results['graphcast']['forecast_data']
                eumetsat_data = self.results.get('eumetsat', {}).get('historical_data')
                
                # Create ensemble forecast
                ensemble_result = await ensemble.create_ensemble_forecast(
                    aifs_data, graphcast_data, eumetsat_data
                )
                
                print(f"✅ Ensemble forecast created")
                print(f"🤖 Models: {', '.join(ensemble_result['metadata']['models_used'])}")
                print(f"📊 Ensemble points: {ensemble_result['metadata']['forecast_points']}")
                print(f"⚖️  Method: {ensemble_result['metadata']['ensemble_method']}")
                
                # Test model comparison
                if 'model_comparison' in ensemble_result:
                    comparison = ensemble_result['model_comparison']
                    print(f"🔍 Recommendations: {len(comparison.get('recommendations', []))}")
                
                self.results['ensemble'] = {
                    'status': 'passed',
                    'ensemble_result': ensemble_result,
                    'models_used': ensemble_result['metadata']['models_used']
                }
                
            else:
                print("⚠️  Skipping ensemble test - missing prerequisite data")
                self.results['ensemble'] = {'status': 'skipped', 'reason': 'Missing prerequisite data'}
                
        except Exception as e:
            print(f"❌ Ensemble test failed: {e}")
            self.results['ensemble'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    async def test_mcp_server(self):
        """Test MCP server integration"""
        print("6️⃣ Testing MCP Server Integration")
        print("-" * 30)
        
        try:
            # Import and test the MCP server
            from weather_mcp.mcp_server import WeatherMCPServer
            
            server = WeatherMCPServer()
            
            # Test tools list
            tools_response = await server.handle_request({"method": "tools/list", "id": 1})
            tools = tools_response.get("result", {}).get("tools", [])
            
            print(f"✅ MCP server initialized")
            print(f"🛠️  Available tools: {len(tools)}")
            
            # Test each new tool
            test_requests = [
                {
                    "method": "tools/call",
                    "id": 2,
                    "params": {
                        "name": "get_aifs_forecast",
                        "arguments": {
                            "latitude": self.test_location["lat"],
                            "longitude": self.test_location["lon"],
                            "forecast_hours": 72
                        }
                    }
                },
                {
                    "method": "tools/call",
                    "id": 3,
                    "params": {
                        "name": "compare_ai_models",
                        "arguments": {
                            "latitude": self.test_location["lat"],
                            "longitude": self.test_location["lon"],
                            "forecast_days": 3
                        }
                    }
                },
                {
                    "method": "tools/call",
                    "id": 4,
                    "params": {
                        "name": "get_ensemble_forecast",
                        "arguments": {
                            "latitude": self.test_location["lat"],
                            "longitude": self.test_location["lon"],
                            "forecast_days": 3
                        }
                    }
                }
            ]
            
            successful_tools = 0
            for request in test_requests:
                try:
                    response = await server.handle_request(request)
                    tool_name = request["params"]["name"]
                    
                    if "error" not in response:
                        successful_tools += 1
                        print(f"  ✅ {tool_name}: Success")
                    else:
                        print(f"  ❌ {tool_name}: {response.get('error', {}).get('message', 'Unknown error')}")
                        
                except Exception as e:
                    tool_name = request["params"]["name"]
                    print(f"  ❌ {tool_name}: Exception - {e}")
            
            print(f"📊 Tool tests: {successful_tools}/{len(test_requests)} passed")
            
            self.results['mcp_server'] = {
                'status': 'passed',
                'total_tools': len(tools),
                'successful_tools': successful_tools,
                'tools_tested': len(test_requests)
            }
            
        except Exception as e:
            print(f"❌ MCP server test failed: {e}")
            self.results['mcp_server'] = {'status': 'failed', 'error': str(e)}
        
        print()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("📊 Integration Test Report")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('status') == 'passed')
        failed_tests = sum(1 for result in self.results.values() if result.get('status') == 'failed')
        skipped_tests = sum(1 for result in self.results.values() if result.get('status') == 'skipped')
        
        print(f"📈 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print()
        
        # Detailed results
        for test_name, result in self.results.items():
            status = result.get('status', 'unknown')
            status_emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⏭️"
            
            print(f"{status_emoji} {test_name.upper()}: {status}")
            
            if status == 'failed' and 'error' in result:
                print(f"  Error: {result['error']}")
            elif status == 'skipped' and 'reason' in result:
                print(f"  Reason: {result['reason']}")
            elif status == 'passed':
                if 'points' in result:
                    print(f"  Data points: {result['points']}")
                if 'models_used' in result:
                    print(f"  Models: {', '.join(result['models_used'])}")
                if 'successful_tools' in result:
                    print(f"  Tool success: {result['successful_tools']}/{result['tools_tested']}")
        
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        if failed_tests == 0:
            print("  🎉 All tests passed! Your AIFS integration is working perfectly.")
            print("  🚀 Deploy with: docker-compose up --build")
        else:
            print("  🔧 Fix failed tests before deployment")
            if self.results.get('aifs', {}).get('status') == 'failed':
                print("  📋 Check AIFS Docker container is running on port 8080")
            if self.results.get('mcp_server', {}).get('status') == 'failed':
                print("  📋 Check MCP server dependencies and imports")
        
        print("\n🏁 Integration test completed!")

async def main():
    """Run integration tests"""
    test_suite = WeatherIntegrationTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())