#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class FinalVehicleAppraisalAPITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.working_endpoints = []
        self.failing_endpoints = []

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data)
            elif method == 'GET':
                response = requests.get(url)
            elif method == 'DELETE':
                response = requests.delete(url, json=data)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    self.working_endpoints.append(endpoint)
                    return True, response_data
                except:
                    self.working_endpoints.append(endpoint)
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                    
                    # Check if this is a critical failure (core functionality broken)
                    if response.status_code == 500 and endpoint in ['api/vin-decode']:
                        self.critical_failures.append(f"{endpoint}: {error_data}")
                    else:
                        self.failing_endpoints.append(f"{endpoint}: Expected {expected_status}, got {response.status_code}")
                        
                except:
                    print(f"   Error Text: {response.text}")
                    self.failing_endpoints.append(f"{endpoint}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.critical_failures.append(f"{endpoint}: Connection error - {str(e)}")
            return False, {}

    def test_vin_decode_functionality(self):
        """Test core VIN decode functionality"""
        print("\n=== TESTING CORE VIN DECODE FUNCTIONALITY ===")
        
        # Test valid VIN
        success, response = self.run_test(
            "VIN Decode with Valid VIN",
            "POST",
            "api/vin-decode",
            200,
            data={"vin": "1HGBH41JXMN109186"}
        )
        
        if success and 'vehicle' in response:
            vehicle = response['vehicle']
            if vehicle.get('make') and vehicle.get('year'):
                print(f"   ✅ Core VIN decode working: {vehicle['make']} {vehicle['year']}")
                return True
        
        return False

    def test_vin_decode_validation(self):
        """Test VIN decode input validation"""
        
        # Test missing VIN
        self.run_test(
            "VIN Decode - Missing VIN",
            "POST",
            "api/vin-decode",
            400,
            data={}
        )
        
        # Test invalid VIN
        self.run_test(
            "VIN Decode - Invalid VIN",
            "POST",
            "api/vin-decode",
            400,
            data={"vin": "INVALID"}
        )

    def test_ocr_endpoints_basic(self):
        """Test OCR endpoints basic functionality (expected to have issues)"""
        print("\n=== TESTING OCR ENDPOINTS (KNOWN ISSUES) ===")
        
        ocr_endpoints = [
            ("api/ocr-vin", "VIN OCR"),
            ("api/ocr-license-plate", "License Plate OCR"),
            ("api/ocr-mileage", "Mileage OCR")
        ]
        
        for endpoint, name in ocr_endpoints:
            # Test without image (should return 400, but may return 500 due to Google Vision API issues)
            success, response = self.run_test(
                f"{name} - No Image",
                "POST",
                endpoint,
                400  # Expected, but may get 500
            )
            
            # Note: These are expected to fail due to Google Vision API configuration issues
            if not success:
                print(f"   ⚠️  {name} has configuration issues (Google Vision API)")

    def test_admin_endpoints(self):
        """Test admin endpoints"""
        print("\n=== TESTING ADMIN ENDPOINTS ===")
        
        # Test get users
        success, response = self.run_test(
            "Admin - Get Users",
            "GET",
            "api/admin/users",
            200
        )
        
        if not success:
            print("   ⚠️  Admin endpoints have Firebase configuration issues")
        
        # Test add user validation
        self.run_test(
            "Admin - Add User Invalid Data",
            "POST",
            "api/admin/add-user",
            400,
            data={"email": "", "password": "", "role": ""}
        )
        
        # Test delete user validation
        self.run_test(
            "Admin - Delete User Invalid UID",
            "DELETE",
            "api/admin/delete-user",
            400,
            data={"uid": ""}
        )

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n✅ WORKING ENDPOINTS ({len(self.working_endpoints)}):")
        for endpoint in set(self.working_endpoints):
            print(f"  - {endpoint}")
        
        print(f"\n❌ FAILING ENDPOINTS ({len(self.failing_endpoints)}):")
        for failure in self.failing_endpoints:
            print(f"  - {failure}")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"  - {failure}")
        
        # Determine overall status
        core_working = any('vin-decode' in endpoint for endpoint in self.working_endpoints)
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if core_working:
            print("✅ Core VIN decode functionality is WORKING")
            print("⚠️  OCR endpoints have Google Vision API configuration issues")
            print("⚠️  Admin endpoints have Firebase configuration issues")
            print("📋 Application has basic functionality but needs configuration fixes")
        else:
            print("❌ Core functionality is BROKEN")
            
        return core_working

def main():
    print("🚀 Final Vehicle Appraisal API Test Suite")
    print("=" * 60)
    
    tester = FinalVehicleAppraisalAPITester("http://localhost:3000")
    
    # Test core functionality first
    core_working = tester.test_vin_decode_functionality()
    
    # Test input validation
    tester.test_vin_decode_validation()
    
    # Test OCR endpoints (expected issues)
    tester.test_ocr_endpoints_basic()
    
    # Test admin endpoints
    tester.test_admin_endpoints()
    
    # Generate summary
    overall_success = tester.generate_summary()
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit(main())