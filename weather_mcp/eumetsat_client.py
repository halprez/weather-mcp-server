"""
EUMETSAT Client - Day 4
Mock implementation for now - we'll make it real in the next phase
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import random

class EUMETSATClient:
    """
    EUMETSAT Historical Weather Data Client
    
    For now, this is mock data. In the next phase, we'll connect to
    real EUMETSAT APIs for historical satellite data.
    """
    
    def __init__(self):
        print("🛰️  EUMETSAT Client initialized (mock mode)", file=sys.stderr)
        
    async def get_historical_data(self, 
                                latitude: float,
                                longitude: float, 
                                start_date: datetime,
                                end_date: datetime) -> Dict:
        """
        Get historical weather data
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start of historical period  
            end_date: End of historical period
            
        Returns:
            Dictionary with historical weather data
        """
        print(f"📚 Getting historical data for {latitude}, {longitude}", file=sys.stderr)
        print(f"📅 Period: {start_date.date()} to {end_date.date()}", file=sys.stderr)
        
        # Generate mock historical data
        data_points = []
        current_date = start_date
        
        while current_date < end_date:
            # Create realistic-looking mock data
            data_point = {
                "time": current_date.isoformat(),
                "temperature": 15 + random.uniform(-5, 15),  # Realistic temperature range
                "humidity": 40 + random.uniform(0, 40),      # Realistic humidity
                "precipitation": random.uniform(0, 5) if random.random() < 0.3 else 0,
                "wind_speed": random.uniform(5, 25),
                "pressure": 1000 + random.uniform(-30, 30)
            }
            
            data_points.append(data_point)
            current_date += timedelta(hours=6)  # 6-hourly data
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "historical_data": data_points,
            "metadata": {
                "source": "EUMETSAT (mock)",
                "satellites": ["MSG", "SEVIRI", "Meteosat"],
                "note": "Real EUMETSAT integration coming soon!",
                "data_points": len(data_points)
            }
        }

# Test EUMETSAT client
async def test_eumetsat_client():
    """Test our EUMETSAT client"""
    print("🧪 Testing EUMETSAT Client")
    print("=" * 30)
    
    client = EUMETSATClient()
    
    # Get 7 days of historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    historical = await client.get_historical_data(
        28.2916, -16.6291, start_date, end_date
    )
    
    print("✅ Historical data received!")
    print(f"📊 Data points: {len(historical['historical_data'])}")
    print(f"🛰️  Source: {historical['metadata']['source']}")
    
    # Show sample data
    print("\n📈 Sample historical data:")
    for i, point in enumerate(historical['historical_data'][:3]):
        print(f"  {i+1}. {point['time'][:16]} - {point['temperature']:.1f}°C")

if __name__ == "__main__":
    asyncio.run(test_eumetsat_client())
