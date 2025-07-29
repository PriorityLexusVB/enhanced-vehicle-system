#!/usr/bin/env python3

import requests
import sys
import os
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont
import json

class VehicleAppraisalAPITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def create_test_image_with_text(self, text, filename):
        """Create a simple test image with text for OCR testing"""
        # Create a white image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Draw the text in black
        draw.text((50, 80), text, fill='black', font=font)
        
        # Save the image
        img.save(filename)
        return filename

    def run_test(self, name, method, endpoint, expected_status, files=None, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                except:
                    print(f"   Error Text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # OCR VIN Tests
    def test_ocr_vin_with_valid_vin(self):
        """Test VIN OCR with a valid VIN number"""
        print("\n📸 Creating test image with valid VIN...")
        test_vin = "1HGBH41JXMN109186"  # Valid VIN format
        test_image = self.create_test_image_with_text(test_vin, "/tmp/valid_vin.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('valid_vin.png', f, 'image/png')}
            success, response = self.run_test(
                "OCR VIN with Valid VIN",
                "POST",
                "api/ocr-vin",
                200,
                files=files
            )
        
        os.remove(test_image)
        
        if success and 'vin' in response:
            vin = response['vin']
            if vin != "UNREADABLE" and len(vin) == 17:
                print(f"   ✅ Successfully extracted VIN: {vin}")
                return True
            else:
                print(f"   ⚠️  Unexpected VIN result: {vin}")
                return False
        return False

    def test_ocr_vin_no_image(self):
        """Test VIN OCR endpoint without providing an image"""
        success, response = self.run_test(
            "VIN OCR without Image",
            "POST",
            "api/ocr-vin",
            400
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error: {response['error']}")
            return True
        return False

    # OCR License Plate Tests
    def test_ocr_license_plate_with_valid_plate(self):
        """Test License Plate OCR with a valid plate"""
        print("\n📸 Creating test image with license plate...")
        test_plate = "ABC1234"
        test_image = self.create_test_image_with_text(test_plate, "/tmp/license_plate.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('license_plate.png', f, 'image/png')}
            success, response = self.run_test(
                "OCR License Plate with Valid Plate",
                "POST",
                "api/ocr-license-plate",
                200,
                files=files
            )
        
        os.remove(test_image)
        
        if success and 'licensePlate' in response:
            plate = response['licensePlate']
            if plate != "UNREADABLE" and len(plate) >= 4:
                print(f"   ✅ Successfully extracted license plate: {plate}")
                return True
            else:
                print(f"   ⚠️  Unexpected license plate result: {plate}")
                return False
        return False

    def test_ocr_license_plate_no_image(self):
        """Test License Plate OCR endpoint without providing an image"""
        success, response = self.run_test(
            "License Plate OCR without Image",
            "POST",
            "api/ocr-license-plate",
            400
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error: {response['error']}")
            return True
        return False

    # OCR Mileage Tests
    def test_ocr_mileage_with_clear_image(self):
        """Test OCR with a clear image containing readable numbers"""
        print("\n📸 Creating test image with clear mileage...")
        test_image = self.create_test_image_with_text("87325", "/tmp/clear_mileage.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_mileage.png', f, 'image/png')}
            success, response = self.run_test(
                "OCR Mileage with Clear Image",
                "POST",
                "api/ocr-mileage",
                200,
                files=files
            )
        
        os.remove(test_image)
        
        if success and 'mileage' in response:
            mileage = response['mileage']
            if mileage != "UNREADABLE" and mileage.isdigit():
                print(f"   ✅ Successfully extracted mileage: {mileage}")
                return True
            else:
                print(f"   ⚠️  Unexpected mileage result: {mileage}")
                return False
        return False

    def test_ocr_mileage_no_image(self):
        """Test Mileage OCR endpoint without providing an image"""
        success, response = self.run_test(
            "Mileage OCR without Image",
            "POST",
            "api/ocr-mileage",
            400
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error: {response['error']}")
            return True
        return False

    # VIN Decode Tests
    def test_vin_decode_with_valid_vin(self):
        """Test VIN decode with a valid VIN"""
        test_vin = "1HGBH41JXMN109186"
        success, response = self.run_test(
            "VIN Decode with Valid VIN",
            "POST",
            "api/vin-decode",
            200,
            data={"vin": test_vin}
        )
        
        if success and 'vehicle' in response:
            vehicle = response['vehicle']
            if 'make' in vehicle and 'model' in vehicle and 'year' in vehicle:
                print(f"   ✅ Successfully decoded VIN: {vehicle['make']} {vehicle['model']} {vehicle['year']}")
                return True
            else:
                print(f"   ⚠️  Incomplete vehicle data: {vehicle}")
                return False
        return False

    def test_vin_decode_invalid_vin(self):
        """Test VIN decode with invalid VIN"""
        success, response = self.run_test(
            "VIN Decode with Invalid VIN",
            "POST",
            "api/vin-decode",
            400,
            data={"vin": "INVALID"}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error for invalid VIN: {response['error']}")
            return True
        return False

    def test_vin_decode_no_vin(self):
        """Test VIN decode without providing VIN"""
        success, response = self.run_test(
            "VIN Decode without VIN",
            "POST",
            "api/vin-decode",
            400,
            data={}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error for missing VIN: {response['error']}")
            return True
        return False

    # Admin API Tests
    def test_admin_get_users(self):
        """Test admin endpoint to get users"""
        success, response = self.run_test(
            "Admin Get Users",
            "GET",
            "api/admin/users",
            200
        )
        
        if success and 'users' in response:
            users = response['users']
            print(f"   ✅ Successfully retrieved {len(users)} users")
            return True
        return False

    def test_admin_add_user_valid(self):
        """Test admin endpoint to add a valid user"""
        test_user = {
            "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password": "testpassword123",
            "role": "sales"
        }
        
        success, response = self.run_test(
            "Admin Add Valid User",
            "POST",
            "api/admin/add-user",
            200,
            data=test_user
        )
        
        if success and 'success' in response and response['success']:
            print(f"   ✅ Successfully added user: {test_user['email']}")
            # Store the UID for cleanup
            if 'uid' in response:
                self.test_user_uid = response['uid']
            return True
        return False

    def test_admin_add_user_invalid(self):
        """Test admin endpoint with invalid user data"""
        success, response = self.run_test(
            "Admin Add Invalid User",
            "POST",
            "api/admin/add-user",
            400,
            data={"email": "invalid", "password": "", "role": "invalid_role"}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error for invalid user data: {response['error']}")
            return True
        return False

    def test_admin_delete_user_invalid(self):
        """Test admin endpoint to delete user with invalid UID"""
        success, response = self.run_test(
            "Admin Delete Invalid User",
            "DELETE",
            "api/admin/delete-user",
            400,
            data={"uid": ""}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error for invalid UID: {response['error']}")
            return True
        return False

    def cleanup_test_user(self):
        """Clean up test user if created"""
        if hasattr(self, 'test_user_uid'):
            try:
                success, response = self.run_test(
                    "Cleanup Test User",
                    "DELETE",
                    "api/admin/delete-user",
                    200,
                    data={"uid": self.test_user_uid}
                )
                if success:
                    print(f"   ✅ Successfully cleaned up test user")
            except:
                print(f"   ⚠️  Could not clean up test user")

def main():
    print("🚀 Starting Comprehensive Vehicle Appraisal API Tests...")
    print("=" * 60)
    
    # Setup
    tester = VehicleAppraisalAPITester("http://localhost:3000")
    
    # Run all tests
    tests = [
        # OCR VIN Tests
        tester.test_ocr_vin_no_image,
        tester.test_ocr_vin_with_valid_vin,
        
        # OCR License Plate Tests
        tester.test_ocr_license_plate_no_image,
        tester.test_ocr_license_plate_with_valid_plate,
        
        # OCR Mileage Tests
        tester.test_ocr_mileage_no_image,
        tester.test_ocr_mileage_with_clear_image,
        
        # VIN Decode Tests
        tester.test_vin_decode_no_vin,
        tester.test_vin_decode_invalid_vin,
        tester.test_vin_decode_with_valid_vin,
        
        # Admin API Tests
        tester.test_admin_get_users,
        tester.test_admin_add_user_invalid,
        tester.test_admin_add_user_valid,
        tester.test_admin_delete_user_invalid,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Cleanup
    tester.cleanup_test_user()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())