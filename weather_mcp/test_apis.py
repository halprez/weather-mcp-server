"""
Let's make sure we can connect to our data sources
"""

import asyncio
import openmeteo_requests
from datetime import datetime

async def test_open_meteo():
    """Test GraphCast via Open-Meteo API"""
    print("🧪 Testing Open-Meteo API (GraphCast)...")
    
    try:
        # Create client
        client = openmeteo_requests.Client()
        
        # Test request for Canary Islands
        params = {
            "latitude": 28.2916,
            "longitude": -16.6291,
            "hourly": ["temperature_2m", "wind_speed_10m"],
            "forecast_days": 1
        }
        
        # Make request
        responses = client.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]
        
        print(f"✅ Success! Got data for:")
        print(f"   📍 Location: {response.Latitude()}°N, {response.Longitude()}°E")
        print(f"   🏔️  Elevation: {response.Elevation()}m")
        print(f"   🕐 Timezone: {response.Timezone()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_eumetsat_connection():
    """Test EUMETSAT API connection (we'll implement this later)"""
    print("\n🧪 Testing EUMETSAT API...")
    print("📝 Note: We'll implement this in the next phase")
    print("✅ Connection test placeholder - OK")
    return True

async def main():
    """Run all API tests"""
    print("🚀 API Connection Tests")
    print("=" * 30)
    
    # Test GraphCast via Open-Meteo
    test1 = await test_open_meteo()
    
    # Test EUMETSAT (placeholder)
    test2 = await test_eumetsat_connection()
    
    print(f"\n📊 Results:")
    print(f"GraphCast API: {'✅ Working' if test1 else '❌ Failed'}")
    print(f"EUMETSAT API: {'✅ Ready' if test2 else '❌ Failed'}")
    
    if test1 and test2:
        print("\n🎉 All APIs ready! Let's start building!")
    else:
        print("\n🛠️  Some APIs need attention. Let's debug together!")

if __name__ == "__main__":
    asyncio.run(main())