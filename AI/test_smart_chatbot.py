#!/usr/bin/env python3
"""
Test client for the Smart AI Pipeline Chatbot
===========================================

Tests the new intelligent device selection capabilities.
"""

import requests
import json

# Configuration
CHATBOT_URL = "http://localhost:8003"

def test_smart_device_selection():
    """Test smart device selection with various prompts"""
    print("🧠 Testing Smart Device Selection")
    print("=" * 60)
    
    test_prompts = [
        # Device-specific requests
        "Show me temperature data from the DHT11 sensor",
        "Get battery levels from my battery sensor",
        "Display humidity readings for the last 5 days",
        
        # General requests that should auto-select
        "Show me battery data as a bar chart",
        "Get temperature readings for the past week",
        "Fetch humidity data and create a line chart",
        
        # Time-specific requests
        "Show device data for the last 3 days",
        "Get battery levels for the past 2 weeks",
        
        # Chart-specific requests
        "Create a bar chart of temperature data",
        "Generate line chart for humidity readings"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🔍 Test {i}: {prompt}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=60  # Longer timeout for device selection
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"🤖 Response: {data['response']}")
                
                if 'pipeline_result' in data:
                    result = data['pipeline_result']
                    if result['success']:
                        print(f"🎉 Pipeline executed successfully!")
                        if 'details' in result:
                            print(f"📋 Details: {result['details']}")
                        if 'params_used' in result:
                            params = result['params_used']
                            print(f"🔧 Parameters used:")
                            for key, value in params.items():
                                print(f"   {key}: {value}")
                    else:
                        print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
                        
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def test_edge_cases():
    """Test edge cases and ambiguous requests"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 40)
    
    edge_prompts = [
        "Show me data",  # Very vague
        "Get readings from device abc123",  # Non-existent device
        "Display temperature and humidity together",  # Multiple keys
        "Create visualization for battery and temperature",  # Multiple sensors
    ]
    
    for i, prompt in enumerate(edge_prompts, 1):
        print(f"\n📝 Edge Case {i}: {prompt}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"🤖 Response: {data['response'][:100]}...")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_non_pipeline_requests():
    """Test that non-pipeline requests still work"""
    print("\n🚫 Testing Non-Pipeline Requests")
    print("=" * 40)
    
    non_pipeline_prompts = [
        "Hello, how are you?",
        "What's the weather like?",
        "Tell me about Python programming",
        "How do I cook pasta?",
        "What is artificial intelligence?"
    ]
    
    for i, prompt in enumerate(non_pipeline_prompts, 1):
        print(f"\n📝 Non-Pipeline {i}: {prompt}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"🤖 Response: {data['response']}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_health_and_capabilities():
    """Test health endpoint and show capabilities"""
    print("\n🏥 Testing Health & Capabilities")
    print("-" * 35)
    
    try:
        # Test health
        response = requests.get(f"{CHATBOT_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"🔧 Pipeline Script: {data['pipeline_script_available']}")
            print(f"🔑 API Configured: {data['api_configured']}")
            print(f"🤖 Model Loaded: {data['model_loaded']}")
            print(f"🧠 Smart Selector: {data['smart_device_selector']}")
        
        # Test capabilities
        response = requests.get(f"{CHATBOT_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🎯 Service: {data['message']}")
            print(f"📋 Description: {data['description']}")
            print("\n🚀 Capabilities:")
            for capability, description in data['capabilities'].items():
                print(f"   • {capability}: {description}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_smart_mode():
    """Interactive chat mode showcasing smart selection"""
    print("\n💬 Interactive Smart Chat Mode")
    print("=" * 40)
    print("💡 Try these smart prompts:")
    print("  • 'Show me temperature data from DHT11'")
    print("  • 'Get battery levels for 3 days as bar chart'")
    print("  • 'Display humidity readings'")
    print("  • 'Create visualization for my sensors'")
    print("  • 'Hello' (non-pipeline)")
    print("\nType 'quit' to exit")
    print("-" * 40)
    
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
                timeout=60  # Longer timeout for smart selection
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Bot: {data['response']}")
                
                # Show smart selection details
                if data['status'] == 'pipeline_executed' and 'pipeline_result' in data:
                    result = data['pipeline_result']
                    if result['success']:
                        if 'params_used' in result and result['params_used']:
                            print(f"🧠 Smart Selection:")
                            params = result['params_used']
                            if 'device_id' in params:
                                print(f"   📱 Device: {params['device_id'][:12]}...")
                            if 'keys' in params:
                                print(f"   🔑 Data: {params['keys']}")
                            if 'chart_type' in params:
                                print(f"   📊 Chart: {params['chart_type']}")
                            if 'days_back' in params:
                                print(f"   📅 Time: {params['days_back']} days")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                        
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Smart AI Pipeline Chatbot Test Client")
    print("=" * 70)
    
    # Test all capabilities
    test_health_and_capabilities()
    test_smart_device_selection() 
    test_edge_cases()
    test_non_pipeline_requests()
    
    # Ask if user wants interactive mode
    choice = input("\n❓ Want to try interactive smart mode? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        interactive_smart_mode()
    else:
        print("👋 Test complete!")
