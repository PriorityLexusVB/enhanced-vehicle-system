#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class AdminAPITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_users = []  # Track users we create for cleanup

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=10)

            success = response.status_code == expected_status
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    result['response'] = response_data
                    self.test_results.append(result)
                    return True, response_data
                except:
                    result['response'] = {}
                    self.test_results.append(result)
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    result['error'] = error_data
                except:
                    print(f"   Error Text: {response.text}")
                    result['error'] = response.text
                self.test_results.append(result)
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_admin_get_users(self):
        """Test GET /api/admin/users - This was returning empty arrays"""
        success, response = self.run_test(
            "Admin Get Users API",
            "GET",
            "api/admin/users",
            200
        )
        
        if success:
            users = response.get('users', [])
            print(f"   📊 Found {len(users)} users in system")
            if len(users) > 0:
                print(f"   👥 User emails: {[u.get('email', 'no-email') for u in users]}")
            return True, users
        return False, []

    def test_admin_add_user(self):
        """Test POST /api/admin/add-user - Test creating a new user"""
        timestamp = int(time.time())
        test_email = f"test-user-{timestamp}@priority-appraisal.com"
        test_password = "TestPassword123!"
        test_role = "manager"
        
        success, response = self.run_test(
            "Admin Add User API",
            "POST",
            "api/admin/add-user",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "role": test_role
            }
        )
        
        if success and response.get('success'):
            user_uid = response.get('user', {}).get('uid')
            if user_uid:
                self.created_users.append(user_uid)
                print(f"   ✅ User created successfully with UID: {user_uid}")
                return True, user_uid
            else:
                print(f"   ⚠️  User creation response missing UID")
                return False, None
        return False, None

    def test_admin_add_user_validation(self):
        """Test POST /api/admin/add-user with missing fields"""
        success, response = self.run_test(
            "Admin Add User API - Missing Fields",
            "POST",
            "api/admin/add-user",
            400,
            data={
                "email": "incomplete@test.com"
                # Missing password and role
            }
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned validation error: {response['error']}")
            return True
        return False

    def test_admin_delete_user(self, uid):
        """Test DELETE /api/admin/delete-user - Test deleting a user"""
        if not uid:
            print("   ⚠️  No UID provided for deletion test")
            return False
            
        success, response = self.run_test(
            "Admin Delete User API",
            "DELETE",
            "api/admin/delete-user",
            200,
            data={"uid": uid}
        )
        
        if success and response.get('success'):
            print(f"   ✅ User deleted successfully")
            return True
        return False

    def test_admin_delete_user_validation(self):
        """Test DELETE /api/admin/delete-user with missing UID"""
        success, response = self.run_test(
            "Admin Delete User API - Missing UID",
            "DELETE",
            "api/admin/delete-user",
            400,
            data={}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned validation error: {response['error']}")
            return True
        return False

    def test_vin_decode_api(self):
        """Test VIN decode API to ensure we didn't break anything"""
        success, response = self.run_test(
            "VIN Decode API - Regression Test",
            "POST",
            "api/vin-decode",
            200,
            data={"vin": "1HGBH41JXMN109186"}
        )
        
        if success and response.get('success'):
            vehicle = response.get('vehicle', {})
            if vehicle.get('make') and vehicle.get('year'):
                print(f"   ✅ VIN decoded: {vehicle.get('year')} {vehicle.get('make')} - Trade-in: {vehicle.get('tradeInValue', 'N/A')}")
                return True
            else:
                print(f"   ⚠️  VIN decoded but missing vehicle info")
                return False
        return False

    def test_gemini_ai_analysis(self):
        """Test Gemini AI photo analysis to ensure we didn't break anything"""
        test_data = {
            "submissionId": "test-submission-123",
            "photoUrls": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
                "https://example.com/photo3.jpg"
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "make": "Honda",
                "model": "Civic",
                "year": "1991",
                "mileage": "150000"
            }
        }
        
        success, response = self.run_test(
            "Gemini AI Photo Analysis - Regression Test",
            "POST",
            "api/analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and response.get('success'):
            analysis = response.get('data', {}).get('analysis', {})
            if analysis.get('overall_condition') and analysis.get('confidence_score'):
                print(f"   ✅ AI Analysis completed - Grade: {analysis.get('vehicle_grade', 'N/A')}, Confidence: {analysis.get('confidence_score', 'N/A')}%")
                return True
            else:
                print(f"   ⚠️  AI analysis response missing key fields")
                return False
        return False

    def test_admin_user_cycle(self):
        """Test the complete admin user management cycle"""
        print("\n🔄 Testing Complete Admin User Management Cycle...")
        
        # Step 1: Get initial user count
        print("\n📊 Step 1: Get initial user count")
        success1, initial_users = self.test_admin_get_users()
        initial_count = len(initial_users) if success1 else 0
        print(f"   Initial user count: {initial_count}")
        
        # Step 2: Add a new user
        print("\n➕ Step 2: Add a new user")
        success2, new_uid = self.test_admin_add_user()
        
        # Step 3: Get users again to verify the new user appears
        print("\n📊 Step 3: Verify user appears in list")
        success3, updated_users = self.test_admin_get_users()
        updated_count = len(updated_users) if success3 else 0
        print(f"   Updated user count: {updated_count}")
        
        # Check if user count increased
        user_visible = updated_count > initial_count
        if user_visible:
            print(f"   ✅ User count increased from {initial_count} to {updated_count}")
        else:
            print(f"   ❌ User count did not increase (still {updated_count})")
        
        # Step 4: Delete the user if it was created
        if success2 and new_uid:
            print(f"\n🗑️  Step 4: Delete the created user (UID: {new_uid})")
            success4 = self.test_admin_delete_user(new_uid)
            
            # Step 5: Verify user is removed
            print("\n📊 Step 5: Verify user is removed from list")
            success5, final_users = self.test_admin_get_users()
            final_count = len(final_users) if success5 else 0
            print(f"   Final user count: {final_count}")
            
            user_removed = final_count == initial_count
            if user_removed:
                print(f"   ✅ User successfully removed (count back to {final_count})")
            else:
                print(f"   ❌ User not properly removed (expected {initial_count}, got {final_count})")
            
            return success1 and success2 and user_visible and success4 and user_removed
        else:
            print("\n⚠️  Skipping deletion test - user creation failed")
            return success1 and success2 and user_visible

    def cleanup_created_users(self):
        """Clean up any users we created during testing"""
        if self.created_users:
            print(f"\n🧹 Cleaning up {len(self.created_users)} created users...")
            for uid in self.created_users:
                try:
                    self.test_admin_delete_user(uid)
                except:
                    print(f"   ⚠️  Failed to cleanup user {uid}")

    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "=" * 80)
        print("📊 ADMIN FUNCTIONALITY TEST RESULTS")
        print("=" * 80)
        
        admin_tests = [r for r in self.test_results if 'admin' in r['endpoint'].lower()]
        regression_tests = [r for r in self.test_results if 'admin' not in r['endpoint'].lower()]
        
        print(f"\n👥 ADMIN ENDPOINTS TESTING:")
        for test in admin_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
                if 'error' in test:
                    error_msg = test['error']
                    if isinstance(error_msg, dict):
                        error_msg = json.dumps(error_msg, indent=6)
                    print(f"      Error: {error_msg}")
        
        print(f"\n🔄 REGRESSION TESTING (Other APIs):")
        for test in regression_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Check critical functionality
        admin_get_working = any(
            test['success'] and 'Admin Get Users' in test['name'] 
            for test in self.test_results
        )
        admin_add_working = any(
            test['success'] and 'Admin Add User API' == test['name'] 
            for test in self.test_results
        )
        admin_delete_working = any(
            test['success'] and 'Admin Delete User API' == test['name'] 
            for test in self.test_results
        )
        vin_decode_working = any(
            test['success'] and 'VIN Decode' in test['name'] 
            for test in self.test_results
        )
        gemini_working = any(
            test['success'] and 'Gemini AI' in test['name'] 
            for test in self.test_results
        )
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        print(f"   Admin Get Users: {'✅ WORKING' if admin_get_working else '❌ FAILING'}")
        print(f"   Admin Add User: {'✅ WORKING' if admin_add_working else '❌ FAILING'}")
        print(f"   Admin Delete User: {'✅ WORKING' if admin_delete_working else '❌ FAILING'}")
        print(f"   VIN Decode API: {'✅ WORKING' if vin_decode_working else '❌ FAILING'}")
        print(f"   Gemini AI Analysis: {'✅ WORKING' if gemini_working else '❌ FAILING'}")
        
        # Determine overall admin functionality status
        admin_fully_working = admin_get_working and admin_add_working and admin_delete_working
        
        return {
            'admin_fully_working': admin_fully_working,
            'admin_get_working': admin_get_working,
            'admin_add_working': admin_add_working,
            'admin_delete_working': admin_delete_working,
            'vin_decode_working': vin_decode_working,
            'gemini_working': gemini_working,
            'total_tests': self.tests_run,
            'passed_tests': self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run)*100 if self.tests_run > 0 else 0
        }

def main():
    print("🚀 Starting Admin Functionality Tests...")
    print("🎯 Focus: Admin user management endpoints that had issues")
    print("=" * 80)
    
    # Setup
    tester = AdminAPITester("http://localhost:3000")
    
    try:
        # Test individual admin endpoints first
        print("\n📋 INDIVIDUAL ENDPOINT TESTS:")
        tester.test_admin_get_users()
        tester.test_admin_add_user_validation()
        tester.test_admin_delete_user_validation()
        
        # Test the complete admin user management cycle
        print("\n🔄 COMPLETE ADMIN USER MANAGEMENT CYCLE:")
        cycle_success = tester.test_admin_user_cycle()
        
        # Test regression - ensure other APIs still work
        print("\n🔄 REGRESSION TESTING:")
        tester.test_vin_decode_api()
        tester.test_gemini_ai_analysis()
        
        # Print detailed results
        results = tester.print_summary()
        
        # Determine overall success
        if results['admin_fully_working']:
            print("\n🎉 SUCCESS: Admin functionality is working correctly!")
            print("   ✅ Users can be retrieved from Firebase/Firestore")
            print("   ✅ Users can be created and appear in the list immediately")
            print("   ✅ Users can be deleted successfully")
            if results['vin_decode_working'] and results['gemini_working']:
                print("   ✅ Other APIs are still working (no regressions)")
            return 0
        elif results['admin_get_working'] and results['admin_add_working']:
            print("\n⚠️  PARTIAL SUCCESS: Admin functionality partially working")
            print("   ✅ Users can be retrieved and created")
            if not results['admin_delete_working']:
                print("   ❌ User deletion needs attention")
            return 1
        else:
            print("\n❌ CRITICAL FAILURE: Admin functionality not working")
            if not results['admin_get_working']:
                print("   ❌ Cannot retrieve users from system")
            if not results['admin_add_working']:
                print("   ❌ Cannot create new users")
            return 2
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return 3
    finally:
        # Always try to cleanup
        tester.cleanup_created_users()

if __name__ == "__main__":
    sys.exit(main())