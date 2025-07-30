#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class FirestoreRoleCreator:
    def __init__(self):
        self.firebase_config = {
            'apiKey': 'AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8',
            'authDomain': 'priority-appraisal-ai-tool.firebaseapp.com',
            'projectId': 'priority-appraisal-ai-tool'
        }
        self.base_url = "http://localhost:3000"
        
    def create_firestore_user_document(self, uid, email, role):
        """Create user document in Firestore using REST API"""
        print(f"📝 Creating Firestore document for {email} with role '{role}'...")
        
        # Firestore REST API endpoint
        url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_config['projectId']}/databases/(default)/documents/users/{uid}"
        
        # Document data
        document_data = {
            "fields": {
                "email": {"stringValue": email},
                "role": {"stringValue": role},
                "createdAt": {"timestampValue": datetime.utcnow().isoformat() + "Z"}
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # Try to create the document
            response = requests.patch(url, json=document_data, headers=headers, params={"key": self.firebase_config['apiKey']})
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Successfully created Firestore document")
                print(f"   📍 Path: /users/{uid}")
                print(f"   📊 Data: email={email}, role={role}")
                return True
            else:
                print(f"   ❌ Failed to create document: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📋 Error: {error_data}")
                except:
                    print(f"   📋 Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception creating document: {str(e)}")
            return False

    def verify_firestore_document(self, uid, email):
        """Verify the Firestore document was created"""
        print(f"🔍 Verifying Firestore document for {email}...")
        
        url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_config['projectId']}/databases/(default)/documents/users/{uid}"
        
        try:
            response = requests.get(url, params={"key": self.firebase_config['apiKey']})
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get('fields', {})
                
                stored_email = fields.get('email', {}).get('stringValue', 'N/A')
                stored_role = fields.get('role', {}).get('stringValue', 'N/A')
                
                print(f"   ✅ Document found!")
                print(f"   📧 Email: {stored_email}")
                print(f"   🎭 Role: {stored_role}")
                
                return stored_role != 'N/A'
            else:
                print(f"   ❌ Document not found: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception verifying document: {str(e)}")
            return False

    def test_admin_api_after_role_creation(self):
        """Test admin API to see if it can now find the users"""
        print(f"🔍 Testing Admin API after role creation...")
        
        try:
            url = f"{self.base_url}/api/admin/users"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                print(f"   ✅ Admin API returned {len(users)} users:")
                for user in users:
                    email = user.get('email', 'N/A')
                    role = user.get('role', 'N/A')
                    uid = user.get('uid', 'N/A')
                    print(f"      👤 {email} - Role: {role} - UID: {uid}")
                
                return len(users) > 0
            else:
                print(f"   ❌ Admin API failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception testing admin API: {str(e)}")
            return False

def main():
    print("🚀 Firestore Role Document Creator")
    print("=" * 60)
    
    creator = FirestoreRoleCreator()
    
    # Users with their UIDs (from previous test)
    users_to_create = [
        {
            "uid": "2FsveUKHTlWAZB6ywrL9DzZaaxq2",
            "email": "test-admin@priority-appraisal.com",
            "role": "admin"
        },
        {
            "uid": "TIUKD9BmcnbYaKQLuDzT1xvbLjG3",
            "email": "manager@priority-appraisal.com",
            "role": "manager"
        }
    ]
    
    results = []
    
    for user_config in users_to_create:
        print(f"\n🔧 Processing user: {user_config['email']}")
        print("-" * 50)
        
        # Create Firestore document
        document_created = creator.create_firestore_user_document(
            user_config['uid'],
            user_config['email'],
            user_config['role']
        )
        
        # Verify the document
        document_verified = False
        if document_created:
            time.sleep(1)  # Give Firestore a moment
            document_verified = creator.verify_firestore_document(
                user_config['uid'],
                user_config['email']
            )
        
        results.append({
            'email': user_config['email'],
            'role': user_config['role'],
            'uid': user_config['uid'],
            'document_created': document_created,
            'document_verified': document_verified
        })
    
    # Test admin API
    print(f"\n🔍 Testing Admin API Integration...")
    print("-" * 50)
    admin_api_working = creator.test_admin_api_after_role_creation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 FIRESTORE ROLE CREATION RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n👤 User: {result['email']}")
        print(f"   🎭 Role: {result['role']}")
        print(f"   📝 UID: {result['uid']}")
        print(f"   📄 Document Created: {'✅ Yes' if result['document_created'] else '❌ No'}")
        print(f"   🔍 Document Verified: {'✅ Yes' if result['document_verified'] else '❌ No'}")
    
    print(f"\n🔧 Admin API Integration: {'✅ Working' if admin_api_working else '❌ Not Working'}")
    
    # Overall status
    all_created = all(r['document_created'] for r in results)
    all_verified = all(r['document_verified'] for r in results)
    
    print(f"\n🎯 OVERALL STATUS:")
    print(f"   Document Creation: {'✅ COMPLETE' if all_created else '❌ FAILED'}")
    print(f"   Document Verification: {'✅ COMPLETE' if all_verified else '❌ FAILED'}")
    print(f"   Admin API Integration: {'✅ WORKING' if admin_api_working else '❌ NOT WORKING'}")
    
    if all_created and all_verified and admin_api_working:
        print(f"\n🎉 SUCCESS: All user roles configured in Firestore!")
        print(f"📋 NEXT STEPS:")
        print(f"   1. Test Manager Dashboard access with test-admin@priority-appraisal.com")
        print(f"   2. Verify 'Current role' shows 'admin' instead of 'None'")
        print(f"   3. Confirm Manager Dashboard displays without 'Access Denied' error")
        print(f"   4. Test complete end-to-end integration flow")
        return 0
    else:
        print(f"\n⚠️  ISSUES DETECTED: Role configuration incomplete")
        print(f"🔧 TROUBLESHOOTING:")
        print(f"   1. Check Firestore security rules allow document creation")
        print(f"   2. Verify Firebase project permissions")
        print(f"   3. Consider using Firebase Admin SDK instead of REST API")
        return 1

if __name__ == "__main__":
    sys.exit(main())