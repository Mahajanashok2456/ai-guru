#!/usr/bin/env python3
"""
Test script to verify FastAPI backend is working correctly
Run this to test if the backend can handle requests properly
"""

import requests
import json

def test_backend():
    """Test the FastAPI backend endpoints"""

    base_url = "http://127.0.0.1:8000"

    print("Testing FastAPI Backend")
    print("=" * 50)

    # Test 1: Health check
    try:
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return False

    # Test 2: Root endpoint
    try:
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Root endpoint failed: {e}")
        return False

    # Test 3: Simple test endpoint (no MongoDB/Gemini required)
    try:
        print("\n3. Testing simple test endpoint...")
        test_payload = {
            "question": "What is the Mahabharata about?"
        }

        print(f"   Sending: {json.dumps(test_payload, indent=2)}")

        response = requests.post(
            f"{base_url}/test",
            headers={"Content-Type": "application/json"},
            json=test_payload
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   Failed! Response: {response.text}")

    except Exception as e:
        print(f"   Test endpoint failed: {e}")
        return False

    # Test 4: Chat endpoint with correct format
    try:
        print("\n4. Testing chat endpoint with correct JSON format...")
        test_payload = {
            "question": "What is the Mahabharata about?"
        }

        print(f"   Sending: {json.dumps(test_payload, indent=2)}")

        response = requests.post(
            f"{base_url}/chat",
            headers={"Content-Type": "application/json"},
            json=test_payload
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   Failed! Response: {response.text}")

    except Exception as e:
        print(f"   Chat endpoint failed: {e}")
        return False

    # Test 5: Chat endpoint with wrong format (should fail)
    try:
        print("\n5. Testing chat endpoint with wrong JSON format...")
        wrong_payload = {
            "message": "This should fail"  # Wrong field name
        }

        print(f"   Sending: {json.dumps(wrong_payload, indent=2)}")

        response = requests.post(
            f"{base_url}/chat",
            headers={"Content-Type": "application/json"},
            json=wrong_payload
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 422:
            print("   Expected 422 error for wrong format!")
            print(f"   Response: {response.text}")
        else:
            print(f"   Unexpected response: {response.text}")

    except Exception as e:
        print(f"   Test failed: {e}")

    print("\n" + "=" * 50)
    print("Backend testing complete!")
    return True

if __name__ == "__main__":
    test_backend()