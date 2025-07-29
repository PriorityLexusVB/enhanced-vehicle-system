#!/usr/bin/env python3

import requests
import json

def test_basic_endpoints():
    base_url = "http://localhost:3000"
    
    print("🚀 Testing Basic API Endpoints...")
    print("=" * 50)
    
    # Test VIN Decode (doesn't require Google Vision)
    print("\n🔍 Testing VIN Decode API...")
    try:
        response = requests.post(f"{base_url}/api/vin-decode", 
                               json={"vin": "1HGBH41JXMN109186"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VIN Decode working - Vehicle: {data['vehicle']['make']} {data['vehicle']['model']} {data['vehicle']['year']}")
        else:
            print(f"❌ VIN Decode failed: {response.text}")
    except Exception as e:
        print(f"❌ VIN Decode error: {e}")
    
    # Test Admin endpoints
    print("\n🔍 Testing Admin Get Users...")
    try:
        response = requests.get(f"{base_url}/api/admin/users")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin Get Users working - Found {len(data.get('users', []))} users")
        else:
            print(f"❌ Admin Get Users failed: {response.text}")
    except Exception as e:
        print(f"❌ Admin Get Users error: {e}")
    
    # Test OCR endpoints (will likely fail due to Google Vision API)
    print("\n🔍 Testing OCR Endpoints (expected to fail due to Google Vision API)...")
    
    ocr_endpoints = [
        "api/ocr-vin",
        "api/ocr-license-plate", 
        "api/ocr-mileage"
    ]
    
    for endpoint in ocr_endpoints:
        try:
            response = requests.post(f"{base_url}/{endpoint}")
            print(f"{endpoint}: Status {response.status_code}")
            if response.status_code in [200, 400, 500]:
                data = response.json()
                print(f"  Response: {data}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_basic_endpoints()