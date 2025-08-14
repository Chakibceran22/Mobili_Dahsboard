#!/usr/bin/env python3
"""
Simple Device Selector Test (No AI)
==================================

Test device fetching without AI dependency to debug the device ID issue.
"""

import requests
import json
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from list_devices.py
try:
    from list_devices import login_and_get_token, list_all_devices, get_device_telemetry_keys
    print("✅ Successfully imported functions from list_devices.py")
except ImportError as e:
    print(f"❌ Could not import from list_devices.py: {e}")
    exit(1)

def test_device_fetching():
    """Test device fetching to see what we get"""
    print("🧪 Testing Device Fetching")
    print("=" * 40)
    
    # Step 1: Login
    print("🔐 Logging in...")
    jwt_token = login_and_get_token()
    if not jwt_token:
        print("❌ Failed to login")
        return
    print("✅ Login successful")
    
    # Step 2: Get devices
    print("📱 Fetching devices...")
    devices = list_all_devices(jwt_token)
    if not devices:
        print("❌ No devices found")
        return
    
    print(f"✅ Found {len(devices)} devices")
    
    # Step 3: Show detailed device info
    for i, device in enumerate(devices, 1):
        device_id = device['id']['id']
        device_name = device.get('name', 'Unknown')
        device_type = device.get('type', 'Unknown')
        
        print(f"\n🔍 Device #{i}")
        print(f"   📛 Name: {device_name}")
        print(f"   🆔 Full ID: {device_id}")
        print(f"   📋 Type: {device_type}")
        print(f"   🔍 ID Length: {len(device_id)} characters")
        
        # Get telemetry keys
        try:
            keys = get_device_telemetry_keys(device_id, jwt_token)
            if keys:
                print(f"   🔑 Keys: {', '.join(keys)}")
            else:
                print(f"   🔑 Keys: None found")
        except Exception as e:
            print(f"   ❌ Error getting keys: {e}")
        
        print("-" * 50)

def test_manual_selection():
    """Test manual device selection like AI would do"""
    print("\n🎯 Testing Manual Selection")
    print("=" * 40)
    
    # Get devices
    jwt_token = login_and_get_token()
    devices = list_all_devices(jwt_token)
    
    if not devices:
        print("❌ No devices available for testing")
        return
    
    # Try to select first device manually
    first_device = devices[0]
    device_id = first_device['id']['id']
    device_name = first_device.get('name', 'Unknown')
    
    print(f"🎯 Manually selecting first device:")
    print(f"   📛 Name: {device_name}")
    print(f"   🆔 ID: {device_id}")
    
    # Simulate what the validation code does
    print(f"\n🔍 Validation test:")
    print(f"   Looking for ID: {device_id}")
    
    found = False
    for device in devices:
        if device['id']['id'] == device_id:
            found = True
            print(f"   ✅ FOUND: {device.get('name')}")
            break
    
    if not found:
        print(f"   ❌ NOT FOUND!")
    
    return device_id, device_name

if __name__ == "__main__":
    print("🚀 Device Selector Debug Test")
    print("=" * 50)
    
    test_device_fetching()
    test_manual_selection()
    
    print("\n✅ Debug test complete!")
