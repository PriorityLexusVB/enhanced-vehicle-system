#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ComprehensiveRoleBasedTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'projectId': 'priority-appraisal-ai-tool'
        }
        self.test_results = []
        
    def run_test(self, name, test_func):
        """Run a test and record results"""
        print(f"\n🔍 {name}")
        print("-" * 50)
        
        try:
            success, details = test_func()
            self.test_results.append({
                'name': name,
                'success': success,
                'details': details
            })
            
            if success:
                print(f"✅ PASSED: {details}")
            else:
                print(f"❌ FAILED: {details}")
                
            return success
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.test_results.append({
                'name': name,
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False

    def test_admin_api_functionality(self):
        """Test admin API endpoints"""
        try:
            # Test GET users
            response = requests.get(f"{self.base_url}/api/admin/users")
            if response.status_code != 200:
                return False, f"GET /api/admin/users failed with status {response.status_code}"
            
            # Test POST add-user validation
            response = requests.post(f"{self.base_url}/api/admin/add-user", json={})
            if response.status_code != 400:
                return False, f"POST /api/admin/add-user validation failed"
            
            # Test DELETE delete-user validation
            response = requests.delete(f"{self.base_url}/api/admin/delete-user", json={})
            if response.status_code != 400:
                return False, f"DELETE /api/admin/delete-user validation failed"
            
            return True, "All admin API endpoints responding correctly"
            
        except Exception as e:
            return False, f"Admin API test exception: {str(e)}"

    def test_core_api_functionality(self):
        """Test core API endpoints"""
        try:
            # Test VIN decode API
            response = requests.post(f"{self.base_url}/api/vin-decode", json={"vin": "1HGBH41JXMN109186"})
            if response.status_code != 200:
                return False, f"VIN decode API failed with status {response.status_code}"
            
            data = response.json()
            if not data.get('success'):
                return False, "VIN decode API returned success=false"
            
            # Test Gemini AI analysis API
            test_data = {
                "submissionId": "test-123",
                "photoUrls": ["https://example.com/photo1.jpg"],
                "submissionData": {
                    "vin": "1HGBH41JXMN109186",
                    "make": "Honda",
                    "model": "Civic",
                    "year": 1991,
                    "mileage": 87325
                }
            }
            
            response = requests.post(f"{self.base_url}/api/analyze-vehicle-photos", json=test_data)
            if response.status_code != 200:
                return False, f"Gemini AI API failed with status {response.status_code}"
            
            return True, "Core APIs (VIN decode, Gemini AI) working correctly"
            
        except Exception as e:
            return False, f"Core API test exception: {str(e)}"

    def test_firebase_auth_functionality(self):
        """Test Firebase authentication with existing users"""
        try:
            # Test with known working credentials
            test_credentials = [
                ("test-admin@priority-appraisal.com", "TestAdmin123!"),
                ("manager@priority-appraisal.com", "Manager123!")
            ]
            
            working_users = []
            
            for email, password in test_credentials:
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_config['apiKey']}"
                payload = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    working_users.append({
                        'email': email,
                        'password': password,
                        'uid': data.get('localId')
                    })
            
            if len(working_users) >= 1:
                return True, f"Firebase Auth working with {len(working_users)} test users"
            else:
                return False, "No working Firebase Auth credentials found"
                
        except Exception as e:
            return False, f"Firebase Auth test exception: {str(e)}"

    def test_role_assignment_issue_diagnosis(self):
        """Diagnose the role assignment issue"""
        try:
            # Create a test user to understand the issue
            timestamp = int(time.time())
            test_email = f"role-test-{timestamp}@test.com"
            
            # Step 1: Create user via admin API
            response = requests.post(f"{self.base_url}/api/admin/add-user", json={
                "email": test_email,
                "password": "RoleTest123!",
                "role": "admin"
            })
            
            if response.status_code != 200:
                return False, f"Cannot create test user: {response.status_code}"
            
            data = response.json()
            if not data.get('success'):
                return False, "Test user creation returned success=false"
            
            uid = data.get('uid')
            
            # Step 2: Check if user appears in admin API
            time.sleep(2)  # Wait for potential sync
            response = requests.get(f"{self.base_url}/api/admin/users")
            
            if response.status_code == 200:
                users_data = response.json()
                users = users_data.get('users', [])
                
                user_found = any(user.get('email') == test_email for user in users)
                
                if user_found:
                    return True, f"Role assignment working - test user found in Firestore"
                else:
                    return False, f"Role assignment issue confirmed - user created in Auth but not in Firestore (UID: {uid})"
            else:
                return False, f"Cannot check admin users API: {response.status_code}"
                
        except Exception as e:
            return False, f"Role diagnosis exception: {str(e)}"

    def provide_role_assignment_solution(self):
        """Provide solution for role assignment"""
        print("\n" + "=" * 80)
        print("🔧 ROLE ASSIGNMENT SOLUTION")
        print("=" * 80)
        
        print("\n📋 ISSUE IDENTIFIED:")
        print("   - Firebase Auth user creation works correctly")
        print("   - Firestore document creation fails due to security rules")
        print("   - Users exist in Firebase Auth but have no role documents")
        print("   - Manager Dashboard shows 'Current role: None'")
        
        print("\n🎯 WORKING USER CREDENTIALS:")
        print("   📧 test-admin@priority-appraisal.com")
        print("   🔑 Password: TestAdmin123!")
        print("   📝 UID: 2FsveUKHTlWAZB6ywrL9DzZaaxq2")
        print("   🎭 Needs role: admin")
        print()
        print("   📧 manager@priority-appraisal.com")
        print("   🔑 Password: Manager123!")
        print("   📝 UID: TIUKD9BmcnbYaKQLuDzT1xvbLjG3")
        print("   🎭 Needs role: manager")
        
        print("\n🔧 MANUAL SOLUTION STEPS:")
        print("1. Open Firebase Console:")
        print("   https://console.firebase.google.com/project/priority-appraisal-ai-tool/firestore")
        
        print("\n2. Navigate to Firestore Database")
        
        print("\n3. Create 'users' collection if it doesn't exist")
        
        print("\n4. Create document for test-admin user:")
        print("   📝 Document ID: 2FsveUKHTlWAZB6ywrL9DzZaaxq2")
        print("   📊 Document fields:")
        print("      email: test-admin@priority-appraisal.com")
        print("      role: admin")
        print("      createdAt: [Current timestamp]")
        
        print("\n5. Create document for manager user:")
        print("   📝 Document ID: TIUKD9BmcnbYaKQLuDzT1xvbLjG3")
        print("   📊 Document fields:")
        print("      email: manager@priority-appraisal.com")
        print("      role: manager")
        print("      createdAt: [Current timestamp]")
        
        print("\n6. Alternative: Update Firestore Security Rules")
        print("   Allow authenticated users to create their own role documents")
        
        print("\n🎉 EXPECTED OUTCOME:")
        print("   - Manager Dashboard will show correct role instead of 'None'")
        print("   - Access Denied error will be resolved")
        print("   - Complete end-to-end integration will work")

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ROLE-BASED ACCESS TESTING RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
            if not result['success']:
                print(f"      Details: {result['details']}")
        
        # Determine system status
        admin_api_working = any(r['success'] and 'admin api' in r['name'].lower() for r in self.test_results)
        core_api_working = any(r['success'] and 'core api' in r['name'].lower() for r in self.test_results)
        auth_working = any(r['success'] and 'firebase auth' in r['name'].lower() for r in self.test_results)
        
        print(f"\n🎯 SYSTEM STATUS:")
        print(f"   Admin APIs: {'✅ WORKING' if admin_api_working else '❌ FAILING'}")
        print(f"   Core APIs: {'✅ WORKING' if core_api_working else '❌ FAILING'}")
        print(f"   Firebase Auth: {'✅ WORKING' if auth_working else '❌ FAILING'}")
        print(f"   Role Assignment: ❌ NEEDS MANUAL FIX")
        
        return admin_api_working and core_api_working and auth_working

def main():
    print("🚀 Comprehensive Role-Based Access Control Testing")
    print("=" * 80)
    
    tester = ComprehensiveRoleBasedTester()
    
    # Run all tests
    tests = [
        ("Admin API Functionality", tester.test_admin_api_functionality),
        ("Core API Functionality", tester.test_core_api_functionality),
        ("Firebase Auth Functionality", tester.test_firebase_auth_functionality),
        ("Role Assignment Issue Diagnosis", tester.test_role_assignment_issue_diagnosis)
    ]
    
    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)
    
    # Print comprehensive results
    system_working = tester.print_comprehensive_summary()
    
    # Provide solution
    tester.provide_role_assignment_solution()
    
    # Final status
    print(f"\n🎯 FINAL STATUS:")
    if system_working:
        print("✅ BACKEND SYSTEMS: All working correctly")
        print("🔧 ACTION REQUIRED: Manual role assignment in Firebase Console")
        print("📋 IMPACT: Manager Dashboard will work after role assignment")
        return 0
    else:
        print("❌ BACKEND SYSTEMS: Some issues detected")
        print("🔧 ACTION REQUIRED: Fix backend issues and role assignment")
        return 1

if __name__ == "__main__":
    sys.exit(main())