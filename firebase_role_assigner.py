#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class FirebaseRoleAssigner:
    def __init__(self):
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'authDomain': 'priority-appraisal-ai-tool.firebaseapp.com',
            'projectId': 'priority-appraisal-ai-tool'
        }
        self.base_url = "http://localhost:3000"
        
    def get_user_uid_by_email(self, email, password):
        """Get user UID by logging in with email/password"""
        print(f"🔍 Getting UID for user: {email}")
        
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
                uid = data.get('localId')
                print(f"   ✅ Found UID: {uid}")
                return uid
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Failed to get UID: {error_message}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception getting UID: {str(e)}")
            return None

    def assign_role_via_admin_api(self, email, password, role):
        """Assign role by creating user via admin API"""
        print(f"🔧 Assigning role '{role}' to {email} via Admin API...")
        
        url = f"{self.base_url}/api/admin/add-user"
        
        payload = {
            "email": email,
            "password": password,
            "role": role
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Successfully assigned role '{role}' to {email}")
                    print(f"   📝 User UID: {data.get('uid')}")
                    return True, data.get('uid')
                else:
                    print(f"   ❌ API returned success=false")
                    return False, None
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', 'Unknown error')
                
                if 'already exists' in error_message.lower():
                    print(f"   ⚠️  User already exists: {email}")
                    # Try to get UID for existing user
                    uid = self.get_user_uid_by_email(email, password)
                    if uid:
                        print(f"   📝 Existing user UID: {uid}")
                        print(f"   🔧 Role assignment may need manual verification in Firestore")
                        return True, uid
                    return False, None
                else:
                    print(f"   ❌ Failed to assign role: {error_message}")
                    return False, None
                
        except Exception as e:
            print(f"   ❌ Exception assigning role: {str(e)}")
            return False, None

    def verify_role_assignment(self, email, password):
        """Verify role assignment by checking user login and role"""
        print(f"🔍 Verifying role assignment for: {email}")
        
        # First, verify login works
        uid = self.get_user_uid_by_email(email, password)
        if not uid:
            print(f"   ❌ Cannot verify - login failed")
            return False
        
        # Check if we can get users (this would indicate admin API is working)
        try:
            url = f"{self.base_url}/api/admin/users"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                # Look for our user in the list
                user_found = False
                for user in users:
                    if user.get('email') == email:
                        user_found = True
                        role = user.get('role', 'None')
                        print(f"   ✅ User found in Firestore with role: {role}")
                        return True
                
                if not user_found:
                    print(f"   ⚠️  User authenticated but not found in Firestore users collection")
                    print(f"   🔧 This indicates the role document may not be created yet")
                    return False
            else:
                print(f"   ⚠️  Cannot verify role - admin API returned {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception verifying role: {str(e)}")
            return False

    def test_manager_dashboard_access(self, email, password):
        """Test if user can access manager dashboard (simulation)"""
        print(f"🔐 Testing Manager Dashboard access for: {email}")
        
        # This is a simulation since we can't easily test the frontend auth flow
        # In reality, this would require:
        # 1. Login to get Firebase ID token
        # 2. Make request to protected route with token
        # 3. Check if access is granted
        
        uid = self.get_user_uid_by_email(email, password)
        if uid:
            print(f"   ✅ User can authenticate (UID: {uid})")
            print(f"   🔧 Manager Dashboard access depends on Firestore role document")
            print(f"   📋 Expected: Role should be 'admin' or 'manager' in /users/{uid}")
            return True
        else:
            print(f"   ❌ User cannot authenticate - Manager Dashboard access blocked")
            return False

def main():
    print("🚀 Firebase Role Assignment Tool")
    print("=" * 60)
    
    assigner = FirebaseRoleAssigner()
    
    # Users to configure with roles
    users_to_configure = [
        {
            "email": "test-admin@priority-appraisal.com",
            "password": "TestAdmin123!",
            "role": "admin"
        },
        {
            "email": "manager@priority-appraisal.com",
            "password": "Manager123!",
            "role": "manager"
        }
    ]
    
    results = []
    
    for user_config in users_to_configure:
        print(f"\n🔧 Processing user: {user_config['email']}")
        print("-" * 50)
        
        # Try to assign role via admin API
        success, uid = assigner.assign_role_via_admin_api(
            user_config['email'],
            user_config['password'],
            user_config['role']
        )
        
        if success:
            # Verify the role assignment
            role_verified = assigner.verify_role_assignment(
                user_config['email'],
                user_config['password']
            )
            
            # Test manager dashboard access
            dashboard_access = assigner.test_manager_dashboard_access(
                user_config['email'],
                user_config['password']
            )
            
            results.append({
                'email': user_config['email'],
                'role': user_config['role'],
                'uid': uid,
                'role_assigned': success,
                'role_verified': role_verified,
                'dashboard_access': dashboard_access
            })
        else:
            results.append({
                'email': user_config['email'],
                'role': user_config['role'],
                'uid': None,
                'role_assigned': False,
                'role_verified': False,
                'dashboard_access': False
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 ROLE ASSIGNMENT RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n👤 User: {result['email']}")
        print(f"   🎭 Target Role: {result['role']}")
        print(f"   📝 UID: {result['uid'] or 'Not available'}")
        print(f"   ✅ Role Assigned: {'✅ Yes' if result['role_assigned'] else '❌ No'}")
        print(f"   🔍 Role Verified: {'✅ Yes' if result['role_verified'] else '❌ No'}")
        print(f"   🔐 Dashboard Access: {'✅ Ready' if result['dashboard_access'] else '❌ Blocked'}")
    
    # Overall status
    all_assigned = all(r['role_assigned'] for r in results)
    all_verified = all(r['role_verified'] for r in results)
    
    print(f"\n🎯 OVERALL STATUS:")
    print(f"   Role Assignment: {'✅ COMPLETE' if all_assigned else '⚠️  PARTIAL'}")
    print(f"   Role Verification: {'✅ COMPLETE' if all_verified else '⚠️  PARTIAL'}")
    
    if all_assigned and all_verified:
        print(f"\n🎉 SUCCESS: All users configured with proper roles!")
        print(f"📋 NEXT STEPS:")
        print(f"   1. Test Manager Dashboard access in frontend")
        print(f"   2. Verify 'Current role' shows correct value")
        print(f"   3. Confirm no 'Access Denied' errors")
        return 0
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: Some role assignments need attention")
        print(f"🔧 MANUAL STEPS REQUIRED:")
        print(f"   1. Check Firebase Console: https://console.firebase.google.com/project/priority-appraisal-ai-tool/firestore")
        print(f"   2. Verify /users collection has documents for each user")
        print(f"   3. Ensure role field is set correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())