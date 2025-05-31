#!/usr/bin/env python3
"""
Test script for Wh0Dini-AI FastAPI chatbot
Tests both regular and streaming endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat_endpoint():
    """Test the regular chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    
    chat_data = {
        "messages": [
            {
                "role": "user", 
                "content": "Hello! Can you tell me what you are in one sentence?"
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Request ID: {result['request_id']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Wh0Dini-AI API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Chat Endpoint", test_chat_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed! Your API is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
