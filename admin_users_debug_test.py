#!/usr/bin/env python3
"""
CRITICAL BUG INVESTIGATION: Admin Panel Users API Testing
Testing the /api/admin/users endpoint that should return users from Firestore
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
def get_backend_url():
    try:
        with open('/app/.env.local', 'r') as f:
            for line in f:
                if line.startswith('NEXT_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    
    # Default to localhost for testing
    return "http://localhost:3000"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def test_admin_users_api():
    """Test the /api/admin/users endpoint that should return Firestore users"""
    print_header("ADMIN USERS API INVESTIGATION")
    
    print(f"🌐 Testing API Base URL: {API_BASE}")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Basic API endpoint accessibility
    print(f"\n🔍 TEST 1: API Endpoint Accessibility")
    try:
        response = requests.get(f"{API_BASE}/admin/users", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print_test_result("API Endpoint Accessible", True)
            
            # Parse response
            try:
                data = response.json()
                print(f"   Response Data: {json.dumps(data, indent=2)}")
                
                # Check if users array exists
                if 'users' in data:
                    users = data['users']
                    print(f"   Users Array Length: {len(users)}")
                    
                    if len(users) == 0:
                        print_test_result("Users Data Retrieved", False, "Users array is empty despite Firestore having data")
                        print("   🚨 CRITICAL ISSUE: API returns empty users array")
                        print("   📋 Expected: Users from Firestore collection should be returned")
                        print("   🔍 Investigating potential causes...")
                        
                        # Additional debugging
                        print(f"\n🔍 DEBUGGING EMPTY USERS RESPONSE:")
                        print(f"   - API endpoint is accessible (200 OK)")
                        print(f"   - Response structure is correct (has 'users' key)")
                        print(f"   - Users array is empty: {users}")
                        print(f"   - This suggests the Firestore query is not returning data")
                        
                    else:
                        print_test_result("Users Data Retrieved", True, f"Found {len(users)} users")
                        
                        # Display user details
                        print(f"\n📋 USER DETAILS:")
                        for i, user in enumerate(users, 1):
                            print(f"   User {i}:")
                            print(f"     - UID: {user.get('uid', 'N/A')}")
                            print(f"     - Email: {user.get('email', 'N/A')}")
                            print(f"     - Role: {user.get('role', 'N/A')}")
                            print(f"     - Created: {user.get('createdAt', 'N/A')}")
                else:
                    print_test_result("Response Structure", False, "Missing 'users' key in response")
                    
            except json.JSONDecodeError as e:
                print_test_result("JSON Response Parsing", False, f"Invalid JSON: {e}")
                print(f"   Raw Response: {response.text[:500]}")
                
        elif response.status_code == 500:
            print_test_result("API Endpoint Accessible", False, "Internal Server Error (500)")
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Error Response: {response.text}")
                
        else:
            print_test_result("API Endpoint Accessible", False, f"HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print_test_result("API Endpoint Accessible", False, "Connection refused - server may not be running")
        print("   🚨 Make sure the Next.js development server is running")
        print("   💡 Try: npm run dev or yarn dev")
        return False
        
    except requests.exceptions.Timeout:
        print_test_result("API Endpoint Accessible", False, "Request timeout")
        return False
        
    except Exception as e:
        print_test_result("API Endpoint Accessible", False, f"Unexpected error: {e}")
        return False
    
    return True

def test_firestore_connection():
    """Test if we can verify Firestore connection indirectly"""
    print_header("FIRESTORE CONNECTION ANALYSIS")
    
    print("🔍 Analyzing potential Firestore connection issues:")
    print("   1. Server-side rendering issue (typeof window === 'undefined')")
    print("   2. Firebase configuration missing or incorrect")
    print("   3. Firestore security rules blocking access")
    print("   4. Collection name mismatch")
    print("   5. Query execution failure")
    
    # Check if we can access other Firebase-related endpoints
    print(f"\n🔍 Testing related Firebase functionality...")
    
    # This would require authentication, but we can test the endpoint structure
    try:
        # Test if the API route exists and returns proper error for unauthenticated requests
        response = requests.get(f"{API_BASE}/admin/users", timeout=5)
        
        if response.status_code == 401:
            print_test_result("Firebase Auth Integration", True, "API properly requires authentication")
        elif response.status_code == 500:
            print_test_result("Firebase Auth Integration", False, "Server error suggests configuration issue")
        elif response.status_code == 200:
            print_test_result("Firebase Auth Integration", True, "API accessible (may be in development mode)")
        else:
            print_test_result("Firebase Auth Integration", False, f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   Error testing Firebase integration: {e}")

def analyze_code_issues():
    """Analyze potential code-level issues based on the implementation"""
    print_header("CODE ANALYSIS")
    
    print("🔍 Analyzing firebase-admin.ts implementation:")
    print("   Key findings from code review:")
    print("   1. ✅ Uses client-side Firebase SDK (not Admin SDK)")
    print("   2. ⚠️  Server-side check: 'typeof window === undefined' returns empty array")
    print("   3. ✅ Proper Firestore query: collection('users') with orderBy('createdAt')")
    print("   4. ✅ Error handling in place")
    print("   5. ⚠️  Potential issue: Server-side rendering limitation")
    
    print(f"\n🚨 CRITICAL FINDING:")
    print(f"   The getAllUsers() function has this check:")
    print(f"   if (typeof window === 'undefined') {{ return []; }}")
    print(f"   ")
    print(f"   This means during server-side rendering (Next.js API routes),")
    print(f"   the function immediately returns an empty array!")
    print(f"   ")
    print(f"   🔧 SOLUTION NEEDED:")
    print(f"   - Remove the server-side check, OR")
    print(f"   - Implement proper Firebase Admin SDK for server-side operations")

def provide_recommendations():
    """Provide specific recommendations to fix the issue"""
    print_header("RECOMMENDATIONS TO FIX THE BUG")
    
    print("🔧 IMMEDIATE FIXES NEEDED:")
    print("   ")
    print("   1. 🎯 PRIMARY ISSUE: Server-side rendering check")
    print("      File: /app/lib/firebase-admin.ts")
    print("      Problem: Lines 50-53 return empty array for server-side calls")
    print("      Fix: Remove or modify the typeof window check")
    print("   ")
    print("   2. 🔄 ALTERNATIVE APPROACH: Use Firebase Admin SDK")
    print("      - Install firebase-admin package")
    print("      - Configure server-side Firebase Admin")
    print("      - Use admin.auth().listUsers() for proper server-side user fetching")
    print("   ")
    print("   3. 🔍 IMMEDIATE TEST:")
    print("      - Comment out lines 50-53 in firebase-admin.ts")
    print("      - Test if users are returned (may need client-side execution)")
    print("   ")
    print("   4. 📋 VERIFICATION STEPS:")
    print("      - Check Firestore console for actual user documents")
    print("      - Verify collection name is exactly 'users'")
    print("      - Check Firestore security rules allow read access")

def main():
    """Main test execution"""
    print("🚀 STARTING ADMIN USERS API DEBUG INVESTIGATION")
    print(f"Target: {API_BASE}/admin/users")
    
    # Run tests
    api_accessible = test_admin_users_api()
    
    if api_accessible:
        test_firestore_connection()
    
    analyze_code_issues()
    provide_recommendations()
    
    print_header("INVESTIGATION COMPLETE")
    print("📋 SUMMARY:")
    print("   🎯 Root Cause: Server-side rendering check in firebase-admin.ts")
    print("   🔧 Fix: Remove typeof window check or implement proper Admin SDK")
    print("   ⚡ Priority: CRITICAL - Admin panel completely non-functional")
    print("   📅 Next Steps: Modify firebase-admin.ts and retest")

if __name__ == "__main__":
    main()