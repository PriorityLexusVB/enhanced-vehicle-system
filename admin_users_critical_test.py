#!/usr/bin/env python3

import requests
import sys
import os
import json
from datetime import datetime

class AdminUsersCriticalTester:
    def __init__(self, base_url="https://app-p4xu7qp6d-robs-projects-98a6166f.vercel.app"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'GET':
                response = requests.get(url, headers=headers)

            success = response.status_code == expected_status
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success
            }
            
            print(f"   Status Code: {response.status_code}")
            
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

    def test_admin_users_api(self):
        """Test the critical admin users API endpoint"""
        print("\n🚨 CRITICAL TEST: Admin Users API")
        print("=" * 50)
        
        success, response = self.run_test(
            "Admin Users API - GET /api/admin/users",
            "GET",
            "api/admin/users",
            200
        )
        
        if success:
            users = response.get('users', [])
            print(f"\n📊 ANALYSIS:")
            print(f"   Users returned: {len(users)}")
            
            if len(users) == 0:
                print("   ⚠️  Empty users array - this could indicate:")
                print("      1. No users exist in the system")
                print("      2. Firebase Admin SDK configuration issue")
                print("      3. Firestore security rules blocking access")
                print("      4. Environment variables missing/incorrect")
                return False
            else:
                print("   ✅ Users found in system:")
                for user in users:
                    print(f"      - {user.get('email', 'no-email')} (Role: {user.get('role', 'unknown')})")
                return True
        else:
            print(f"\n🚨 CRITICAL ERROR: API endpoint failed completely")
            return False

    def test_environment_variables_check(self):
        """Check if we can infer environment variable status from API behavior"""
        print("\n🔍 ENVIRONMENT VARIABLES INFERENCE TEST")
        print("=" * 50)
        
        # Test a simple endpoint to see if the app is running
        success, response = self.run_test(
            "Basic API Health Check",
            "POST",
            "api/vin-decode",
            400,  # Should return 400 for missing VIN, not 500 for server error
            data={}
        )
        
        if success:
            print("   ✅ Basic API infrastructure is working")
            print("   ✅ Next.js app is running and responding")
            return True
        else:
            print("   ❌ Basic API infrastructure has issues")
            return False

    def test_firebase_admin_sdk_initialization(self):
        """Test if Firebase Admin SDK is properly initialized by testing user creation"""
        print("\n🔥 FIREBASE ADMIN SDK INITIALIZATION TEST")
        print("=" * 50)
        
        # Try to create a test user to see if Firebase Admin SDK is working
        test_email = f"test-firebase-check-{int(datetime.now().timestamp())}@priority-appraisal.com"
        
        success, response = self.run_test(
            "Firebase Admin SDK - Create Test User",
            "POST",
            "api/admin/add-user",
            200,
            data={
                "email": test_email,
                "password": "TestPassword123!",
                "role": "sales"
            }
        )
        
        if success:
            print("   ✅ Firebase Admin SDK appears to be working")
            print("   ✅ User creation successful")
            
            # Now test if the user appears in the users list
            print("\n   🔍 Testing if created user appears in users list...")
            users_success, users_response = self.run_test(
                "Check if created user appears in users list",
                "GET",
                "api/admin/users",
                200
            )
            
            if users_success:
                users = users_response.get('users', [])
                created_user_found = any(user.get('email') == test_email for user in users)
                
                if created_user_found:
                    print("   ✅ Created user found in users list - Firebase integration working!")
                    return True
                else:
                    print("   ❌ Created user NOT found in users list - Firestore query issue!")
                    print("   🔍 This indicates:")
                    print("      - User creation works (Firebase Auth)")
                    print("      - User retrieval fails (Firestore/Admin SDK)")
                    print("      - Possible Firestore security rules issue")
                    return False
            else:
                print("   ❌ Could not retrieve users list after creation")
                return False
        else:
            print("   ❌ Firebase Admin SDK initialization appears to be failing")
            print("   🔍 Possible issues:")
            print("      - FIREBASE_PROJECT_ID missing or incorrect")
            print("      - FIREBASE_CLIENT_EMAIL missing or incorrect") 
            print("      - FIREBASE_PRIVATE_KEY missing or malformed")
            print("      - Firebase Admin SDK not properly initialized")
            return False

    def diagnose_firebase_admin_issue(self):
        """Comprehensive diagnosis of Firebase Admin SDK issues"""
        print("\n🔬 COMPREHENSIVE FIREBASE ADMIN SDK DIAGNOSIS")
        print("=" * 60)
        
        # Test 1: Basic API functionality
        print("\n1️⃣ Testing basic API functionality...")
        basic_working = self.test_environment_variables_check()
        
        # Test 2: Admin users endpoint
        print("\n2️⃣ Testing admin users endpoint...")
        users_working = self.test_admin_users_api()
        
        # Test 3: Firebase Admin SDK functionality
        print("\n3️⃣ Testing Firebase Admin SDK functionality...")
        firebase_working = self.test_firebase_admin_sdk_initialization()
        
        # Analysis
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSIS RESULTS")
        print("=" * 60)
        
        if basic_working and users_working and firebase_working:
            print("✅ ALL SYSTEMS WORKING - No issues found!")
            return "WORKING"
        elif basic_working and not users_working and not firebase_working:
            print("🚨 FIREBASE ADMIN SDK CONFIGURATION ISSUE")
            print("   Root Cause: Environment variables or Firebase Admin SDK setup")
            print("   Required Variables:")
            print("   - FIREBASE_PROJECT_ID")
            print("   - FIREBASE_CLIENT_EMAIL") 
            print("   - FIREBASE_PRIVATE_KEY")
            return "FIREBASE_CONFIG_ISSUE"
        elif basic_working and not users_working and firebase_working:
            print("🚨 FIRESTORE QUERY/SECURITY RULES ISSUE")
            print("   Root Cause: Users can be created but not retrieved")
            print("   Likely Issues:")
            print("   - Firestore security rules blocking server-side access")
            print("   - Client SDK vs Admin SDK configuration mismatch")
            return "FIRESTORE_SECURITY_ISSUE"
        else:
            print("🚨 MULTIPLE SYSTEM FAILURES")
            print("   Root Cause: Fundamental infrastructure issues")
            return "SYSTEM_FAILURE"

    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "=" * 60)
        print("📊 ADMIN USERS API CRITICAL TEST RESULTS")
        print("=" * 60)
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔍 DETAILED TEST RESULTS:")
        for test in self.test_results:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
                if 'error' in test:
                    error_str = str(test['error'])[:200] + "..." if len(str(test['error'])) > 200 else str(test['error'])
                    print(f"      Error: {error_str}")

def main():
    print("🚨 CRITICAL: Admin Panel 'Failed to Fetch Users' Investigation")
    print("🔍 Testing deployed app: https://app-p4xu7qp6d-robs-projects-98a6166f.vercel.app")
    print("=" * 80)
    
    # Setup
    tester = AdminUsersCriticalTester()
    
    # Run comprehensive diagnosis
    diagnosis = tester.diagnose_firebase_admin_issue()
    
    # Print detailed results
    tester.print_summary()
    
    # Final recommendations
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS FOR MAIN AGENT")
    print("=" * 60)
    
    if diagnosis == "WORKING":
        print("✅ No action needed - system is working correctly")
        return 0
    elif diagnosis == "FIREBASE_CONFIG_ISSUE":
        print("🔧 IMMEDIATE ACTIONS REQUIRED:")
        print("   1. Verify FIREBASE_PROJECT_ID in Vercel environment variables")
        print("   2. Verify FIREBASE_CLIENT_EMAIL in Vercel environment variables")
        print("   3. Verify FIREBASE_PRIVATE_KEY in Vercel environment variables")
        print("   4. Check Firebase Admin SDK initialization in lib/firebase-admin.ts")
        print("   5. Fix import mismatch: adminOperations vs firebaseAdmin")
        return 1
    elif diagnosis == "FIRESTORE_SECURITY_ISSUE":
        print("🔧 IMMEDIATE ACTIONS REQUIRED:")
        print("   1. Update Firestore security rules to allow server-side access")
        print("   2. Ensure Firebase Admin SDK has proper permissions")
        print("   3. Check if users collection exists and is accessible")
        return 1
    else:
        print("🔧 CRITICAL SYSTEM ISSUES - COMPREHENSIVE DEBUGGING NEEDED")
        return 2

if __name__ == "__main__":
    sys.exit(main())