#!/usr/bin/env python3
"""
Test client for the Device Pipeline Chatbot
"""

import requests
import json

# Configuration
CHATBOT_URL = "http://localhost:8003"

def test_pipeline_requests():
    """Test various pipeline execution requests"""
    print("🔧 Testing Pipeline Execution Requests")
    print("=" * 50)
    
    test_prompts = [
        "Run the device pipeline",
        "Fetch battery data and create a chart",
        "Get temperature data for the last 7 days",
        "Execute pipeline with bar chart",
        "Show humidity data",
        "Create a line chart of battery data",
        "Pull telemetry data and visualize it"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{CHATBOT_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=30
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
                    else:
                        print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_non_pipeline_requests():
    """Test non-pipeline requests"""
    print("\n🚫 Testing Non-Pipeline Requests")
    print("=" * 50)
    
    test_prompts = [
        "Hello, how are you?",
        "What's the weather like?",
        "Tell me a joke",
        "What is Python?",
        "How do I cook pasta?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
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

def test_health():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("-" * 25)
    
    try:
        response = requests.get(f"{CHATBOT_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"🔧 Pipeline Script Available: {data['pipeline_script_available']}")
            print(f"🤖 Service Type: {data['service_type']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def interactive_mode():
    """Interactive chat mode"""
    print("\n💬 Interactive Pipeline Chat Mode")
    print("Type 'quit' to exit")
    print("-" * 40)
    print("💡 Try these examples:")
    print("  • 'Run the device pipeline'")
    print("  • 'Get battery data for 3 days'")
    print("  • 'Create a bar chart of temperature'")
    print("  • 'Hello' (non-pipeline request)")
    
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
                timeout=60  # Longer timeout for pipeline execution
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Bot: {data['response']}")
                
                # Show additional details for pipeline requests
                if data['status'] == 'pipeline_executed' and 'pipeline_result' in data:
                    result = data['pipeline_result']
                    if result['success'] and 'details' in result:
                        print(f"📋 Details: {result['details']}")
                elif data['status'] == 'pipeline_failed' and 'pipeline_result' in data:
                    result = data['pipeline_result']
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Device Pipeline Chatbot Test Client")
    print("=" * 60)
    
    # Test health first
    test_health()
    
    # Test pipeline requests
    test_pipeline_requests()
    
    # Test non-pipeline requests
    test_non_pipeline_requests()
    
    # Ask if user wants interactive mode
    choice = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        interactive_mode()
    else:
        print("👋 Test complete!")
