#!/usr/bin/env python3

import requests
import sys
import os
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont

class OCRAPITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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

    def run_test(self, name, method, endpoint, expected_status, files=None, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data)
            elif method == 'GET':
                response = requests.get(url)

            success = response.status_code == expected_status
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    result['response'] = response_data
                    self.test_results.append(result)
                    return True, response_data
                except:
                    result['response'] = {}
                    self.test_results.append(result)
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                    result['error'] = error_data
                except:
                    print(f"   Error Text: {response.text}")
                    result['error'] = response.text
                self.test_results.append(result)
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_vin_ocr_with_clear_image(self):
        """Test VIN OCR with a clear image containing a valid VIN"""
        print("\n📸 Creating test image with clear VIN...")
        test_image = self.create_test_image_with_text("1HGBH41JXMN109186", "/tmp/clear_vin.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_vin.png', f, 'image/png')}
            success, response = self.run_test(
                "VIN OCR with Clear VIN Image",
                "POST",
                "api/ocr-vin",
                200,
                files=files
            )
        
        # Clean up
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

    def test_vin_ocr_no_image(self):
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

    def test_license_plate_ocr_with_clear_image(self):
        """Test License Plate OCR with a clear image containing a license plate"""
        print("\n📸 Creating test image with clear license plate...")
        test_image = self.create_test_image_with_text("ABC1234", "/tmp/clear_plate.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_plate.png', f, 'image/png')}
            success, response = self.run_test(
                "License Plate OCR with Clear Plate Image",
                "POST",
                "api/ocr-license-plate",
                200,
                files=files
            )
        
        # Clean up
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

    def test_license_plate_ocr_no_image(self):
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
    def test_mileage_ocr_with_clear_image(self):
        """Test Mileage OCR with a clear image containing readable numbers"""
        print("\n📸 Creating test image with clear mileage...")
        test_image = self.create_test_image_with_text("87325", "/tmp/clear_mileage.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_mileage.png', f, 'image/png')}
            success, response = self.run_test(
                "Mileage OCR with Clear Mileage Image",
                "POST",
                "api/ocr-mileage",
                200,
                files=files
            )
        
        # Clean up
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

    def test_mileage_ocr_with_unclear_image(self):
        """Test Mileage OCR with an unclear/empty image"""
        print("\n📸 Creating test image with unclear content...")
        # Create a mostly black image (unclear)
        img = Image.new('RGB', (400, 200), color='black')
        draw = ImageDraw.Draw(img)
        # Add some noise but no clear numbers
        draw.text((50, 80), "###@@@", fill='gray')
        test_image = "/tmp/unclear_image.png"
        img.save(test_image)
        
        with open(test_image, 'rb') as f:
            files = {'image': ('unclear_image.png', f, 'image/png')}
            success, response = self.run_test(
                "Mileage OCR with Unclear Image",
                "POST",
                "api/ocr-mileage",
                200,
                files=files
            )
        
        # Clean up
        os.remove(test_image)
        
        if success and 'mileage' in response:
            mileage = response['mileage']
            if mileage == "UNREADABLE":
                print(f"   ✅ Correctly returned UNREADABLE for unclear image")
                return True
            else:
                print(f"   ⚠️  Expected UNREADABLE but got: {mileage}")
                return False
        return False

    def test_mileage_ocr_no_image(self):
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

    def test_ocr_with_multiple_numbers(self):
        """Test OCR with image containing multiple numbers"""
        print("\n📸 Creating test image with multiple numbers...")
        test_image = self.create_test_image_with_text("2023 87325 MILES", "/tmp/multiple_numbers.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('multiple_numbers.png', f, 'image/png')}
            success, response = self.run_test(
                "OCR with Multiple Numbers",
                "POST",
                "api/ocr-mileage",
                200,
                files=files
            )
        
        # Clean up
        os.remove(test_image)
        
        if success and 'mileage' in response:
            mileage = response['mileage']
            if mileage == "87325":  # Should extract the mileage, not the year
                print(f"   ✅ Correctly extracted mileage: {mileage} (ignored year 2023)")
                return True
            else:
                print(f"   ⚠️  Expected 87325 but got: {mileage}")
                return False
        return False

    def test_response_time(self):
        """Test OCR API response time"""
        print("\n⏱️  Testing OCR response time...")
        test_image = self.create_test_image_with_text("12345", "/tmp/timing_test.png")
        
        start_time = datetime.now()
        
        with open(test_image, 'rb') as f:
            files = {'image': ('timing_test.png', f, 'image/png')}
            success, response = self.run_test(
                "OCR Response Time",
                "POST",
                "api/ocr-mileage",
                200,
                files=files
            )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Clean up
        os.remove(test_image)
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        if response_time < 5.0:  # Should be under 5 seconds as per requirements
            print(f"   ✅ Response time is acceptable (< 5 seconds)")
            return True
        else:
            print(f"   ⚠️  Response time is too slow (> 5 seconds)")
            return False

def main():
    print("🚀 Starting OCR API Tests...")
    print("=" * 50)
    
    # Setup
    tester = OCRAPITester("http://localhost:3000")
    
    # Run all tests
    tests = [
        tester.test_ocr_no_image,
        tester.test_ocr_with_clear_image,
        tester.test_ocr_with_unclear_image,
        tester.test_ocr_with_multiple_numbers,
        tester.test_response_time,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())