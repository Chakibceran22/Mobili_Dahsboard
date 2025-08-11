#!/usr/bin/env python3
"""
Simple Chatbot with GenAI
=========================

A minimal chatbot that uses Google Generative AI to respond to prompts.
Runs on port 8003 and accepts POST requests with prompts.
"""

import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
# You need to set your API key as an environment variable
# export GOOGLE_API_KEY="your_api_key_here"
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key_here'")
    else:
        genai.configure(api_key=api_key)
        print("✅ Google Generative AI configured successfully")
except Exception as e:
    print(f"❌ Error configuring Google Generative AI: {e}")

# Initialize the model
try:
    # Use Gemini Flash model (fastest and most reliable)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    print("✅ models/gemini-1.5-flash model loaded successfully")
except Exception as e:
    print(f"❌ Error loading Gemini Flash model: {e}")
    model = None

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Simple Chatbot with GenAI",
        "status": "running",
        "port": 8003,
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
            "info": "/ (GET)"
        },
        "usage": {
            "method": "POST",
            "url": "http://localhost:8003/chat",
            "body": {
                "prompt": "Your question or message here"
            }
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    api_configured = os.getenv('GOOGLE_API_KEY') is not None
    model_loaded = model is not None
    
    return jsonify({
        "status": "healthy" if api_configured and model_loaded else "unhealthy",
        "api_configured": api_configured,
        "model_loaded": model_loaded,
        "timestamp": "2025-07-29"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint that accepts prompts and returns AI responses"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing 'prompt' in request body",
                "example": {
                    "prompt": "Hello, how are you?"
                }
            }), 400
        
        user_prompt = data['prompt']
        
        if not user_prompt.strip():
            return jsonify({
                "error": "Prompt cannot be empty"
            }), 400
        
        # Check if model is available
        if not model:
            return jsonify({
                "error": "AI model not available. Check GOOGLE_API_KEY configuration.",
                "user_prompt": user_prompt,
                "response": "Sorry, I'm not configured properly. Please check the API key."
            }), 500
        
        print(f"💬 Received prompt: {user_prompt[:100]}...")
        
        # Generate response using Gemini
        try:
            response = model.generate_content(user_prompt)
            ai_response = response.text
            print(f"🤖 Generated response: {ai_response[:100]}...")
            
            return jsonify({
                "status": "success",
                "user_prompt": user_prompt,
                "response": ai_response,
                "model": "models/gemini-1.5-flash"
            })
            
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            return jsonify({
                "error": f"Failed to generate AI response: {str(e)}",
                "user_prompt": user_prompt,
                "response": "Sorry, I encountered an error while processing your request."
            }), 500
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to quickly check if the chatbot is working"""
    test_prompt = "Hello! Can you tell me what you are?"
    
    if not model:
        return jsonify({
            "error": "AI model not available",
            "test_prompt": test_prompt,
            "response": "Model not configured"
        })
    
    try:
        response = model.generate_content(test_prompt)
        return jsonify({
            "status": "test_successful",
            "test_prompt": test_prompt,
            "response": response.text,
            "model": "models/gemini-1.5-flash"
        })
    except Exception as e:
        return jsonify({
            "error": f"Test failed: {str(e)}",
            "test_prompt": test_prompt
        })

def main():
    """Main function to start the chatbot server"""
    print("🤖 Starting Simple Chatbot with GenAI")
    print("=" * 50)
    print("📡 Server will run on: http://localhost:8003")
    print("💬 Chat endpoint: http://localhost:8003/chat")
    print("🔍 Health check: http://localhost:8003/health")
    print("🧪 Test endpoint: http://localhost:8003/test")
    print()
    print("📝 Example curl command:")
    print('curl -X POST http://localhost:8003/chat \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"prompt": "Hello, how are you?"}\'')
    print()
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  WARNING: GOOGLE_API_KEY not set!")
        print("   To set it: export GOOGLE_API_KEY='your_api_key_here'")
        print("   The chatbot will not work without it.")
    
    print("🚀 Starting server...")
    
    try:
        app.run(host='0.0.0.0', port=8003, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Chatbot server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
