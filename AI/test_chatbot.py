#!/usr/bin/env python3
"""
Simple test client for the chatbot API
"""

import requests
import json

# Configuration
CHATBOT_URL = "http://localhost:8003"

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
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

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

if __name__ == "__main__":
    print("🚀 Chatbot Test Client")
    print("=" * 40)
    
    # Run tests
    test_health()
    test_chatbot()
    
    # Ask if user wants interactive mode
    choice = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        interactive_mode()
    else:
        print("👋 Test complete!")