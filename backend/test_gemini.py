#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""
import os
import sys
sys.path.append('.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def test_gemini():
    try:
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")
        
        if not api_key or api_key == "your_gemini_api_key_here":
            print("❌ Error: Gemini API key not configured")
            print("Please set GEMINI_API_KEY in your .env file")
            return False
        
        genai.configure(api_key=api_key)
        
        # List available models first
        print("📋 Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Try different model names (free tier compatible)
        model_names = ['gemini-1.5-flash-8b', 'gemini-flash-lite-latest', 'gemini-flash-latest', 'gemini-1.5-flash-latest']
        
        for model_name in model_names:
            try:
                print(f"🔄 Testing {model_name}...")
                text_model = genai.GenerativeModel(model_name)
                response = text_model.generate_content("Say hello in a friendly way")
                print(f"✅ {model_name} Response: {response.text}")
                return True, model_name
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)}")
                continue
        
        return False, None
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration...")
    success, working_model = test_gemini()
    if success:
        print(f"🎉 All tests passed! Gemini API is working correctly with model: {working_model}")
    else:
        print("💥 Tests failed. Please check your configuration.")