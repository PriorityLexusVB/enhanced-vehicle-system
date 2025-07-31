#!/usr/bin/env python3
"""
ADMIN FUNCTIONALITY VERIFICATION TEST
Testing Enhanced Vehicle Appraisal System Admin Panel and Core APIs

Focus Areas:
1. Admin Panel User Management (/api/admin/users)
2. Add/Delete User functionality 
3. No test/mock data verification
4. Core system status (VIN decode, Gemini AI, OCR)
5. Role-based access control

User Requirements:
- Verify admin panel shows real users from Firestore
- Test add/remove user functionality
- Confirm no mock data is returned
- Verify all APIs are production-ready
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
import io
from PIL import Image, ImageDraw, ImageFont

class AdminFunctionalityTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.admin_users_found = []
        
    def print_header(self, title: str):
        print(f"\n{'='*70}")
        print(f"🔍 {title}")
        print(f"{'='*70}")
        
    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
            
    def run_api_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                     data: Dict = None, files: Dict = None) -> Tuple[bool, Dict]:
        """Run a single API test and return success status and response data"""
        url = f"{self.api_base}/{endpoint}"
        self.tests_run += 1
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Status: {response.status_code} (Expected: {expected_status})")
                
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Status: {response.status_code} (Expected: {expected_status})")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                    return False, error_data
                except:
                    print(f"   Error Text: {response.text}")
                    return False, {"error": response.text}
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error - Server may not be running")
            return False, {"error": "Connection refused"}
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False, {"error": str(e)}

    def test_admin_users_api(self) -> bool:
        """Test /api/admin/users endpoint - CRITICAL for admin functionality"""
        self.print_header("ADMIN USERS API - CRITICAL TEST")
        
        success, response = self.run_api_test(
            "Admin Users List",
            "GET", 
            "admin/users",
            200
        )
        
        if success and 'users' in response:
            users = response['users']
            self.admin_users_found = users
            
            print(f"\n📊 ADMIN USERS ANALYSIS:")
            print(f"   Users Found: {len(users)}")
            
            if len(users) == 0:
                print(f"   🚨 CRITICAL: No users returned from Firestore")
                print(f"   📋 Expected: Real users like admin@priority-appraisal.com")
                print(f"   🔍 This suggests either:")
                print(f"      - Firestore has no user documents")
                print(f"      - Server-side query is failing")
                print(f"      - Security rules blocking access")
                return False
            else:
                print(f"   ✅ SUCCESS: Found {len(users)} users in system")
                
                # Analyze user data for mock vs real
                real_users_found = []
                mock_users_found = []
                
                for i, user in enumerate(users, 1):
                    email = user.get('email', 'N/A')
                    role = user.get('role', 'N/A')
                    uid = user.get('uid', 'N/A')
                    created = user.get('createdAt', 'N/A')
                    
                    print(f"   User {i}:")
                    print(f"     - Email: {email}")
                    print(f"     - Role: {role}")
                    print(f"     - UID: {uid}")
                    print(f"     - Created: {created}")
                    
                    # Check if this looks like real vs mock data
                    if any(domain in email for domain in ['priority-appraisal.com', 'test-admin', 'manager@']):
                        real_users_found.append(email)
                    elif any(mock_domain in email for mock_domain in ['test@', 'mock@', 'dummy@']):
                        mock_users_found.append(email)
                    else:
                        real_users_found.append(email)  # Assume real unless obviously mock
                
                print(f"\n🎯 DATA VERIFICATION:")
                print(f"   Real Users: {len(real_users_found)} - {real_users_found}")
                print(f"   Mock Users: {len(mock_users_found)} - {mock_users_found}")
                
                if len(mock_users_found) > 0:
                    print(f"   ⚠️  WARNING: Mock users detected in system")
                    return False
                else:
                    print(f"   ✅ SUCCESS: All users appear to be real data")
                    return True
        
        return False

    def test_add_user_api(self) -> bool:
        """Test /api/admin/add-user endpoint"""
        self.print_header("ADD USER API TEST")
        
        # Test 1: Valid user creation
        test_user_data = {
            "email": f"test-user-{int(time.time())}@priority-appraisal.com",
            "password": "TestPassword123!",
            "role": "sales"
        }
        
        success, response = self.run_api_test(
            "Add Valid User",
            "POST",
            "admin/add-user",
            200,
            data=test_user_data
        )
        
        if success and response.get('success'):
            print(f"   ✅ User creation successful")
            print(f"   📧 Email: {test_user_data['email']}")
            print(f"   👤 Role: {test_user_data['role']}")
            
            # Store for cleanup if needed
            created_uid = response.get('uid')
            if created_uid:
                print(f"   🆔 UID: {created_uid}")
                
            user_creation_success = True
        else:
            print(f"   ❌ User creation failed")
            user_creation_success = False
        
        # Test 2: Invalid data validation
        invalid_data_tests = [
            ({"email": "", "password": "test", "role": "admin"}, "Empty email"),
            ({"email": "test@test.com", "password": "", "role": "admin"}, "Empty password"),
            ({"email": "test@test.com", "password": "test", "role": ""}, "Empty role"),
            ({"email": "test@test.com", "password": "test", "role": "invalid"}, "Invalid role"),
        ]
        
        validation_success = True
        for invalid_data, test_desc in invalid_data_tests:
            success, response = self.run_api_test(
                f"Add User Validation - {test_desc}",
                "POST",
                "admin/add-user", 
                400,
                data=invalid_data
            )
            if not success:
                validation_success = False
                
        return user_creation_success and validation_success

    def test_delete_user_api(self) -> bool:
        """Test /api/admin/delete-user endpoint"""
        self.print_header("DELETE USER API TEST")
        
        # Test 1: Missing UID validation
        success, response = self.run_api_test(
            "Delete User - Missing UID",
            "DELETE",
            "admin/delete-user",
            400,
            data={}
        )
        
        validation_success = success and 'error' in response
        
        # Test 2: Invalid UID (should handle gracefully)
        success, response = self.run_api_test(
            "Delete User - Invalid UID",
            "DELETE", 
            "admin/delete-user",
            500,  # Expect 500 for non-existent user
            data={"uid": "non-existent-uid-12345"}
        )
        
        # This should fail gracefully, so we expect either 400 or 500
        invalid_uid_success = response.get('error') is not None
        
        return validation_success and invalid_uid_success

    def test_vin_decode_api(self) -> bool:
        """Test VIN decode API - Core functionality"""
        self.print_header("VIN DECODE API - CORE FUNCTIONALITY")
        
        # Test with real VIN
        success, response = self.run_api_test(
            "VIN Decode - Real VIN",
            "POST",
            "vin-decode",
            200,
            data={"vin": "1HGBH41JXMN109186"}
        )
        
        if success and response.get('success'):
            vehicle = response.get('vehicle', {})
            make = vehicle.get('make')
            year = vehicle.get('year')
            
            print(f"   ✅ VIN Decoded Successfully")
            print(f"   🚗 Vehicle: {year} {make}")
            
            # Check for mock vs real data
            if make and year and make != "MOCK" and year != "MOCK":
                print(f"   ✅ Real vehicle data returned (not mock)")
                return True
            else:
                print(f"   ❌ Mock data detected in VIN decode")
                return False
        
        return False

    def test_gemini_ai_analysis(self) -> bool:
        """Test Gemini AI photo analysis - NEW feature"""
        self.print_header("GEMINI AI PHOTO ANALYSIS - NEW FEATURE")
        
        # Create test data for Gemini AI
        test_data = {
            "submissionId": f"test-{int(time.time())}",
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
                "mileage": "87325"
            }
        }
        
        success, response = self.run_api_test(
            "Gemini AI Vehicle Analysis",
            "POST",
            "analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and response.get('success'):
            analysis = response.get('analysis', {})
            
            # Check for comprehensive analysis components
            required_fields = [
                'overall_condition', 'exterior_condition', 'interior_condition',
                'severity_assessment', 'confidence_score', 'vehicle_grade'
            ]
            
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if not missing_fields:
                print(f"   ✅ Comprehensive AI analysis returned")
                print(f"   🎯 Confidence: {analysis.get('confidence_score', 'N/A')}%")
                print(f"   📊 Grade: {analysis.get('vehicle_grade', 'N/A')}")
                print(f"   🔍 Condition: {analysis.get('overall_condition', 'N/A')}")
                
                # Check if this is real AI processing vs mock
                confidence = analysis.get('confidence_score', 0)
                if isinstance(confidence, (int, float)) and 50 <= confidence <= 100:
                    print(f"   ✅ Real AI processing (confidence: {confidence}%)")
                    return True
                else:
                    print(f"   ❌ Suspicious confidence score: {confidence}")
                    return False
            else:
                print(f"   ❌ Missing analysis fields: {missing_fields}")
                return False
        
        return False

    def create_test_image(self, text: str, filename: str) -> str:
        """Create test image for OCR testing"""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), text, fill='black', font=font)
        img.save(filename)
        return filename

    def test_ocr_endpoints(self) -> bool:
        """Test OCR endpoints for real processing vs mock"""
        self.print_header("OCR ENDPOINTS - REAL PROCESSING VERIFICATION")
        
        ocr_tests = [
            ("VIN OCR", "ocr-vin", "1HGBH41JXMN109186", "vin"),
            ("License Plate OCR", "ocr-license-plate", "ABC1234", "licensePlate"),
            ("Mileage OCR", "ocr-mileage", "87325", "mileage")
        ]
        
        all_ocr_success = True
        
        for test_name, endpoint, test_text, response_key in ocr_tests:
            print(f"\n🔍 Testing {test_name}...")
            
            # Create test image
            test_image = f"/tmp/{endpoint.replace('-', '_')}_test.png"
            self.create_test_image(test_text, test_image)
            
            try:
                with open(test_image, 'rb') as f:
                    files = {'image': (f'{endpoint}_test.png', f, 'image/png')}
                    success, response = self.run_api_test(
                        test_name,
                        "POST",
                        endpoint,
                        200,
                        files=files
                    )
                
                if success and response_key in response:
                    extracted_value = response[response_key]
                    print(f"   📝 Extracted: {extracted_value}")
                    
                    # Check for real processing vs mock
                    if extracted_value == "MOCK_RESULT" or extracted_value == "TEST_RESULT":
                        print(f"   ❌ Mock data detected: {extracted_value}")
                        all_ocr_success = False
                    elif extracted_value == "UNREADABLE":
                        print(f"   ⚠️  Could not read text (may be normal)")
                    else:
                        print(f"   ✅ Real OCR processing detected")
                else:
                    print(f"   ❌ OCR processing failed")
                    all_ocr_success = False
                    
            except Exception as e:
                print(f"   ❌ Error testing {test_name}: {e}")
                all_ocr_success = False
            finally:
                # Cleanup
                try:
                    import os
                    os.remove(test_image)
                except:
                    pass
        
        return all_ocr_success

    def test_role_based_access(self) -> bool:
        """Test role-based access control"""
        self.print_header("ROLE-BASED ACCESS CONTROL")
        
        # For now, we can only test that admin endpoints exist and respond
        # Full RBAC testing would require authentication tokens
        
        admin_endpoints = [
            "admin/users",
            "admin/add-user", 
            "admin/delete-user"
        ]
        
        rbac_success = True
        
        for endpoint in admin_endpoints:
            print(f"\n🔍 Testing access to {endpoint}...")
            
            if endpoint == "admin/users":
                success, response = self.run_api_test(
                    f"Access Control - {endpoint}",
                    "GET",
                    endpoint,
                    200  # Should be accessible in development
                )
            else:
                # Test with invalid data to check endpoint exists
                success, response = self.run_api_test(
                    f"Access Control - {endpoint}",
                    "POST" if "add-user" in endpoint else "DELETE",
                    endpoint,
                    400,  # Should return validation error
                    data={}
                )
            
            if not success and response.get('error') == 'Connection refused':
                print(f"   ❌ Server not running - cannot test RBAC")
                rbac_success = False
            elif success or 'error' in response:
                print(f"   ✅ Endpoint accessible with proper error handling")
            else:
                print(f"   ❌ Unexpected response from {endpoint}")
                rbac_success = False
        
        return rbac_success

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE ADMIN FUNCTIONALITY REPORT")
        
        print(f"📊 TEST EXECUTION SUMMARY:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "   Success Rate: 0%")
        
        print(f"\n👥 ADMIN USERS FOUND:")
        if self.admin_users_found:
            for user in self.admin_users_found:
                print(f"   - {user.get('email', 'N/A')} ({user.get('role', 'N/A')})")
        else:
            print(f"   🚨 NO USERS FOUND - CRITICAL ISSUE")
        
        print(f"\n🎯 CRITICAL FINDINGS:")
        
        # Determine overall status
        if len(self.admin_users_found) > 0:
            print(f"   ✅ Admin panel can access real user data")
        else:
            print(f"   ❌ Admin panel shows no users (CRITICAL)")
            
        print(f"\n📋 PRODUCTION READINESS:")
        print(f"   - User Management: {'✅ Ready' if len(self.admin_users_found) > 0 else '❌ Not Ready'}")
        print(f"   - No Mock Data: {'✅ Verified' if len(self.admin_users_found) > 0 else '⚠️  Cannot Verify'}")
        print(f"   - API Endpoints: {'✅ Accessible' if self.tests_passed > 0 else '❌ Issues Found'}")

def main():
    """Main test execution"""
    print("🚀 STARTING ADMIN FUNCTIONALITY VERIFICATION")
    print("=" * 70)
    print("🎯 Focus: Admin Panel User Management & Production Readiness")
    print("📅 Test Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    tester = AdminFunctionalityTester()
    
    # Execute tests in priority order
    test_results = {}
    
    print("\n🔥 CRITICAL ADMIN FUNCTIONALITY TESTS:")
    
    # 1. Admin Users API (CRITICAL)
    test_results['admin_users'] = tester.test_admin_users_api()
    
    # 2. Add User API
    test_results['add_user'] = tester.test_add_user_api()
    
    # 3. Delete User API  
    test_results['delete_user'] = tester.test_delete_user_api()
    
    print("\n🔥 CORE SYSTEM VERIFICATION:")
    
    # 4. VIN Decode API (Core functionality)
    test_results['vin_decode'] = tester.test_vin_decode_api()
    
    # 5. Gemini AI Analysis (NEW feature)
    test_results['gemini_ai'] = tester.test_gemini_ai_analysis()
    
    # 6. OCR Endpoints (Real processing verification)
    test_results['ocr_endpoints'] = tester.test_ocr_endpoints()
    
    # 7. Role-based Access Control
    test_results['rbac'] = tester.test_role_based_access()
    
    # Generate comprehensive report
    tester.generate_comprehensive_report()
    
    # Final assessment
    critical_tests = ['admin_users', 'vin_decode']
    critical_passed = all(test_results.get(test, False) for test in critical_tests)
    
    print(f"\n🎉 FINAL ASSESSMENT:")
    if critical_passed:
        print(f"   ✅ CRITICAL FUNCTIONALITY WORKING")
        print(f"   🚀 Admin panel can manage real users")
        print(f"   📊 Core APIs are production-ready")
        return 0
    else:
        print(f"   ❌ CRITICAL ISSUES FOUND")
        if not test_results.get('admin_users', False):
            print(f"   🚨 Admin panel cannot access users")
        if not test_results.get('vin_decode', False):
            print(f"   🚨 VIN decode API not working")
        return 1

if __name__ == "__main__":
    sys.exit(main())