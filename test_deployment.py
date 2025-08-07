#!/usr/bin/env python3
"""
Test script for Railway deployment
Replace YOUR_APP_URL with your actual Railway app URL
"""

import requests
import json

# Replace with your actual Railway app URL
APP_URL = "https://your-app-name.railway.app"  # Replace this!

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{APP_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_api_docs():
    """Test if API docs are accessible"""
    try:
        response = requests.get(f"{APP_URL}/docs")
        print(f"✅ API Docs: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Docs Failed: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint structure"""
    try:
        response = requests.get(f"{APP_URL}/openapi.json")
        data = response.json()
        endpoints = [f"{method.upper()} {path}" for path, methods in data['paths'].items() for method in methods.keys()]
        print(f"✅ Available Endpoints:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        return True
    except Exception as e:
        print(f"❌ Endpoint Test Failed: {e}")
        return False

def main():
    print("🚀 Testing Railway Deployment")
    print("=" * 40)
    
    if not APP_URL or APP_URL == "https://your-app-name.railway.app":
        print("❌ Please update APP_URL in this script with your actual Railway app URL")
        return
    
    tests = [
        ("Health Check", test_health),
        ("API Documentation", test_api_docs),
        ("API Endpoints", test_upload_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is working correctly!")
        print(f"🌐 Your app is live at: {APP_URL}")
        print(f"📚 API docs at: {APP_URL}/docs")
    else:
        print("⚠️  Some tests failed. Check your deployment configuration.")

if __name__ == "__main__":
    main() 