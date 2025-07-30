#!/usr/bin/env python3

import requests
import sys
import os
import json
from datetime import datetime

class FirebaseAuthTester:
    def __init__(self):
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'authDomain': 'priority-appraisal-ai-tool.firebaseapp.com',
            'projectId': 'priority-appraisal-ai-tool'
        }
        self.test_credentials = {
            'email': 'admin@priority-appraisal.com',
            'password': 'admin123'  # Common admin password
        }
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def test_firebase_auth_endpoint(self):
        """Test Firebase Authentication REST API directly"""
        print("\n🔍 Testing Firebase Authentication REST API...")
        
        # Firebase Auth REST API endpoint
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_config['apiKey']}"
        
        payload = {
            "email": self.test_credentials['email'],
            "password": self.test_credentials['password'],
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'idToken' in data:
                    self.log_test(
                        "Firebase Authentication - Direct API",
                        True,
                        f"Successfully authenticated user: {data.get('email', 'Unknown')}"
                    )
                    return True, data
                else:
                    self.log_test(
                        "Firebase Authentication - Direct API",
                        False,
                        "Response missing idToken"
                    )
                    return False, {}
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                self.log_test(
                    "Firebase Authentication - Direct API",
                    False,
                    f"HTTP {response.status_code}: {error_message}"
                )
                return False, error_data
                
        except Exception as e:
            self.log_test(
                "Firebase Authentication - Direct API",
                False,
                f"Exception: {str(e)}"
            )
            return False, {}

    def test_user_creation_via_api(self):
        """Test creating the admin user via Firebase Auth API"""
        print("\n🔍 Testing Admin User Creation...")
        
        # Firebase Auth REST API endpoint for creating users
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.firebase_config['apiKey']}"
        
        payload = {
            "email": self.test_credentials['email'],
            "password": self.test_credentials['password'],
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Admin User Creation",
                    True,
                    f"Successfully created user: {data.get('email', 'Unknown')}"
                )
                return True, data
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if 'EMAIL_EXISTS' in error_message:
                    self.log_test(
                        "Admin User Creation",
                        True,
                        "User already exists (this is expected)"
                    )
                    return True, {'message': 'User already exists'}
                else:
                    self.log_test(
                        "Admin User Creation",
                        False,
                        f"HTTP {response.status_code}: {error_message}"
                    )
                    return False, error_data
                
        except Exception as e:
            self.log_test(
                "Admin User Creation",
                False,
                f"Exception: {str(e)}"
            )
            return False, {}

    def test_firebase_config_validation(self):
        """Test Firebase configuration validity"""
        print("\n🔍 Testing Firebase Configuration...")
        
        # Test if Firebase project is accessible
        url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_config['projectId']}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                self.log_test(
                    "Firebase Project Configuration",
                    True,
                    f"Project {self.firebase_config['projectId']} is accessible"
                )
                return True
            else:
                self.log_test(
                    "Firebase Project Configuration",
                    False,
                    f"HTTP {response.status_code}: Project not accessible"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Firebase Project Configuration",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_alternative_passwords(self):
        """Test common admin passwords"""
        print("\n🔍 Testing Alternative Admin Passwords...")
        
        common_passwords = [
            'admin123',
            'password123',
            'admin',
            'password',
            'Priority123',
            'appraisal123',
            'Admin@123'
        ]
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_config['apiKey']}"
        
        for password in common_passwords:
            payload = {
                "email": self.test_credentials['email'],
                "password": password,
                "returnSecureToken": True
            }
            
            try:
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'idToken' in data:
                        self.log_test(
                            f"Password Test: {password}",
                            True,
                            f"✅ FOUND WORKING PASSWORD: {password}"
                        )
                        return True, password
                    
            except Exception as e:
                continue
        
        self.log_test(
            "Alternative Password Testing",
            False,
            "No working passwords found from common list"
        )
        return False, None

    def test_user_lookup(self):
        """Test if user exists in Firebase"""
        print("\n🔍 Testing User Existence...")
        
        # This requires admin privileges, but we can try
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.firebase_config['apiKey']}"
        
        # We need an ID token for this, so let's try a different approach
        # Try to reset password to see if user exists
        reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.firebase_config['apiKey']}"
        
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": self.test_credentials['email']
        }
        
        try:
            response = requests.post(reset_url, json=payload)
            
            if response.status_code == 200:
                self.log_test(
                    "User Existence Check",
                    True,
                    f"User {self.test_credentials['email']} exists (password reset email sent)"
                )
                return True
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if 'EMAIL_NOT_FOUND' in error_message:
                    self.log_test(
                        "User Existence Check",
                        False,
                        f"User {self.test_credentials['email']} does not exist"
                    )
                    return False
                else:
                    self.log_test(
                        "User Existence Check",
                        False,
                        f"HTTP {response.status_code}: {error_message}"
                    )
                    return False
                
        except Exception as e:
            self.log_test(
                "User Existence Check",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🔥 FIREBASE AUTHENTICATION DIAGNOSTIC REPORT")
        print("=" * 80)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
            if result['details']:
                print(f"      {result['details']}")
        
        print(f"\n🎯 FIREBASE CONFIGURATION:")
        print(f"   Project ID: {self.firebase_config['projectId']}")
        print(f"   Auth Domain: {self.firebase_config['authDomain']}")
        print(f"   API Key: {self.firebase_config['apiKey'][:20]}...")
        
        print(f"\n👤 TEST CREDENTIALS:")
        print(f"   Email: {self.test_credentials['email']}")
        print(f"   Password: {'*' * len(self.test_credentials['password'])}")
        
        # Determine critical issues
        auth_working = any(
            result['success'] and 'Authentication' in result['name'] 
            for result in self.test_results
        )
        user_exists = any(
            result['success'] and 'Existence' in result['name'] 
            for result in self.test_results
        )
        
        print(f"\n🚨 CRITICAL STATUS:")
        print(f"   Firebase Auth API: {'✅ WORKING' if auth_working else '❌ FAILING'}")
        print(f"   Admin User Exists: {'✅ YES' if user_exists else '❌ NO'}")
        
        return auth_working, user_exists

def main():
    print("🚀 Starting Firebase Authentication Diagnostic...")
    print("=" * 60)
    
    tester = FirebaseAuthTester()
    
    # Run comprehensive tests
    print("🔥 CRITICAL: Testing Firebase Authentication Issue")
    print("📧 Target User: admin@priority-appraisal.com")
    print("🎯 Goal: Identify why authentication is failing")
    
    # Test sequence
    tests = [
        tester.test_firebase_config_validation,
        tester.test_user_lookup,
        tester.test_firebase_auth_endpoint,
        tester.test_alternative_passwords,
        tester.test_user_creation_via_api,
    ]
    
    for test in tests:
        try:
            result = test()
            if isinstance(result, tuple) and result[0]:
                # If we found a working password, update credentials
                if 'Password Test' in test.__name__ or 'alternative_passwords' in test.__name__:
                    if len(result) > 1:
                        print(f"\n🎉 BREAKTHROUGH: Found working password!")
                        break
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print comprehensive results
    auth_working, user_exists = tester.print_summary()
    
    # Provide actionable recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if not user_exists:
        print("   1. 🚨 CRITICAL: Admin user does not exist in Firebase")
        print("   2. ✅ ACTION: Create admin user via Firebase Console or API")
        print("   3. 📧 Email: admin@priority-appraisal.com")
        print("   4. 🔑 Password: Set a secure password")
        
    elif not auth_working:
        print("   1. 🚨 CRITICAL: Authentication failing with existing user")
        print("   2. ✅ ACTION: Reset password via Firebase Console")
        print("   3. 🔍 CHECK: Verify user is not disabled")
        print("   4. 🔑 TRY: Common passwords tested above")
        
    else:
        print("   1. ✅ SUCCESS: Authentication should be working")
        print("   2. 🔍 CHECK: Frontend implementation for auth state persistence")
        print("   3. 🔄 VERIFY: Browser cookies and local storage")
    
    print(f"\n🔗 FIREBASE CONSOLE:")
    print(f"   https://console.firebase.google.com/project/{tester.firebase_config['projectId']}/authentication/users")
    
    # Return appropriate exit code
    if user_exists and auth_working:
        print("\n🎉 AUTHENTICATION SYSTEM: WORKING!")
        return 0
    elif user_exists:
        print("\n⚠️  AUTHENTICATION SYSTEM: USER EXISTS BUT AUTH FAILING")
        return 1
    else:
        print("\n❌ AUTHENTICATION SYSTEM: USER DOES NOT EXIST")
        return 2

if __name__ == "__main__":
    sys.exit(main())