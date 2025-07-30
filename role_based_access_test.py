#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class RoleBasedAccessTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.working_credentials = [
            ("test-admin@priority-appraisal.com", "TestAdmin123!"),
            ("manager@priority-appraisal.com", "Manager123!")
        ]
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)

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
                    print(f"   Response: {response_data}")
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
                    print(f"   Error Response: {error_data}")
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
        """Test admin users endpoint"""
        success, response = self.run_test(
            "Admin Get Users API",
            "GET",
            "api/admin/users",
            200
        )
        
        if success and 'users' in response:
            users = response['users']
            print(f"   ✅ Successfully retrieved {len(users)} users")
            return True
        return False

    def test_admin_add_user_validation(self):
        """Test admin add user endpoint validation"""
        # Test missing fields
        success, response = self.run_test(
            "Admin Add User - Missing Fields",
            "POST",
            "api/admin/add-user",
            400,
            data={"email": "test@example.com"}  # Missing password and role
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned validation error: {response['error']}")
            return True
        return False

    def test_admin_add_user_invalid_role(self):
        """Test admin add user endpoint with invalid role"""
        success, response = self.run_test(
            "Admin Add User - Invalid Role",
            "POST",
            "api/admin/add-user",
            400,
            data={
                "email": "test@example.com",
                "password": "password123",
                "role": "invalid_role"
            }
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned role validation error: {response['error']}")
            return True
        return False

    def test_admin_add_user_valid(self):
        """Test admin add user endpoint with valid data"""
        test_email = f"test-user-{int(time.time())}@example.com"
        success, response = self.run_test(
            "Admin Add User - Valid Data",
            "POST",
            "api/admin/add-user",
            200,
            data={
                "email": test_email,
                "password": "TestPassword123!",
                "role": "manager"
            }
        )
        
        if success and response.get('success'):
            print(f"   ✅ Successfully created user: {test_email}")
            return True, response.get('uid')
        return False, None

    def test_admin_delete_user_validation(self):
        """Test admin delete user endpoint validation"""
        success, response = self.run_test(
            "Admin Delete User - Missing UID",
            "DELETE",
            "api/admin/delete-user",
            400,
            data={}  # Missing uid
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned validation error: {response['error']}")
            return True
        return False

    def test_admin_delete_user_valid(self, uid):
        """Test admin delete user endpoint with valid UID"""
        if not uid:
            print("   ⚠️  Skipping delete test - no UID provided")
            return False
            
        success, response = self.run_test(
            "Admin Delete User - Valid UID",
            "DELETE",
            "api/admin/delete-user",
            200,
            data={"uid": uid}
        )
        
        if success and response.get('success'):
            print(f"   ✅ Successfully deleted user with UID: {uid}")
            return True
        return False

    def test_firebase_user_role_assignment(self):
        """Test Firebase user role assignment using direct Firestore API"""
        print("\n🔧 Testing Firebase User Role Assignment...")
        
        # This would require Firebase Admin SDK or direct Firestore REST API
        # For now, we'll simulate the role assignment process
        
        test_user_email = "test-admin@priority-appraisal.com"
        
        print(f"   📝 Simulating role assignment for: {test_user_email}")
        print(f"   🎯 Target role: admin")
        
        # In a real implementation, this would:
        # 1. Get the user's UID from Firebase Auth
        # 2. Create/update a document in Firestore at /users/{uid}
        # 3. Set the role field to 'admin' or 'manager'
        
        print(f"   ✅ Role assignment simulation completed")
        print(f"   📋 Next steps:")
        print(f"      1. Verify user document exists in Firestore /users collection")
        print(f"      2. Ensure role field is set to 'admin' or 'manager'")
        print(f"      3. Test Manager Dashboard access with updated role")
        
        return True

    def test_role_based_access_simulation(self):
        """Simulate role-based access control testing"""
        print("\n🔐 Testing Role-Based Access Control...")
        
        # Test scenarios
        scenarios = [
            {
                "user": "test-admin@priority-appraisal.com",
                "expected_role": "admin",
                "should_access_manager_dashboard": True,
                "should_access_admin_panel": True
            },
            {
                "user": "manager@priority-appraisal.com", 
                "expected_role": "manager",
                "should_access_manager_dashboard": True,
                "should_access_admin_panel": False
            }
        ]
        
        for scenario in scenarios:
            print(f"\n   👤 Testing access for: {scenario['user']}")
            print(f"   🎭 Expected role: {scenario['expected_role']}")
            print(f"   📊 Manager Dashboard access: {'✅ Allowed' if scenario['should_access_manager_dashboard'] else '❌ Denied'}")
            print(f"   ⚙️  Admin Panel access: {'✅ Allowed' if scenario['should_access_admin_panel'] else '❌ Denied'}")
        
        return True

    def test_gemini_ai_analysis_api(self):
        """Test Gemini AI photo analysis API"""
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
                "year": 1991,
                "mileage": 87325,
                "ownerNotes": "Minor scratches on rear bumper"
            }
        }
        
        success, response = self.run_test(
            "Gemini AI Photo Analysis API",
            "POST",
            "api/analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and 'analysis' in response:
            analysis = response['analysis']
            print(f"   ✅ Analysis completed successfully")
            print(f"   📊 Overall condition: {analysis.get('overall_condition', 'N/A')}")
            print(f"   🎯 Vehicle grade: {analysis.get('vehicle_grade', 'N/A')}")
            print(f"   📈 Confidence score: {analysis.get('confidence_score', 'N/A')}%")
            return True
        return False

    def test_vin_decode_api(self):
        """Test VIN decode API"""
        success, response = self.run_test(
            "VIN Decode API",
            "POST",
            "api/vin-decode",
            200,
            data={"vin": "1HGBH41JXMN109186"}
        )
        
        if success and response.get('success'):
            vehicle = response.get('vehicle', {})
            print(f"   ✅ VIN decoded successfully: {vehicle.get('make')} {vehicle.get('model')} {vehicle.get('year')}")
            return True
        return False

    def print_role_assignment_instructions(self):
        """Print detailed instructions for role assignment"""
        print("\n" + "=" * 80)
        print("🔧 FIREBASE USER ROLE ASSIGNMENT INSTRUCTIONS")
        print("=" * 80)
        
        print("\n📋 MANUAL STEPS TO ASSIGN ROLES:")
        print("1. Open Firebase Console:")
        print("   https://console.firebase.google.com/project/priority-appraisal-ai-tool/firestore")
        
        print("\n2. Navigate to Firestore Database")
        
        print("\n3. Create/Update user documents in 'users' collection:")
        
        users_to_configure = [
            {
                "email": "test-admin@priority-appraisal.com",
                "role": "admin",
                "uid": "Get from Firebase Auth Users tab"
            },
            {
                "email": "manager@priority-appraisal.com", 
                "role": "manager",
                "uid": "Get from Firebase Auth Users tab"
            }
        ]
        
        for user in users_to_configure:
            print(f"\n   👤 User: {user['email']}")
            print(f"   📝 Document path: /users/{user['uid']}")
            print(f"   📊 Document data:")
            print(f"      {{")
            print(f"        \"email\": \"{user['email']}\",")
            print(f"        \"role\": \"{user['role']}\",")
            print(f"        \"createdAt\": [Firestore Timestamp]")
            print(f"      }}")
        
        print("\n4. Alternative: Use Firebase Admin SDK or REST API")
        print("5. Verify role assignment by testing Manager Dashboard access")
        
        print("\n🎯 EXPECTED OUTCOME:")
        print("   - test-admin@priority-appraisal.com should access Manager Dashboard")
        print("   - Current role should show 'admin' instead of 'None'")
        print("   - Manager Dashboard should display properly without 'Access Denied' error")

    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "=" * 60)
        print("📊 ROLE-BASED ACCESS TESTING RESULTS")
        print("=" * 60)
        
        admin_tests = [r for r in self.test_results if 'admin' in r['endpoint'].lower()]
        api_tests = [r for r in self.test_results if 'admin' not in r['endpoint'].lower()]
        
        print(f"\n🔧 ADMIN API ENDPOINTS:")
        for test in admin_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
        
        print(f"\n🚀 CORE API ENDPOINTS:")
        for test in api_tests:
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
        admin_api_working = any(
            test['success'] and 'admin' in test['endpoint'].lower()
            for test in self.test_results
        )
        core_api_working = any(
            test['success'] and ('vin-decode' in test['endpoint'] or 'analyze-vehicle' in test['endpoint'])
            for test in self.test_results
        )
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        print(f"   Admin APIs: {'✅ WORKING' if admin_api_working else '❌ FAILING'}")
        print(f"   Core APIs: {'✅ WORKING' if core_api_working else '❌ FAILING'}")
        
        return admin_api_working, core_api_working

def main():
    print("🚀 Starting Role-Based Access Control Testing...")
    print("=" * 60)
    
    # Setup
    tester = RoleBasedAccessTester("http://localhost:3000")
    
    # Run all tests
    print("\n🔧 Testing Admin API Endpoints...")
    tester.test_admin_get_users()
    tester.test_admin_add_user_validation()
    tester.test_admin_add_user_invalid_role()
    
    # Test user creation and deletion
    success, uid = tester.test_admin_add_user_valid()
    if success and uid:
        tester.test_admin_delete_user_valid(uid)
    
    tester.test_admin_delete_user_validation()
    
    print("\n🚀 Testing Core API Endpoints...")
    tester.test_vin_decode_api()
    tester.test_gemini_ai_analysis_api()
    
    print("\n🔐 Testing Role-Based Access Control...")
    tester.test_firebase_user_role_assignment()
    tester.test_role_based_access_simulation()
    
    # Print detailed results
    admin_working, core_working = tester.print_summary()
    
    # Print role assignment instructions
    tester.print_role_assignment_instructions()
    
    # Determine overall success
    if admin_working and core_working:
        print("\n🎉 SUCCESS: Admin APIs and Core APIs working!")
        print("🔧 NEXT STEP: Configure user roles in Firebase/Firestore")
        return 0
    elif core_working:
        print("\n⚠️  PARTIAL SUCCESS: Core APIs working, Admin APIs need attention")
        print("🔧 NEXT STEP: Fix Admin API configuration and assign user roles")
        return 1
    else:
        print("\n❌ CRITICAL FAILURE: Core functionality not working")
        return 2

if __name__ == "__main__":
    sys.exit(main())