"""
DHT11 Test Script for ThingsBoard
================================

This script sends realistic temperature and humidity readings to a DHT11 device in ThingsBoard.
It simulates a real DHT11 sensor with realistic values and variations.

Prerequisites:
1. Run create_dht11_device.py first to create the device
2. The device token should be in exp/dht11.txt
"""

import requests
import time
import random
import math

def generate_realistic_dht11_data():
    """Generate realistic DHT11 temperature and humidity readings"""
    # DHT11 specifications:
    # Temperature: 0-50°C (±2°C accuracy)
    # Humidity: 20-90% RH (±5% accuracy)
    
    # Base values (simulating indoor conditions)
    base_temp = 22.0  # 22°C room temperature
    base_humidity = 45.0  # 45% humidity
    
    # Add some realistic variation
    temp_variation = random.uniform(-3, 3)  # ±3°C variation
    humidity_variation = random.uniform(-10, 10)  # ±10% variation
    
    # Add small sensor noise
    temp_noise = random.uniform(-0.5, 0.5)
    humidity_noise = random.uniform(-2, 2)
    
    temperature = base_temp + temp_variation + temp_noise
    humidity = base_humidity + humidity_variation + humidity_noise
    
    # Ensure values are within DHT11 range
    temperature = max(0, min(50, temperature))
    humidity = max(20, min(90, humidity))
    
    # Round to 1 decimal place (DHT11 precision)
    temperature = round(temperature, 1)
    humidity = round(humidity, 1)
    
    return temperature, humidity

def send_dht11_reading(access_token, temperature, humidity, base_url="http://localhost:8081"):
    """Send a single DHT11 reading to ThingsBoard"""
    telemetry_data = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": int(time.time() * 1000)
    }
    
    response = requests.post(f"{base_url}/api/v1/{access_token}/telemetry", json=telemetry_data)
    return response.status_code == 200, response

def simulate_dht11_sensor(access_token, readings_count=20, interval=2):
    """Simulate DHT11 sensor sending readings over time"""
    print(f"🌡️  Starting DHT11 simulation...")
    print(f"📊 Sending {readings_count} readings every {interval} seconds")
    print("=" * 60)
    
    for i in range(readings_count):
        temp, humidity = generate_realistic_dht11_data()
        
        success, response = send_dht11_reading(access_token, temp, humidity)
        
        if success:
            print(f"📋 Reading {i+1:2d}/{readings_count}: "
                  f"🌡️  {temp:5.1f}°C | 💧 {humidity:5.1f}% RH | ✅ Sent")
        else:
            print(f"📋 Reading {i+1:2d}/{readings_count}: "
                  f"🌡️  {temp:5.1f}°C | 💧 {humidity:5.1f}% RH | ❌ Failed")
            print(f"   Error: {response.text}")
        
        if i < readings_count - 1:  # Don't sleep after last reading
            time.sleep(interval)
    
    print("\n🎉 DHT11 simulation complete!")
    print("📊 Check your ThingsBoard dashboard to view the data")

def load_device_config():
    """Load device configuration from file"""
    try:
        config = {}
        with open("exp/dht11.txt", "r") as f:
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
    print("🌡️  DHT11 Sensor Test for ThingsBoard")
    print("=" * 50)
    
    # Load configuration
    access_token, device_id = load_device_config()
    
    if not access_token:
        print("❌ No DHT11 device configuration found!")
        print("📋 Please run: python exp/create_dht11_device.py first")
        return
    
    print(f"✅ Loaded DHT11 device configuration")
    print(f"🆔 Device ID: {device_id}")
    print(f"🔑 Token: {access_token[:8]}...")
    print()
    
    # Ask user for simulation parameters
    try:
        readings = 20
        
        interval = 2.0
        
        print()
        
    except ValueError:
        print("⚠️  Using default values: 20 readings, 2 second interval")
        readings = 20
        interval = 2.0
    
    # Start simulation
    simulate_dht11_sensor(access_token, readings, interval)

if __name__ == "__main__":
    main()
