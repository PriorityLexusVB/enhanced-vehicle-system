#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class DirectRoleAssigner:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        
    def create_new_users_with_roles(self):
        """Create new users with proper roles using admin API"""
        print("🔧 Creating new users with proper roles...")
        
        # Create unique test users to avoid conflicts
        timestamp = int(time.time())
        
        users_to_create = [
            {
                "email": f"admin-{timestamp}@priority-appraisal.com",
                "password": "AdminTest123!",
                "role": "admin",
                "original_email": "test-admin@priority-appraisal.com"
            },
            {
                "email": f"manager-{timestamp}@priority-appraisal.com", 
                "password": "ManagerTest123!",
                "role": "manager",
                "original_email": "manager@priority-appraisal.com"
            }
        ]
        
        created_users = []
        
        for user_config in users_to_create:
            print(f"\n📝 Creating user: {user_config['email']}")
            
            url = f"{self.base_url}/api/admin/add-user"
            payload = {
                "email": user_config['email'],
                "password": user_config['password'],
                "role": user_config['role']
            }
            
            try:
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ Successfully created user with role '{user_config['role']}'")
                        print(f"   📝 UID: {data.get('uid')}")
                        print(f"   📧 Email: {data.get('email')}")
                        
                        created_users.append({
                            'email': user_config['email'],
                            'password': user_config['password'],
                            'role': user_config['role'],
                            'uid': data.get('uid'),
                            'original_email': user_config['original_email']
                        })
                    else:
                        print(f"   ❌ API returned success=false")
                else:
                    error_data = response.json() if response.content else {}
                    print(f"   ❌ Failed to create user: {error_data.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Exception creating user: {str(e)}")
        
        return created_users

    def verify_users_in_firestore(self):
        """Verify users are properly stored in Firestore via admin API"""
        print(f"\n🔍 Verifying users in Firestore...")
        
        try:
            url = f"{self.base_url}/api/admin/users"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                print(f"   ✅ Found {len(users)} users in Firestore:")
                
                admin_users = []
                manager_users = []
                
                for user in users:
                    email = user.get('email', 'N/A')
                    role = user.get('role', 'N/A')
                    uid = user.get('uid', 'N/A')
                    
                    print(f"      👤 {email}")
                    print(f"         🎭 Role: {role}")
                    print(f"         📝 UID: {uid}")
                    
                    if role == 'admin':
                        admin_users.append(user)
                    elif role == 'manager':
                        manager_users.append(user)
                
                return {
                    'total_users': len(users),
                    'admin_users': admin_users,
                    'manager_users': manager_users,
                    'all_users': users
                }
            else:
                print(f"   ❌ Failed to get users: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception getting users: {str(e)}")
            return None

    def test_login_with_new_credentials(self, email, password):
        """Test login with new credentials"""
        print(f"🔐 Testing login for: {email}")
        
        firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8'
        }
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login successful!")
                print(f"   📝 UID: {data.get('localId')}")
                return True, data.get('localId')
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Login failed: {error_message}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Exception during login: {str(e)}")
            return False, None

def main():
    print("🚀 Direct Role Assignment via Admin API")
    print("=" * 60)
    
    assigner = DirectRoleAssigner()
    
    # Step 1: Create new users with proper roles
    print("\n📝 STEP 1: Creating users with roles...")
    created_users = assigner.create_new_users_with_roles()
    
    if not created_users:
        print("❌ No users were created successfully")
        return 1
    
    # Step 2: Verify users are in Firestore
    print("\n🔍 STEP 2: Verifying Firestore integration...")
    firestore_data = assigner.verify_users_in_firestore()
    
    if not firestore_data:
        print("❌ Could not verify Firestore integration")
        return 1
    
    # Step 3: Test login with new credentials
    print("\n🔐 STEP 3: Testing authentication...")
    login_results = []
    
    for user in created_users:
        success, uid = assigner.test_login_with_new_credentials(user['email'], user['password'])
        login_results.append({
            'email': user['email'],
            'role': user['role'],
            'login_success': success,
            'uid': uid
        })
    
    # Print comprehensive summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE ROLE ASSIGNMENT RESULTS")
    print("=" * 80)
    
    print(f"\n🎯 FIRESTORE STATUS:")
    print(f"   Total Users: {firestore_data['total_users']}")
    print(f"   Admin Users: {len(firestore_data['admin_users'])}")
    print(f"   Manager Users: {len(firestore_data['manager_users'])}")
    
    print(f"\n👤 CREATED USERS:")
    for user in created_users:
        print(f"   📧 {user['email']}")
        print(f"      🎭 Role: {user['role']}")
        print(f"      🔑 Password: {user['password']}")
        print(f"      📝 UID: {user['uid']}")
        print(f"      🔄 Replaces: {user['original_email']}")
    
    print(f"\n🔐 AUTHENTICATION RESULTS:")
    for result in login_results:
        status = "✅ Working" if result['login_success'] else "❌ Failed"
        print(f"   {status} - {result['email']} ({result['role']})")
    
    # Check if we have working admin credentials
    working_admin = None
    working_manager = None
    
    for user in created_users:
        for result in login_results:
            if user['email'] == result['email'] and result['login_success']:
                if user['role'] == 'admin':
                    working_admin = user
                elif user['role'] == 'manager':
                    working_manager = user
    
    print(f"\n🎉 FINAL RESULTS:")
    if working_admin and working_manager:
        print(f"✅ SUCCESS: Working credentials created for both roles!")
        print(f"\n📋 USE THESE CREDENTIALS FOR MANAGER DASHBOARD TESTING:")
        print(f"   🔑 Admin User:")
        print(f"      Email: {working_admin['email']}")
        print(f"      Password: {working_admin['password']}")
        print(f"   🔑 Manager User:")
        print(f"      Email: {working_manager['email']}")
        print(f"      Password: {working_manager['password']}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Use admin credentials to test Manager Dashboard access")
        print(f"   2. Verify 'Current role' shows 'admin' instead of 'None'")
        print(f"   3. Confirm Manager Dashboard displays without 'Access Denied' error")
        print(f"   4. Test complete end-to-end integration flow")
        
        return 0
    else:
        print(f"⚠️  PARTIAL SUCCESS: Some credentials may not be working")
        return 1

if __name__ == "__main__":
    sys.exit(main())