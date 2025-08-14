"""
DHT11 Device Creator for ThingsBoard
===================================

This script creates a DHT11 temperature and humidity sensor device in ThingsBoard.
It will create the device and return the access token for testing.

Prerequisites:
1. ThingsBoard running on localhost:8081
2. Login credentials: tenant@thingsboard.org / tenant
"""

import requests
import json

def get_auth_token(username="tenant@thingsboard.org", password="tenant", base_url="http://localhost:8081"):
    """Get authentication token from ThingsBoard"""
    auth_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=auth_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def create_dht11_device(auth_token, base_url="http://localhost:8081"):
    """Create a DHT11 device in ThingsBoard"""
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {auth_token}"
    }
    
    device_data = {
        "name": "DHT11 Sensor",
        "type": "DHT11",
        "label": "Temperature & Humidity Sensor",
        "additionalInfo": {
            "description": "DHT11 digital temperature and humidity sensor",
            "sensorType": "DHT11",
            "measurements": ["temperature", "humidity"],
            "location": "Lab Room A"
        }
    }
    
    response = requests.post(f"{base_url}/api/device", json=device_data, headers=headers)
    
    if response.status_code == 200:
        device = response.json()
        device_id = device['id']['id']
        print(f"✅ DHT11 device created successfully!")
        print(f"📱 Device Name: {device['name']}")
        print(f"🆔 Device ID: {device_id}")
        return device_id
    else:
        print(f"❌ Failed to create device: {response.status_code} - {response.text}")
        return None

def get_device_credentials(device_id, auth_token, base_url="http://localhost:8081"):
    """Get device credentials (access token)"""
    headers = {
        "X-Authorization": f"Bearer {auth_token}"
    }
    
    response = requests.get(f"{base_url}/api/device/{device_id}/credentials", headers=headers)
    
    if response.status_code == 200:
        credentials = response.json()
        access_token = credentials.get('credentialsId')
        print(f"🔑 Access Token: {access_token}")
        return access_token
    else:
        print(f"❌ Failed to get credentials: {response.status_code} - {response.text}")
        return None

def save_token_to_file(access_token, device_id):
    """Save the access token to a file for testing"""
    with open("exp/dht11.txt", "w") as f:
        f.write(f"# DHT11 Device Configuration\n")
        f.write(f"device_id={device_id}\n")
        f.write(f"token={access_token}\n")
        f.write(f"# Use this token in test_dht11.py\n")
    
    print(f"💾 Configuration saved to exp/dht11.txt")

def main():
    print("🌡️  DHT11 Device Creator for ThingsBoard")
    print("=" * 50)
    
    # Step 1: Authenticate
    print("\nStep 1: Authenticating with ThingsBoard...")
    auth_token = get_auth_token()
    if not auth_token:
        return
    
    # Step 2: Create device
    print("\nStep 2: Creating DHT11 device...")
    device_id = create_dht11_device(auth_token)
    if not device_id:
        return
    
    # Step 3: Get credentials
    print("\nStep 3: Getting device credentials...")
    access_token = get_device_credentials(device_id, auth_token)
    if not access_token:
        return
    
    # Step 4: Save to file
    print("\nStep 4: Saving configuration...")
    save_token_to_file(access_token, device_id)
    
    print("\n🎉 DHT11 device setup complete!")
    print("📋 Next steps:")
    print("   1. Check your ThingsBoard dashboard")
    print("   2. Run: python exp/test_dht11.py")
    print("   3. View telemetry data in the dashboard")

if __name__ == "__main__":
    main()
