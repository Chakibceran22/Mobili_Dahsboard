#!/usr/bin/env python3
"""
Enhanced test client for the chatbot API with device pipeline and plotting tests
"""

import requests
import json
import time
import os

# Configuration
CHATBOT_URL = "http://localhost:8003"

# Test prompts for different plotting scenarios
PLOTTING_TEST_PROMPTS = [
    "Show me the battery level for the last 7 days",
    "Show me the temperature for the last 7 days",
    "Get battery data and create a line chart",
    "Fetch temperature data as a bar chart",
    "Display humidity data for the last 3 days",
    "Run the device pipeline with battery data",
    "Create a chart of DHT11 sensor data",
    "Show me device telemetry data"
]

def test_chatbot():
    """Test the chatbot with a simple prompt"""
    print("🤖 Testing Chatbot API")
    print("=" * 30)
    
    # Test prompt
    prompt = "Hello! Tell me a fun fact about space."
    
    print(f"📝 Sending prompt: {prompt}")
    
    try:
        # Send POST request to chatbot
        response = requests.post(
            f"{CHATBOT_URL}/chat",
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"🤖 Response: {data['response']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.ConnectionError:
        print("❌ Connection failed! Make sure the chatbot server is running:")
        print("   python chatbot_visualize.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("-" * 25)

    try:
        response = requests.get(f"{CHATBOT_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"🔑 API Configured: {data['api_configured']}")
            print(f"🤖 Model Loaded: {data['model_loaded']}")
            print(f"🧠 Smart Device Selector: {data.get('smart_device_selector', 'Unknown')}")
            print(f"📊 Pipeline Script: {data.get('pipeline_script_available', 'Unknown')}")
            return data['status'] == 'healthy'
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_plotting_functionality():
    """Test the plotting functionality with various prompts"""
    print("\n📊 Testing Plotting Functionality")
    print("=" * 40)

    success_count = 0
    total_tests = len(PLOTTING_TEST_PROMPTS)

    for i, prompt in enumerate(PLOTTING_TEST_PROMPTS, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {prompt}")
        print("-" * 50)

        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=60  # Longer timeout for pipeline execution
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')

                if status == 'pipeline_executed':
                    print(f"✅ SUCCESS: Pipeline executed")
                    print(f"   📱 Device: {data.get('smart_selector_info', {}).get('device_selected', 'Unknown')}")
                    print(f"   🎯 Confidence: {data.get('smart_selector_info', {}).get('confidence', 'Unknown')}")
                    print(f"   📊 Response: {data.get('response', 'No response')}")

                    # Check if plots were created
                    plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
                    if os.path.exists(plots_dir):
                        plot_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
                        if plot_files:
                            print(f"   📈 Plots created: {len(plot_files)} files")
                        else:
                            print(f"   ⚠️  No plot files found in plots/ directory")
                    else:
                        print(f"   ⚠️  Plots directory not found")

                    success_count += 1

                elif status == 'pipeline_failed':
                    print(f"❌ FAILED: Pipeline execution failed")
                    print(f"   Error: {data.get('pipeline_result', {}).get('error', 'Unknown error')}")

                elif status == 'parameter_extraction_failed':
                    print(f"⚠️  PARAMETER EXTRACTION FAILED")
                    print(f"   Details: {data.get('details', 'No details')}")

                else:
                    print(f"ℹ️  NON-PIPELINE RESPONSE: {data.get('response', 'No response')}")

            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except requests.Timeout:
            print(f"⏰ TIMEOUT: Request took too long (>60s)")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        # Small delay between tests
        time.sleep(1)

    print(f"\n📊 PLOTTING TEST SUMMARY")
    print("=" * 30)
    print(f"✅ Successful: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    print(f"📈 Success Rate: {(success_count/total_tests)*100:.1f}%")

    return success_count, total_tests

def test_smart_device_selection():
    """Test smart device selection with specific scenarios"""
    print("\n🧠 Testing Smart Device Selection")
    print("=" * 40)

    test_cases = [
        {
            "prompt": "Show me the battery level for the last 7 days",
            "expected_device": "battery",
            "expected_keys": "batteryLevel",
            "expected_days": 7
        },
        {
            "prompt": "Show me the temperature for the last 7 days",
            "expected_device": "DHT11 Sensor",
            "expected_keys": "temperature",
            "expected_days": 7
        },
        {
            "prompt": "Get humidity data as a bar chart",
            "expected_device": "DHT11 Sensor",
            "expected_keys": "humidity",
            "expected_chart": "bar"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Smart Selection Test {i}: {test_case['prompt']}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": test_case['prompt']},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                smart_info = data.get('smart_selector_info', {})
                params = smart_info.get('parameters_extracted', {})

                print(f"📱 Selected Device: {smart_info.get('device_selected', 'Unknown')}")
                print(f"🎯 Confidence: {smart_info.get('confidence', 'Unknown')}")
                print(f"🔑 Keys: {params.get('keys', 'Unknown')}")
                print(f"📊 Chart Type: {params.get('chart_type', 'Unknown')}")
                print(f"📅 Time Range: {params.get('time_range', 'Unknown')}")

                # Validate expectations
                validations = []
                if 'expected_device' in test_case:
                    device_match = test_case['expected_device'].lower() in smart_info.get('device_selected', '').lower()
                    validations.append(("Device", device_match))

                if 'expected_keys' in test_case:
                    keys_match = test_case['expected_keys'] in params.get('keys', '')
                    validations.append(("Keys", keys_match))

                if 'expected_days' in test_case:
                    # Check if the time range contains the expected days
                    time_range_str = params.get('time_range', '')
                    days_match = str(test_case['expected_days']) in str(time_range_str)
                    validations.append(("Time Range", days_match))

                if 'expected_chart' in test_case:
                    chart_match = test_case['expected_chart'] == params.get('chart_type', '')
                    validations.append(("Chart", chart_match))

                print("🔍 Validation Results:")
                for validation_name, is_valid in validations:
                    status = "✅" if is_valid else "❌"
                    print(f"   {status} {validation_name}: {'PASS' if is_valid else 'FAIL'}")

            else:
                print(f"❌ HTTP ERROR: {response.status_code}")

        except Exception as e:
            print(f"❌ ERROR: {e}")

def interactive_mode():
    """Interactive chat mode"""
    print("\n💬 Interactive Chat Mode")
    print("Type 'quit' to exit")
    print("-" * 25)
    
    while True:
        prompt = input("\n👤 You: ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not prompt:
            continue
            
        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Bot: {data['response']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_all_tests():
    """Run all available tests"""
    print("🚀 Running All Tests")
    print("=" * 40)

    # Health check first
    if not test_health():
        print("❌ Health check failed - some tests may not work properly")

    # Basic chatbot test
    test_chatbot()

    # Smart device selection tests
    test_smart_device_selection()

    # Plotting functionality tests
    success_count, total_tests = test_plotting_functionality()

    print(f"\n🎯 OVERALL TEST SUMMARY")
    print("=" * 30)
    print(f"📊 Plotting Tests: {success_count}/{total_tests} passed")
    print("✅ All tests completed!")

if __name__ == "__main__":
    print("🚀 Enhanced Chatbot Test Client")
    print("=" * 50)
    print("This client can test:")
    print("  📊 Device pipeline and plotting functionality")
    print("  🧠 Smart device selection")
    print("  🏥 Health checks")
    print("  💬 Interactive chat")
    print()

    # Menu options
    print("Choose test mode:")
    print("1. Run all tests (recommended)")
    print("2. Test plotting functionality only")
    print("3. Test smart device selection only")
    print("4. Basic health and chat test")
    print("5. Interactive chat mode")
    print("6. Exit")

    choice = input("\n❓ Enter your choice (1-6): ").strip()

    if choice == "1":
        run_all_tests()
    elif choice == "2":
        test_health()
        test_plotting_functionality()
    elif choice == "3":
        test_health()
        test_smart_device_selection()
    elif choice == "4":
        test_health()
        test_chatbot()
    elif choice == "5":
        test_health()
        interactive_mode()
    elif choice == "6":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Running all tests...")
        run_all_tests()

    print("\n👋 Test session complete!")