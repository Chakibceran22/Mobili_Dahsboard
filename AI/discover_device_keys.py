#!/usr/bin/env python3
"""
Device Keys Discovery Tool
=========================

This script helps discover what telemetry keys are available for a specific device.
"""

import requests
import time
import json

def login_and_get_token(username="tenant@mobilis.dz", password="tenant", base_url="http://192.168.0.1:8081"):
    """Login and get JWT token for API calls"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']
    return None

def get_device_info(device_id, jwt_token, base_url="http://192.168.0.1:8081"):
    """Get device information"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{base_url}/api/device/{device_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_device_telemetry_keys(device_id, jwt_token, base_url="http://192.168.0.1:8081"):
    """Get available telemetry keys for a device"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    # Get telemetry keys
    response = requests.get(f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/keys/timeseries", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_latest_telemetry(device_id, jwt_token, keys, base_url="http://192.168.0.1:8081"):
    """Get latest telemetry values for specific keys"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    keys_param = ','.join(keys) if isinstance(keys, list) else keys
    response = requests.get(f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries", 
                          headers=headers, 
                          params={'keys': keys_param, 'limit': 5})
    if response.status_code == 200:
        return response.json()
    return {}

def discover_device_data(device_id):
    """Main function to discover device data"""
    print("🔍 ThingsBoard Device Data Discovery")
    print("=" * 50)
    print(f"📱 Device ID: {device_id}")
    print()
    
    # Step 1: Login
    print("🔐 Logging in...")
    jwt_token = login_and_get_token()
    if not jwt_token:
        print("❌ Failed to login")
        return
    print("✅ Login successful!")
    
    # Step 2: Get device info
    print("\n📋 Getting device information...")
    device_info = get_device_info(device_id, jwt_token)
    if device_info:
        print(f"✅ Device found: {device_info.get('name', 'Unknown')}")
        print(f"   Type: {device_info.get('type', 'Unknown')}")
        print(f"   Label: {device_info.get('label', 'No label')}")
    else:
        print("❌ Device not found")
        return
    
    # Step 3: Get available telemetry keys
    print("\n🔑 Discovering available telemetry keys...")
    telemetry_keys = get_device_telemetry_keys(device_id, jwt_token)
    
    if telemetry_keys:
        print(f"✅ Found {len(telemetry_keys)} telemetry keys:")
        for i, key in enumerate(telemetry_keys, 1):
            print(f"   {i}. {key}")
        
        # Step 4: Get sample data for each key
        print("\n📊 Getting sample data for each key...")
        latest_data = get_latest_telemetry(device_id, jwt_token, telemetry_keys)
        
        for key in telemetry_keys:
            if key in latest_data and latest_data[key]:
                sample_values = latest_data[key][:3]  # Show first 3 values
                print(f"\n🔸 {key}:")
                for i, point in enumerate(sample_values):
                    timestamp = point['ts']
                    value = point['value']
                    readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))
                    print(f"     {readable_time}: {value}")
            else:
                print(f"\n🔸 {key}: No recent data")
        
        # Step 5: Provide usage examples
        print("\n" + "=" * 50)
        print("💡 Usage Examples:")
        print(f"   # Fetch all available data:")
        all_keys = ','.join(telemetry_keys)
        print(f"   python3 fetch_battery_data.py {device_id} \"{all_keys}\"")
        print()
        for key in telemetry_keys[:3]:  # Show examples for first 3 keys
            print(f"   # Fetch {key} data:")
            print(f"   python3 fetch_battery_data.py {device_id} {key}")
            print(f"   python3 device_pipeline.py -d {device_id} -k {key}")
        
    else:
        print("❌ No telemetry keys found for this device")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 discover_device_keys.py <device_id>")
        print("Example: python3 discover_device_keys.py 031961d0-63de-11f0-90dc-991c5fc69833")
        sys.exit(1)
    
    device_id = sys.argv[1]
    discover_device_data(device_id)
