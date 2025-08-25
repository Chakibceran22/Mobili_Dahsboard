"""
Weather Station Telemetry for ThingsBoard
=========================================

This script fetches meteorological data from the Open-Meteo API and sends it
to ThingsBoard as telemetry data, treating the API as a virtual weather sensor.

Prerequisites:
1. Run create_weather_station.py first to create the device
2. The device token should be in exp/weather_station.txt
3. Install required packages: pip install openmeteo-requests pandas requests-cache retry-requests
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import requests
import time
import json
from datetime import datetime

class WeatherStationTelemetry:
    def __init__(self, access_token, base_url="http://localhost:8081"):
        self.access_token = access_token
        self.base_url = base_url
        
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # API configuration
        self.api_url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": 36.7576523413059,
            "longitude": 3.0605869645037327,
            "hourly": ["temperature_2m", "rain", "cloud_cover", "direct_radiation"],
            "timezone": "Europe/London",
            "forecast_days": 7,
        }
    
    def fetch_weather_data(self):
        """Fetch weather data from Open-Meteo API"""
        try:
            print("🌐 Fetching weather data from Open-Meteo API...")
            responses = self.openmeteo.weather_api(self.api_url, params=self.params)
            
            # Process first location
            response = responses[0]
            print(f"📍 Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
            print(f"⛰️  Elevation: {response.Elevation()} m asl")
            print(f"🕐 Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
            
            # Process hourly data
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_rain = hourly.Variables(1).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
            hourly_direct_radiation = hourly.Variables(3).ValuesAsNumpy()
            
            # Create DataFrame
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ),
                "temperature_2m": hourly_temperature_2m,
                "rain": hourly_rain,
                "cloud_cover": hourly_cloud_cover,
                "direct_radiation": hourly_direct_radiation
            }
            
            df = pd.DataFrame(data=hourly_data)
            print(f"✅ Successfully fetched {len(df)} hourly data points")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
    
    def send_telemetry_batch(self, weather_data, max_points=50):
        """Send weather data as telemetry to ThingsBoard in batches"""
        if weather_data is None or weather_data.empty:
            print("❌ No weather data to send")
            return False
        
        print(f"📤 Sending {len(weather_data)} data points as telemetry...")
        
        # Send data in batches to avoid overwhelming the API
        total_points = len(weather_data)
        batch_size = min(max_points, total_points)
        
        success_count = 0
        
        for i in range(0, total_points, batch_size):
            batch = weather_data.iloc[i:i+batch_size]
            
            # Prepare telemetry data for this batch
            telemetry_data = {}
            
            for _, row in batch.iterrows():
                timestamp = int(row['date'].timestamp() * 1000)  # Convert to milliseconds
                
                # Create telemetry entry for this timestamp
                telemetry_data[timestamp] = {
                    "temperature_2m": round(float(row['temperature_2m']), 2),
                    "rain": round(float(row['rain']), 2),
                    "cloud_cover": round(float(row['cloud_cover']), 1),
                    "direct_radiation": round(float(row['direct_radiation']), 2)
                }
            
            # Send batch to ThingsBoard
            success = self._send_telemetry_request(telemetry_data)
            
            if success:
                success_count += len(batch)
                print(f"✅ Batch {i//batch_size + 1}: Sent {len(batch)} points "
                      f"({success_count}/{total_points} total)")
            else:
                print(f"❌ Batch {i//batch_size + 1}: Failed to send {len(batch)} points")
            
            # Small delay between batches
            if i + batch_size < total_points:
                time.sleep(0.5)
        
        print(f"📊 Telemetry transmission complete: {success_count}/{total_points} points sent")
        return success_count > 0
    
    def _send_telemetry_request(self, telemetry_data):
        """Send a single telemetry request to ThingsBoard"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/{self.access_token}/telemetry",
                json=telemetry_data,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending telemetry: {e}")
            return False
    
    def send_current_weather(self):
        """Send only the current weather data point"""
        weather_data = self.fetch_weather_data()
        if weather_data is None or weather_data.empty:
            return False
        
        # Get the most recent data point (current conditions)
        current_data = weather_data.iloc[0]  # First row is current time
        
        telemetry_data = {
            "temperature_2m": round(float(current_data['temperature_2m']), 2),
            "rain": round(float(current_data['rain']), 2),
            "cloud_cover": round(float(current_data['cloud_cover']), 1),
            "direct_radiation": round(float(current_data['direct_radiation']), 2),
            "timestamp": int(time.time() * 1000)
        }
        
        print(f"🌤️  Current weather conditions:")
        print(f"   🌡️  Temperature: {telemetry_data['temperature_2m']}°C")
        print(f"   🌧️  Rain: {telemetry_data['rain']} mm")
        print(f"   ☁️  Cloud Cover: {telemetry_data['cloud_cover']}%")
        print(f"   ☀️  Solar Radiation: {telemetry_data['direct_radiation']} W/m²")
        
        success = self._send_telemetry_request(telemetry_data)
        
        if success:
            print("✅ Current weather data sent successfully!")
        else:
            print("❌ Failed to send current weather data")
        
        return success

def load_device_config():
    """Load device configuration from file"""
    try:
        config = {}
        with open("exp/weather_station.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key] = value
        return config.get("token"), config.get("device_id")
    except FileNotFoundError:
        return None, None

def main():
    print("🌤️  Weather Station Telemetry for ThingsBoard")
    print("=" * 60)
    
    # Load configuration
    access_token, device_id = load_device_config()
    
    if not access_token:
        print("❌ No Weather Station device configuration found!")
        print("📋 Please run: python exp/create_weather_station.py first")
        return
    
    print(f"✅ Loaded Weather Station device configuration")
    print(f"🆔 Device ID: {device_id}")
    print(f"🔑 Token: {access_token[:8]}...")
    print()
    
    # Create telemetry sender
    weather_station = WeatherStationTelemetry(access_token)
    
    # Ask user what to send
    print("📋 Choose telemetry mode:")
    print("   1. Send current weather only")
    print("   2. Send full 7-day forecast data")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            weather_station.send_current_weather()
        elif choice == "2":
            weather_data = weather_station.fetch_weather_data()
            weather_station.send_telemetry_batch(weather_data)
        else:
            print("⚠️  Invalid choice, sending current weather only")
            weather_station.send_current_weather()
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Weather station telemetry complete!")
    print("📊 Check your ThingsBoard dashboard to view the meteorological data")

if __name__ == "__main__":
    main()
