#!/usr/bin/env python3
"""
CRITICAL ADMIN PANEL VERIFICATION TEST
Testing the Firebase Admin SDK fix for user management functionality.

FOCUS: Verify that admin panel now shows real users from Firestore instead of empty array.
"""

import requests
import json
import time
import random
import string

# Configuration
BASE_URL = "http://localhost:1111"
API_BASE = f"{BASE_URL}/api"

def generate_test_email():
    """Generate a unique test email"""
    random_id = ''.join(random.choices(string.digits, k=10))
    return f"test-user-{random_id}@priority-appraisal.com"

def test_admin_users_api():
    """Test the GET /api/admin/users endpoint"""
    print("🔍 Testing Admin Users API...")
    print(f"Making request to: {API_BASE}/admin/users")
    
    try:
        response = requests.get(f"{API_BASE}/admin/users", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {json.dumps(data, indent=2)}")
            
            users = data.get('users', [])
            print(f"📊 Found {len(users)} users in the system")
            
            if len(users) > 0:
                print("✅ SUCCESS: Admin panel is showing real users from Firestore!")
                for i, user in enumerate(users):
                    print(f"  User {i+1}: {user.get('email', 'No email')} (Role: {user.get('role', 'No role')})")
                return True, users
            else:
                print("⚠️  Admin panel returns empty users array")
                return False, []
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, []
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False, []

def test_add_user_api():
    """Test the POST /api/admin/add-user endpoint"""
    print("\n🔍 Testing Add User API...")
    
    test_email = generate_test_email()
    test_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "role": "sales"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/admin/add-user",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User created successfully: {json.dumps(data, indent=2)}")
            return True, data.get('uid'), test_email
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None, test_email
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False, None, test_email

def test_delete_user_api(uid):
    """Test the DELETE /api/admin/delete-user endpoint"""
    print(f"\n🔍 Testing Delete User API for UID: {uid}")
    
    try:
        response = requests.delete(
            f"{API_BASE}/admin/delete-user",
            json={"uid": uid},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User deleted successfully: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Failed to delete user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 CRITICAL ADMIN PANEL VERIFICATION TEST")
    print("=" * 60)
    print("Testing Firebase Admin SDK fix for user management")
    print("Expected: Admin panel should show real users from Firestore")
    print("=" * 60)
    
    # Test 1: Check current users in admin panel
    print("\n📋 STEP 1: Check existing users in admin panel")
    users_working, initial_users = test_admin_users_api()
    initial_count = len(initial_users)
    
    # Test 2: Create a new test user
    print("\n📋 STEP 2: Create a new test user")
    add_working, new_uid, test_email = test_add_user_api()
    
    if add_working and new_uid:
        print(f"✅ Test user created with UID: {new_uid}")
        
        # Wait a moment for Firestore to sync
        print("⏳ Waiting 3 seconds for Firestore sync...")
        time.sleep(3)
        
        # Test 3: Verify the new user appears in the list
        print("\n📋 STEP 3: Verify new user appears in admin panel")
        users_working_after, updated_users = test_admin_users_api()
        updated_count = len(updated_users)
        
        if updated_count > initial_count:
            print(f"✅ SUCCESS: User count increased from {initial_count} to {updated_count}")
            print("✅ CRITICAL FIX VERIFIED: Admin panel is now showing real users!")
            
            # Find the new user in the list
            new_user_found = False
            for user in updated_users:
                if user.get('email') == test_email:
                    new_user_found = True
                    print(f"✅ New user found in list: {user.get('email')} (UID: {user.get('uid')})")
                    break
            
            if not new_user_found:
                print(f"⚠️  New user {test_email} not found in updated list")
        else:
            print(f"❌ CRITICAL ISSUE: User count did not increase ({initial_count} → {updated_count})")
            print("❌ Admin panel still not showing newly created users")
        
        # Test 4: Clean up - delete the test user
        print("\n📋 STEP 4: Clean up test user")
        delete_working = test_delete_user_api(new_uid)
        
        if delete_working:
            print("✅ Test user cleaned up successfully")
        else:
            print(f"⚠️  Failed to clean up test user {test_email} (UID: {new_uid})")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    if users_working and initial_count > 0:
        print("✅ CRITICAL SUCCESS: Admin Users API is working and showing real users!")
        print(f"✅ Found {initial_count} existing users in Firestore")
        print("✅ Firebase Admin SDK fix is working correctly")
        
        # Show existing users
        if initial_users:
            print("\n📋 Existing users in the system:")
            for i, user in enumerate(initial_users):
                email = user.get('email', 'No email')
                role = user.get('role', 'No role')
                uid = user.get('uid', 'No UID')
                created = user.get('createdAt', 'No date')
                print(f"  {i+1}. {email} (Role: {role}, UID: {uid[:8]}...)")
    
    elif users_working and initial_count == 0:
        print("⚠️  Admin Users API is accessible but returns empty array")
        print("⚠️  This could mean:")
        print("   - No users exist in Firestore yet")
        print("   - Firestore security rules are still blocking access")
        print("   - Firebase Admin SDK configuration needs adjustment")
        
        if add_working:
            print("✅ However, Add User API is working - users can be created")
        else:
            print("❌ Add User API is also failing - complete admin functionality broken")
    
    else:
        print("❌ CRITICAL FAILURE: Admin Users API is not working")
        print("❌ Firebase Admin SDK fix did not resolve the issue")
        print("❌ Admin panel user management is still broken")
    
    print("\n🔧 RECOMMENDATIONS:")
    if users_working and initial_count > 0:
        print("✅ No action needed - admin functionality is working correctly!")
        print("✅ The Firebase Admin SDK fix has successfully resolved the issue")
    else:
        print("🔍 Check Firestore security rules for server-side access")
        print("🔍 Verify Firebase Admin SDK credentials are properly configured")
        print("🔍 Ensure Firestore 'users' collection exists and is accessible")
        print("🔍 Check server logs for detailed error messages")

if __name__ == "__main__":
    main()