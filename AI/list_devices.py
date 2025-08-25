"""
ThingsBoard Device Lister
=========================

This script lists all devices in your ThingsBoard tenant to help you find the correct device IDs.
"""

import requests
import json

def login_and_get_token(username="tenant@mobilis.dz", password="tenant", base_url="http://192.168.0.1:8081"):
    """Login and get JWT token for API calls"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']
    return None

def list_all_devices(jwt_token, base_url="http://192.168.0.1:8081"):
    """List all devices in the tenant"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    # Get tenant devices with pagination
    page_size = 100
    page = 0
    all_devices = []
    
    while True:
        url = f"{base_url}/api/tenant/devices"
        params = {
            'pageSize': page_size,
            'page': page,
            'sortProperty': 'name',
            'sortOrder': 'ASC'
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Failed to fetch devices: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        devices = data.get('data', [])
        all_devices.extend(devices)
        
        # Check if we have more pages
        if not data.get('hasNext', False):
            break
        page += 1
    
    return all_devices

def get_device_telemetry_keys(device_id, jwt_token, base_url="http://192.168.0.1:8081"):
    """Get available telemetry keys for a device"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/keys/timeseries"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return []

def main():
    """Main function - list all devices and their telemetry keys"""
    print("📱 ThingsBoard Device Lister")
    print("=" * 50)
    
    # Step 1: Login
    print("🔐 Logging in...")
    jwt_token = login_and_get_token()
    if not jwt_token:
        print("❌ Failed to login. Check ThingsBoard is running and credentials are correct.")
        return
    print("✅ Login successful!")
    
    # Step 2: List devices
    print("\n📋 Fetching all devices...")
    devices = list_all_devices(jwt_token)
    
    if not devices:
        print("❌ No devices found in this tenant.")
        return
    
    print(f"✅ Found {len(devices)} devices:")
    print("\n" + "=" * 80)
    
    for i, device in enumerate(devices, 1):
        device_id = device['id']['id']
        device_name = device.get('name', 'Unknown')
        device_type = device.get('type', 'Unknown')
        device_label = device.get('label', '')
        
        print(f"\n🔍 Device #{i}")
        print(f"   📛 Name: {device_name}")
        print(f"   🆔 ID: {device_id}")
        print(f"   📋 Type: {device_type}")
        if device_label:
            print(f"   🏷️  Label: {device_label}")
        
        # Get telemetry keys for this device
        print("   🔑 Available telemetry keys:", end=" ")
        try:
            telemetry_keys = get_device_telemetry_keys(device_id, jwt_token)
            if telemetry_keys:
                print(", ".join(telemetry_keys))
                
                # If this device has battery data, highlight it
                if any("battery" in key.lower() for key in telemetry_keys):
                    print("   🔋 *** This device has battery data! ***")
            else:
                print("None found")
        except Exception as e:
            print(f"Error fetching keys: {e}")
        
        print("-" * 60)
    
    print(f"\n🎯 To use any of these devices, copy the ID and use it like:")
    print("python fetch_battery_data.py <DEVICE_ID> <TELEMETRY_KEY>")
    print("\nExample for battery data:")
    if devices:
        example_device = devices[0]['id']['id']
        print(f"python fetch_battery_data.py {example_device} batteryLevel")

if __name__ == "__main__":
    main()
