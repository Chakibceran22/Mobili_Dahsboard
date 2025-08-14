"""
Smart Device Selector for ThingsBoard
====================================

This script uses AI to intelligently select devices and telemetry keys based on natural language prompts.
It fetches available devices and matches them to user requests.
"""

import requests
import json
import os
import sys
import google.generativeai as genai

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from list_devices.py
try:
    from list_devices import login_and_get_token, list_all_devices, get_device_telemetry_keys
    print("✅ Successfully imported functions from list_devices.py")
except ImportError as e:
    print(f"❌ Could not import from list_devices.py: {e}")
    # Fallback functions will be defined below
    login_and_get_token = None
    list_all_devices = None
    get_device_telemetry_keys = None

def get_all_devices_with_keys_from_list_devices(base_url="http://localhost:8081"):
    """Use list_devices.py functions to get all devices with their telemetry keys"""
    if not all([login_and_get_token, list_all_devices, get_device_telemetry_keys]):
        print("❌ list_devices.py functions not available - using fallback")
        return get_all_devices_with_keys_fallback(base_url)
    
    try:
        # Step 1: Login using list_devices function
        print("🔐 Logging in using list_devices.py...")
        jwt_token = login_and_get_token()
        if not jwt_token:
            print("❌ Failed to login via list_devices.py")
            return []
        
        # Step 2: Get all devices using list_devices function
        print("📱 Fetching devices using list_devices.py...")
        devices = list_all_devices(jwt_token, base_url)
        if not devices:
            print("❌ No devices found via list_devices.py")
            return []
        
        print(f"✅ Found {len(devices)} devices via list_devices.py")
        
        # Step 3: Get telemetry keys for each device
        devices_with_keys = []
        for device in devices:
            device_id = device['id']['id']
            device_info = {
                'id': device_id,
                'name': device.get('name', 'Unknown'),
                'type': device.get('type', 'Unknown'),
                'label': device.get('label', ''),
                'keys': []
            }
            
            # Get telemetry keys using list_devices function
            try:
                telemetry_keys = get_device_telemetry_keys(device_id, jwt_token, base_url)
                device_info['keys'] = telemetry_keys if telemetry_keys else []
            except Exception as e:
                print(f"⚠️  Could not get keys for device {device_info['name']}: {e}")
                device_info['keys'] = []
            
            devices_with_keys.append(device_info)
        
        print(f"✅ Successfully processed {len(devices_with_keys)} devices with telemetry keys")
        return devices_with_keys
        
    except Exception as e:
        print(f"❌ Error using list_devices.py functions: {e}")
        print("🔄 Falling back to direct implementation...")
        return get_all_devices_with_keys_fallback(base_url)

def get_all_devices_with_keys_fallback(base_url="http://localhost:8081"):
    """Fallback implementation if list_devices.py is not available"""
    print("⚠️  Using fallback device fetching method")
    
    # Simple login for fallback
    login_data = {"username": "tenant@thingsboard.org", "password": "tenant"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        return []
    
    jwt_token = response.json()['token']
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    # Get devices
    url = f"{base_url}/api/tenant/devices"
    params = {'pageSize': 100, 'page': 0}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return []
    
    devices = response.json().get('data', [])
    devices_with_keys = []
    
    for device in devices:
        device_id = device['id']['id']
        device_info = {
            'id': device_id,
            'name': device.get('name', 'Unknown'),
            'type': device.get('type', 'Unknown'),
            'label': device.get('label', ''),
            'keys': []
        }
        
        # Get telemetry keys
        keys_url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/keys/timeseries"
        keys_response = requests.get(keys_url, headers=headers)
        
        if keys_response.status_code == 200:
            device_info['keys'] = keys_response.json()
        
        devices_with_keys.append(device_info)
    
    return devices_with_keys

def ai_select_device_and_params(prompt, devices_list, model):
    """Use AI to select the best device and parameters based on the prompt"""
    if not model:
        return None
    
    # Create a summary of available devices for the AI
    devices_summary = []
    for device in devices_list:
        summary = f"Device: '{device['name']}' (Type: {device['type']}, Full_ID: {device['id']}, Keys: {', '.join(device['keys'])})"
        devices_summary.append(summary)
    
    devices_text = "\n".join(devices_summary)
    
    analysis_prompt = f"""
You are an intelligent device selector for an IoT dashboard. Based on the user's request, select the most appropriate device and parameters.

Available devices:
{devices_text}

User request: "{prompt}"

Your task:
1. Select the most appropriate device based on the request
2. Choose the best telemetry key(s) from that device
3. Determine the chart type (line or bar)
4. Extract any time range if mentioned

Respond with ONLY a JSON object in this format:
{{
    "device_id": "FULL_DEVICE_ID_EXACTLY_AS_SHOWN",
    "device_name": "device_name_here", 
    "keys": "telemetry_key_or_comma_separated_keys",
    "chart_type": "line_or_bar",
    "days_back": number_or_null,
    "confidence": "high_medium_low",
    "reasoning": "brief_explanation"
}}

IMPORTANT: Use the EXACT Full_ID from the device list above. Do not abbreviate or modify the device_id.

Selection rules:
- For temperature requests, prefer devices with "temperature" keys
- For humidity requests, prefer devices with "humidity" keys  
- For battery requests, prefer devices with "battery" or "batteryLevel" keys
- For general "data" requests, use the first available device
- Default chart type is "line" unless specifically requested
- Only include days_back if time range is mentioned

JSON Response:"""

    try:
        response = model.generate_content(analysis_prompt)
        result_text = response.text.strip()
        
        # Clean up the response
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        selection = json.loads(result_text)
        print(f"🤖 AI Selection: {selection.get('device_name')} - {selection.get('keys')} ({selection.get('confidence')} confidence)")
        print(f"💭 Reasoning: {selection.get('reasoning')}")
        print(f"🆔 Selected Device ID: {selection.get('device_id')}")
        
        return selection
        
    except json.JSONDecodeError as e:
        print(f"❌ Could not parse AI response as JSON: {e}")
        print(f"Raw response: {result_text}")
        return None
    except Exception as e:
        print(f"❌ Error in AI device selection: {e}")
        return None

def smart_device_selection(prompt):
    """Main function to intelligently select device and parameters"""
    print("🧠 Smart Device Selection")
    print("=" * 40)
    print(f"📝 Prompt: {prompt}")
    print()
    
    # Initialize AI model
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set - using fallback selection")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        print(f"❌ Could not initialize AI model: {e}")
        return None
    
    # Step 1: Get all devices with keys using list_devices.py functions
    print("� Fetching available devices using list_devices.py...")
    devices = get_all_devices_with_keys_from_list_devices()
    if not devices:
        print("❌ No devices found")
        return None
    print(f"✅ Found {len(devices)} devices")
    
    # Show what devices were found
    print("� Available devices:")
    for i, device in enumerate(devices, 1):
        keys_str = ", ".join(device['keys']) if device['keys'] else "No keys"
        print(f"   {i}. {device['name']} ({device['type']}) - Keys: {keys_str}")
    
    # Step 2: Use AI to select device and parameters
    print("\n🤖 Analyzing prompt with AI...")
    selection = ai_select_device_and_params(prompt, devices, model)
    
    if not selection:
        print("❌ Could not select device automatically")
        return None
    
    # Step 3: Validate selection
    print(f"🔍 Validating AI selection...")
    print(f"   AI selected device ID: {selection['device_id']}")
    
    selected_device = None
    print("🔍 Checking against available devices:")
    for i, device in enumerate(devices, 1):
        print(f"   {i}. {device['name']} - ID: {device['id']}")
        if device['id'] == selection['device_id']:
            selected_device = device
            print(f"   ✅ MATCH FOUND!")
            break
    
    if not selected_device:
        print("❌ Selected device not found in available devices")
        print(f"   🔍 AI selected: {selection['device_id']}")
        print(f"   📋 Available device IDs:")
        for device in devices:
            print(f"      • {device['id']}")
        return None
    
    # Validate keys
    requested_keys = selection['keys'].split(',')
    available_keys = selected_device['keys']
    valid_keys = [key.strip() for key in requested_keys if key.strip() in available_keys]
    
    if not valid_keys:
        print("❌ Selected keys not available on device")
        print(f"   Requested: {selection['keys']}")
        print(f"   Available: {', '.join(available_keys)}")
        return None
    
    final_selection = {
        'device_id': selection['device_id'],
        'device_name': selection['device_name'],
        'keys': ','.join(valid_keys),
        'chart_type': selection.get('chart_type', 'line'),
        'days_back': selection.get('days_back'),
        'confidence': selection.get('confidence', 'medium')
    }
    
    print("✅ Device selection successful!")
    print(f"📱 Selected: {final_selection['device_name']}")
    print(f"🆔 Device ID: {final_selection['device_id']}")
    print(f"🔑 Keys: {final_selection['keys']}")
    print(f"📊 Chart: {final_selection['chart_type']}")
    if final_selection['days_back']:
        print(f"📅 Time range: Last {final_selection['days_back']} days")
    
    return final_selection

if __name__ == "__main__":
    # Test the function
    if len(sys.argv) > 1:
        test_prompt = " ".join(sys.argv[1:])
    else:
        test_prompt = "Show me the temperature for the last 7 days"
    
    result = smart_device_selection(test_prompt)
    if result:
        print("\n🎯 Final Parameters:")
        print(json.dumps(result, indent=2))
