#!/usr/bin/env python3
"""
ThingsBoard Battery Device Creator
=================================

This script creates a battery device in ThingsBoard and saves its access token
for use with the battery test script.
"""

import requests
import json
import sys
import os

def login_and_get_token(username="tenant@mobilis.dz", password="tenant", base_url="http://192.168.0.1:8081"):
    """Login and get JWT token for API calls"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']
    return None

def create_battery_device(jwt_token, base_url="http://192.168.0.1:8081"):
    """Create a battery device in ThingsBoard"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    # Device data
    device_data = {
        "name": "Battery Sensor Test",
        "type": "Battery Sensor",
        "label": "Test Battery Device for AI Pipeline",
        "additionalInfo": {
            "description": "Battery sensor device for testing AI pipeline functionality"
        }
    }
    
    # Create the device
    response = requests.post(f"{base_url}/api/device", headers=headers, json=device_data)
    
    if response.status_code == 200:
        device = response.json()
        device_id = device['id']['id']
        print(f"✅ Device created successfully!")
        print(f"   📱 Name: {device['name']}")
        print(f"   🆔 Device ID: {device_id}")
        return device_id
    else:
        print(f"❌ Failed to create device: {response.status_code} - {response.text}")
        return None

def get_device_credentials(device_id, jwt_token, base_url="http://192.168.0.1:8081"):
    """Get device credentials (access token)"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{base_url}/api/device/{device_id}/credentials", headers=headers)
    
    if response.status_code == 200:
        credentials = response.json()
        access_token = credentials.get('credentialsId')
        print(f"✅ Device credentials retrieved!")
        print(f"   🔑 Access Token: {access_token}")
        return access_token
    else:
        print(f"❌ Failed to get credentials: {response.status_code} - {response.text}")
        return None

def save_token_to_file(access_token, device_id):
    """Save the access token to battery.txt file"""
    # Create exp directory if it doesn't exist
    os.makedirs("exp", exist_ok=True)
    
    # Save token to file
    with open("exp/battery.txt", "w") as f:
        f.write(f"# Battery Device Credentials\n")
        f.write(f"# Device ID: {device_id}\n")
        f.write(f"# Created: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"token={access_token}\n")
    
    print(f"✅ Token saved to exp/battery.txt")

def main():
    """Main function - create battery device and save credentials"""
    print("🔋 ThingsBoard Battery Device Creator")
    print("=" * 50)
    
    # Step 1: Login
    print("🔐 Logging in to ThingsBoard...")
    jwt_token = login_and_get_token()
    if not jwt_token:
        print("❌ Failed to login. Check ThingsBoard is running and credentials are correct.")
        return
    print("✅ Login successful!")
    
    # Step 2: Create device
    print("\n📱 Creating battery device...")
    device_id = create_battery_device(jwt_token)
    if not device_id:
        print("❌ Failed to create device.")
        return
    
    # Step 3: Get credentials
    print("\n🔑 Getting device credentials...")
    access_token = get_device_credentials(device_id, jwt_token)
    if not access_token:
        print("❌ Failed to get device credentials.")
        return
    
    # Step 4: Save to file
    print("\n💾 Saving credentials...")
    save_token_to_file(access_token, device_id)
    
    print("\n🎉 Battery device setup complete!")
    print("=" * 50)
    print("✅ Device created and credentials saved")
    print("📋 You can now run the battery test script:")
    print("   python3 exp/battery_test.py")
    print("")
    print("🌐 View your device in ThingsBoard:")
    print("   http://192.168.0.1:8081")
    print("   Login: tenant@mobilis.dz / tenant")
    print("   Go to: Entities → Devices → Battery Sensor Test")

if __name__ == "__main__":
    main()
