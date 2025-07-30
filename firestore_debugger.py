#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class FirestoreDebugger:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'projectId': 'priority-appraisal-ai-tool'
        }
        
    def create_user_and_debug(self):
        """Create a user and debug the Firestore document creation"""
        print("🔧 Creating user and debugging Firestore integration...")
        
        timestamp = int(time.time())
        test_email = f"debug-user-{timestamp}@test.com"
        test_password = "DebugTest123!"
        test_role = "admin"
        
        print(f"📝 Creating test user: {test_email}")
        
        # Step 1: Create user via admin API
        url = f"{self.base_url}/api/admin/add-user"
        payload = {
            "email": test_email,
            "password": test_password,
            "role": test_role
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    uid = data.get('uid')
                    print(f"   ✅ User created successfully")
                    print(f"   📝 UID: {uid}")
                    print(f"   📧 Email: {data.get('email')}")
                    print(f"   🎭 Role: {data.get('role')}")
                    
                    # Step 2: Wait a moment for Firestore to sync
                    print(f"\n⏳ Waiting 3 seconds for Firestore sync...")
                    time.sleep(3)
                    
                    # Step 3: Check admin API
                    self.check_admin_api()
                    
                    # Step 4: Try to get specific user document
                    self.check_specific_user_document(uid)
                    
                    # Step 5: Test authentication
                    self.test_user_authentication(test_email, test_password)
                    
                    return True
                else:
                    print(f"   ❌ API returned success=false")
                    return False
            else:
                error_data = response.json() if response.content else {}
                print(f"   ❌ Failed to create user: {error_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception creating user: {str(e)}")
            return False

    def check_admin_api(self):
        """Check what the admin API returns"""
        print(f"\n🔍 Checking Admin API response...")
        
        try:
            url = f"{self.base_url}/api/admin/users"
            response = requests.get(url)
            
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                print(f"   📋 Response: {json.dumps(data, indent=2)}")
                print(f"   👥 Users found: {len(users)}")
                
                for i, user in enumerate(users):
                    print(f"      User {i+1}:")
                    print(f"         📧 Email: {user.get('email', 'N/A')}")
                    print(f"         🎭 Role: {user.get('role', 'N/A')}")
                    print(f"         📝 UID: {user.get('uid', 'N/A')}")
                    print(f"         📅 Created: {user.get('createdAt', 'N/A')}")
            else:
                print(f"   ❌ Admin API failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📋 Error: {error_data}")
                except:
                    print(f"   📋 Error text: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exception checking admin API: {str(e)}")

    def check_specific_user_document(self, uid):
        """Try to check a specific user document via Firestore REST API"""
        print(f"\n🔍 Checking specific user document for UID: {uid}")
        
        # Try with authentication
        url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_config['projectId']}/databases/(default)/documents/users/{uid}"
        
        try:
            response = requests.get(url, params={"key": self.firebase_config['apiKey']})
            
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Document found!")
                print(f"   📋 Document data: {json.dumps(data, indent=2)}")
            elif response.status_code == 404:
                print(f"   ❌ Document not found (404)")
                print(f"   🔧 This suggests the Firestore document was not created")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📋 Error: {error_data}")
                except:
                    print(f"   📋 Error text: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exception checking document: {str(e)}")

    def test_user_authentication(self, email, password):
        """Test if the created user can authenticate"""
        print(f"\n🔐 Testing authentication for: {email}")
        
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
                print(f"   ✅ Authentication successful!")
                print(f"   📝 UID: {data.get('localId')}")
                print(f"   📧 Email: {data.get('email')}")
                return True
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Authentication failed: {error_message}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception during authentication: {str(e)}")
            return False

    def check_firestore_security_rules(self):
        """Check if Firestore security rules might be blocking document creation"""
        print(f"\n🔒 Checking Firestore security rules...")
        
        # This is informational - we can't actually check the rules via API
        print(f"   📋 Potential issues:")
        print(f"      1. Firestore security rules may require authentication")
        print(f"      2. Rules may not allow document creation from server-side")
        print(f"      3. The admin API might be running client-side instead of server-side")
        print(f"   🔧 Suggested fixes:")
        print(f"      1. Update Firestore rules to allow authenticated writes")
        print(f"      2. Use Firebase Admin SDK instead of client SDK")
        print(f"      3. Check if documents are created but not readable")

def main():
    print("🚀 Firestore Integration Debugger")
    print("=" * 60)
    
    debugger = FirestoreDebugger()
    
    # Run comprehensive debugging
    success = debugger.create_user_and_debug()
    
    # Check security rules
    debugger.check_firestore_security_rules()
    
    print("\n" + "=" * 80)
    print("📊 DEBUGGING SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ User creation via admin API is working")
        print("🔍 Check the detailed logs above to identify Firestore issues")
    else:
        print("❌ User creation via admin API failed")
    
    print("\n🎯 LIKELY ROOT CAUSE:")
    print("   The admin API creates users in Firebase Auth successfully,")
    print("   but the Firestore document creation is failing silently.")
    print("   This could be due to:")
    print("   1. Firestore security rules blocking writes")
    print("   2. Client-side Firebase SDK limitations")
    print("   3. Missing Firebase Admin SDK configuration")
    
    print("\n🔧 RECOMMENDED SOLUTION:")
    print("   1. Update Firestore security rules to allow authenticated writes")
    print("   2. Or manually create the role documents in Firebase Console")
    print("   3. Or implement proper Firebase Admin SDK")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())