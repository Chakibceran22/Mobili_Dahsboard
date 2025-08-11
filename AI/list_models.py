#!/usr/bin/env python3
"""
List Available Gemini Models
============================

This script lists all available models from Google's Generative AI API.
"""

import os
import google.generativeai as genai

def list_models():
    """List all available models"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable not set")
            return
        
        genai.configure(api_key=api_key)
        print("✅ Google Generative AI configured")
        
        print("\n📋 Available Models:")
        print("=" * 50)
        
        models = genai.list_models()
        for i, model in enumerate(models, 1):
            print(f"{i:2}. {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                methods = ', '.join(model.supported_generation_methods)
                print(f"    Methods: {methods}")
            print()
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
