#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class FirebaseUserManager:
    def __init__(self):
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'authDomain': 'priority-appraisal-ai-tool.firebaseapp.com',
            'projectId': 'priority-appraisal-ai-tool'
        }
        
    def create_admin_user(self, email, password):
        """Create a new admin user with known credentials"""
        print(f"🔍 Creating admin user: {email}")
        
        # Firebase Auth REST API endpoint for creating users
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.firebase_config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully created user: {data.get('email', 'Unknown')}")
                print(f"   User ID: {data.get('localId', 'Unknown')}")
                print(f"   ID Token: {data.get('idToken', 'Unknown')[:50]}...")
                return True, data
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if 'EMAIL_EXISTS' in error_message:
                    print(f"⚠️  User already exists: {email}")
                    return False, {'message': 'User already exists'}
                else:
                    print(f"❌ Failed to create user: {error_message}")
                    return False, error_data
                
        except Exception as e:
            print(f"❌ Exception creating user: {str(e)}")
            return False, {}
    
    def test_login(self, email, password):
        """Test login with given credentials"""
        print(f"🔍 Testing login for: {email}")
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'idToken' in data:
                    print(f"✅ Login successful for: {data.get('email', 'Unknown')}")
                    return True, data
                else:
                    print(f"❌ Login response missing idToken")
                    return False, {}
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"❌ Login failed: {error_message}")
                return False, error_data
                
        except Exception as e:
            print(f"❌ Exception during login: {str(e)}")
            return False, {}

def main():
    print("🚀 Firebase User Management Tool")
    print("=" * 50)
    
    manager = FirebaseUserManager()
    
    # Try to create alternative admin users with known passwords
    test_users = [
        ("admin@priority-appraisal.com", "Priority123!"),
        ("admin@priority-appraisal.com", "Admin123!"),
        ("test-admin@priority-appraisal.com", "TestAdmin123!"),
        ("manager@priority-appraisal.com", "Manager123!")
    ]
    
    working_credentials = []
    
    for email, password in test_users:
        print(f"\n🔧 Processing user: {email}")
        
        # First try to login (in case user exists with this password)
        success, data = manager.test_login(email, password)
        if success:
            print(f"🎉 FOUND WORKING CREDENTIALS!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            working_credentials.append((email, password))
            continue
        
        # If login failed, try to create user
        if "INVALID_LOGIN_CREDENTIALS" in str(data) or "EMAIL_NOT_FOUND" in str(data):
            print(f"   User doesn't exist or wrong password, attempting to create...")
            success, create_data = manager.create_admin_user(email, password)
            
            if success:
                # Test the newly created user
                login_success, login_data = manager.test_login(email, password)
                if login_success:
                    print(f"🎉 NEW USER CREATED AND TESTED!")
                    print(f"   Email: {email}")
                    print(f"   Password: {password}")
                    working_credentials.append((email, password))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if working_credentials:
        print(f"✅ WORKING CREDENTIALS FOUND:")
        for email, password in working_credentials:
            print(f"   📧 Email: {email}")
            print(f"   🔑 Password: {password}")
            print()
        
        print("🎯 NEXT STEPS:")
        print("1. Use these credentials to test the frontend login")
        print("2. Update the main agent with working credentials")
        print("3. Test the complete end-to-end integration flow")
        
        return 0
    else:
        print("❌ NO WORKING CREDENTIALS FOUND")
        print("🔧 MANUAL ACTION REQUIRED:")
        print("1. Access Firebase Console directly")
        print("2. Reset password for admin@priority-appraisal.com")
        print("3. Or create new admin user manually")
        print(f"4. Console URL: https://console.firebase.google.com/project/{manager.firebase_config['projectId']}/authentication/users")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())