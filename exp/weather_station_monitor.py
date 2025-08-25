"""
Weather Station Continuous Monitor for ThingsBoard
==================================================

This script continuously monitors weather conditions by fetching data from
the Open-Meteo API at regular intervals and sending it as telemetry to ThingsBoard.
This simulates a real weather station that reports conditions periodically.

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
import signal
import sys
from datetime import datetime

class WeatherStationMonitor:
    def __init__(self, access_token, base_url="http://localhost:8081"):
        self.access_token = access_token
        self.base_url = base_url
        self.running = True
        
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=1800)  # 30 min cache
        retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # API configuration
        self.api_url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": 36.7576523413059,
            "longitude": 3.0605869645037327,
            "hourly": ["temperature_2m", "rain", "cloud_cover", "direct_radiation"],
            "timezone": "Europe/London",
            "forecast_days": 1,  # Only get current day for monitoring
        }
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def fetch_current_weather(self):
        """Fetch current weather data from Open-Meteo API"""
        try:
            responses = self.openmeteo.weather_api(self.api_url, params=self.params)
            
            # Process first location
            response = responses[0]
            
            # Process hourly data - get the first (current) hour
            hourly = response.Hourly()
            
            # Get current values (first index)
            current_temp = float(hourly.Variables(0).ValuesAsNumpy()[0])
            current_rain = float(hourly.Variables(1).ValuesAsNumpy()[0])
            current_cloud_cover = float(hourly.Variables(2).ValuesAsNumpy()[0])
            current_radiation = float(hourly.Variables(3).ValuesAsNumpy()[0])
            
            return {
                "temperature_2m": round(current_temp, 2),
                "rain": round(current_rain, 2),
                "cloud_cover": round(current_cloud_cover, 1),
                "direct_radiation": round(current_radiation, 2),
                "timestamp": int(time.time() * 1000)
            }
            
        except Exception as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
    
    def send_telemetry(self, weather_data):
        """Send weather data as telemetry to ThingsBoard"""
        if weather_data is None:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/{self.access_token}/telemetry",
                json=weather_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending telemetry: {e}")
            return False
    
    def monitor(self, interval_minutes=15):
        """Start continuous monitoring with specified interval"""
        print(f"🌤️  Starting weather station monitoring...")
        print(f"📊 Reporting interval: {interval_minutes} minutes")
        print(f"📍 Location: Algiers, Algeria (36.76°N, 3.06°E)")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
        print()
        
        interval_seconds = interval_minutes * 60
        reading_count = 0
        success_count = 0
        
        while self.running:
            try:
                reading_count += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"📋 Reading #{reading_count} at {current_time}")
                
                # Fetch current weather
                weather_data = self.fetch_current_weather()
                
                if weather_data:
                    # Display current conditions
                    print(f"   🌡️  Temperature: {weather_data['temperature_2m']}°C")
                    print(f"   🌧️  Rain: {weather_data['rain']} mm")
                    print(f"   ☁️  Cloud Cover: {weather_data['cloud_cover']}%")
                    print(f"   ☀️  Solar Radiation: {weather_data['direct_radiation']} W/m²")
                    
                    # Send to ThingsBoard
                    if self.send_telemetry(weather_data):
                        success_count += 1
                        print(f"   ✅ Telemetry sent successfully")
                    else:
                        print(f"   ❌ Failed to send telemetry")
                else:
                    print(f"   ❌ Failed to fetch weather data")
                
                print(f"   📊 Success rate: {success_count}/{reading_count} ({100*success_count/reading_count:.1f}%)")
                print()
                
                # Wait for next reading
                if self.running:
                    print(f"⏳ Next reading in {interval_minutes} minutes...")
                    for i in range(interval_seconds):
                        if not self.running:
                            break
                        time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⏳ Retrying in 1 minute...")
                time.sleep(60)
        
        print(f"\n📊 Monitoring session summary:")
        print(f"   📋 Total readings: {reading_count}")
        print(f"   ✅ Successful transmissions: {success_count}")
        print(f"   📊 Success rate: {100*success_count/reading_count:.1f}%" if reading_count > 0 else "   📊 Success rate: 0%")
        print(f"   ⏰ Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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
    print("🌤️  Weather Station Continuous Monitor for ThingsBoard")
    print("=" * 70)
    
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
    
    # Ask for monitoring interval
    try:
        print("📋 Choose monitoring interval:")
        print("   1. Every 5 minutes (frequent updates)")
        print("   2. Every 15 minutes (standard)")
        print("   3. Every 30 minutes (conservative)")
        print("   4. Every hour (minimal)")
        print("   5. Custom interval")
        
        choice = input("Enter choice (1-5): ").strip()
        
        interval_map = {
            "1": 5,
            "2": 15,
            "3": 30,
            "4": 60
        }
        
        if choice in interval_map:
            interval = interval_map[choice]
        elif choice == "5":
            interval = int(input("Enter custom interval in minutes: "))
            if interval < 1:
                raise ValueError("Interval must be at least 1 minute")
        else:
            print("⚠️  Invalid choice, using 15 minutes")
            interval = 15
        
        print()
        
        # Create and start monitor
        monitor = WeatherStationMonitor(access_token)
        monitor.monitor(interval_minutes=interval)
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Weather station monitoring complete!")
    print("📊 Check your ThingsBoard dashboard to view the meteorological data")

if __name__ == "__main__":
    main()
