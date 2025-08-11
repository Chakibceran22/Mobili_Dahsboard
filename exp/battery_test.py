"""
Battery Test Script for ThingsBoard
==================================

This script sends a few battery readings to an existing device in ThingsBoard.
You need the device's access token (see instructions below).

How to get your device access token:
1. Go to ThingsBoard dashboard (http://localhost:8081)
2. Login with: tenant@thingsboard.org / tenant
3. Go to Entities → Devices
4. Click on your device (e.g., "My Battery Sensor")
5. Click on "Manage credentials"
6. Copy the "Access token" value
"""

import requests
import time

def send_battery_test(access_token, base_url="http://localhost:8081"):
    """Send 10 battery readings to an existing device"""
    battery = 85  # Start at 85%
    for i in range(10):
        telemetry_data = {
            "batteryLevel": battery,
            "timestamp": int(time.time() * 1000)
        }
        response = requests.post(f"{base_url}/api/v1/{access_token}/telemetry", json=telemetry_data)
        if response.status_code == 200:
            print(f"📋 Reading {i+1}/10: Battery level {battery}% sent successfully")
        else:
            print(f"❌ Failed to send battery data: {response.text}")
        battery -= 5  # Decrease by 5% each time
        battery = max(0, battery)
        time.sleep(1)
    print("\n🎉 Test complete! Check your ThingsBoard dashboard.")

if __name__ == "__main__":
    print("🔋 ThingsBoard Battery Test")
    print("=" * 40)
    print("Change access token in batter.txt")
    access_token = None
    with open("exp/battery.txt", "r") as f:
        for line in f:
            if line.startswith("token="):
                access_token = line.strip().split("=", 1)[1]
                break
    if not access_token:
        print("❌ No access token provided. Exiting...")
    else:
        send_battery_test(access_token)
