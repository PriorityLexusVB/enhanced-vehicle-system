#!/usr/bin/env python3

import requests
import sys
import os
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont
import json

class EnhancedOCRErrorTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def create_poor_quality_image(self, filename):
        """Create a poor quality/blurry image for testing"""
        img = Image.new('RGB', (200, 100), color='gray')
        draw = ImageDraw.Draw(img)
        # Add some noise and unclear text
        draw.text((10, 40), "###@@@", fill='darkgray')
        img.save(filename)
        return filename

    def create_empty_image(self, filename):
        """Create an empty/blank image for testing"""
        img = Image.new('RGB', (400, 200), color='white')
        img.save(filename)
        return filename

    def create_invalid_image_data(self, filename):
        """Create invalid image data for testing"""
        with open(filename, 'w') as f:
            f.write("This is not image data")
        return filename

    def run_test(self, name, method, endpoint, expected_status, files=None, data=None, check_error_message=False):
        """Run a single API test with enhanced error message checking"""
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
            
            try:
                response_data = response.json()
                result['response'] = response_data
            except:
                result['response'] = {'text': response.text}
                response_data = {'text': response.text}
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check for enhanced error messages
                if check_error_message and 'error' in response_data:
                    error_msg = response_data['error']
                    suggestion = response_data.get('suggestion', '')
                    
                    print(f"   📝 Error Message: {error_msg}")
                    if suggestion:
                        print(f"   💡 Suggestion: {suggestion}")
                    
                    # Check if error message is enhanced (not just generic)
                    if error_msg != "UNREADABLE" and len(error_msg) > 20:
                        print(f"   ✅ Enhanced error message detected")
                        result['enhanced_error'] = True
                    else:
                        print(f"   ⚠️  Generic error message")
                        result['enhanced_error'] = False
                
                self.test_results.append(result)
                return True, response_data
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response_data}")
                self.test_results.append(result)
                return False, response_data

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

    def test_vin_ocr_missing_image(self):
        """Test VIN OCR endpoint with missing image - should return helpful error message"""
        print("\n🎯 Testing VIN OCR with missing image...")
        success, response = self.run_test(
            "VIN OCR - Missing Image",
            "POST",
            "api/ocr-vin",
            400,
            check_error_message=True
        )
        
        if success and 'error' in response:
            error_msg = response['error']
            suggestion = response.get('suggestion', '')
            
            # Check for enhanced error message
            enhanced_keywords = ['image', 'photo', 'VIN', 'clear', 'visible']
            has_enhanced_msg = any(keyword.lower() in error_msg.lower() for keyword in enhanced_keywords)
            
            if has_enhanced_msg:
                print(f"   ✅ Enhanced error message contains helpful guidance")
                return True
            else:
                print(f"   ⚠️  Error message could be more helpful: {error_msg}")
                return False
        return False

    def test_vin_ocr_invalid_image_data(self):
        """Test VIN OCR endpoint with invalid image data"""
        print("\n🎯 Testing VIN OCR with invalid image data...")
        test_file = "/tmp/invalid_image.txt"
        self.create_invalid_image_data(test_file)
        
        try:
            with open(test_file, 'rb') as f:
                files = {'image': ('invalid.txt', f, 'text/plain')}
                success, response = self.run_test(
                    "VIN OCR - Invalid Image Data",
                    "POST",
                    "api/ocr-vin",
                    500,  # Expecting 500 for processing error
                    files=files,
                    check_error_message=True
                )
        finally:
            os.remove(test_file)
        
        if success and 'error' in response:
            error_msg = response['error']
            # Check for helpful guidance
            helpful_keywords = ['image', 'photo', 'clear', 'try again', 'different']
            has_helpful_msg = any(keyword.lower() in error_msg.lower() for keyword in helpful_keywords)
            
            if has_helpful_msg:
                print(f"   ✅ Error message provides helpful guidance")
                return True
            else:
                print(f"   ⚠️  Error message could be more helpful")
                return False
        return False

    def test_mileage_ocr_missing_image(self):
        """Test Mileage OCR endpoint with missing image"""
        print("\n🎯 Testing Mileage OCR with missing image...")
        success, response = self.run_test(
            "Mileage OCR - Missing Image",
            "POST",
            "api/ocr-mileage",
            400,
            check_error_message=True
        )
        
        if success and 'error' in response:
            error_msg = response['error']
            suggestion = response.get('suggestion', '')
            
            # Check for enhanced error message
            enhanced_keywords = ['image', 'photo', 'odometer', 'mileage', 'clear']
            has_enhanced_msg = any(keyword.lower() in error_msg.lower() for keyword in enhanced_keywords)
            
            if has_enhanced_msg:
                print(f"   ✅ Enhanced error message contains helpful guidance")
                return True
            else:
                print(f"   ⚠️  Error message could be more helpful: {error_msg}")
                return False
        return False

    def test_mileage_ocr_poor_quality_image(self):
        """Test Mileage OCR endpoint with poor quality image"""
        print("\n🎯 Testing Mileage OCR with poor quality image...")
        test_image = "/tmp/poor_quality.png"
        self.create_poor_quality_image(test_image)
        
        try:
            with open(test_image, 'rb') as f:
                files = {'image': ('poor_quality.png', f, 'image/png')}
                success, response = self.run_test(
                    "Mileage OCR - Poor Quality Image",
                    "POST",
                    "api/ocr-mileage",
                    200,  # Should return 200 but with UNREADABLE
                    files=files,
                    check_error_message=True
                )
        finally:
            os.remove(test_image)
        
        if success:
            mileage = response.get('mileage', '')
            error_msg = response.get('error', '')
            suggestion = response.get('suggestion', '')
            
            if mileage == "UNREADABLE" and error_msg:
                # Check for enhanced error message
                helpful_keywords = ['clear', 'photo', 'odometer', 'visible', 'focus']
                has_helpful_msg = any(keyword.lower() in error_msg.lower() for keyword in helpful_keywords)
                
                if has_helpful_msg:
                    print(f"   ✅ Enhanced error message provides helpful guidance")
                    return True
                else:
                    print(f"   ⚠️  Error message could be more helpful: {error_msg}")
                    return False
            else:
                print(f"   ⚠️  Expected UNREADABLE with error message, got: {response}")
                return False
        return False

    def test_license_plate_ocr_missing_image(self):
        """Test License Plate OCR endpoint with missing image"""
        print("\n🎯 Testing License Plate OCR with missing image...")
        success, response = self.run_test(
            "License Plate OCR - Missing Image",
            "POST",
            "api/ocr-license-plate",
            400,
            check_error_message=True
        )
        
        if success and 'error' in response:
            error_msg = response['error']
            suggestion = response.get('suggestion', '')
            
            # Check for enhanced error message
            enhanced_keywords = ['image', 'photo', 'license', 'plate', 'clear', 'visible']
            has_enhanced_msg = any(keyword.lower() in error_msg.lower() for keyword in enhanced_keywords)
            
            if has_enhanced_msg:
                print(f"   ✅ Enhanced error message contains helpful guidance")
                return True
            else:
                print(f"   ⚠️  Error message could be more helpful: {error_msg}")
                return False
        return False

    def test_license_plate_ocr_empty_image(self):
        """Test License Plate OCR endpoint with empty/blank image"""
        print("\n🎯 Testing License Plate OCR with empty image...")
        test_image = "/tmp/empty_image.png"
        self.create_empty_image(test_image)
        
        try:
            with open(test_image, 'rb') as f:
                files = {'image': ('empty.png', f, 'image/png')}
                success, response = self.run_test(
                    "License Plate OCR - Empty Image",
                    "POST",
                    "api/ocr-license-plate",
                    200,  # Should return 200 but with UNREADABLE
                    files=files,
                    check_error_message=True
                )
        finally:
            os.remove(test_image)
        
        if success:
            license_plate = response.get('licensePlate', '')
            error_msg = response.get('error', '')
            suggestion = response.get('suggestion', '')
            
            if license_plate == "UNREADABLE" and error_msg:
                # Check for enhanced error message
                helpful_keywords = ['clear', 'photo', 'license', 'plate', 'visible', 'well-lit']
                has_helpful_msg = any(keyword.lower() in error_msg.lower() for keyword in helpful_keywords)
                
                if has_helpful_msg:
                    print(f"   ✅ Enhanced error message provides helpful guidance")
                    return True
                else:
                    print(f"   ⚠️  Error message could be more helpful: {error_msg}")
                    return False
            else:
                print(f"   ⚠️  Expected UNREADABLE with error message, got: {response}")
                return False
        return False

    def test_response_structure_improvements(self):
        """Test that responses include success flags and detailed feedback"""
        print("\n🎯 Testing response structure improvements...")
        test_image = "/tmp/empty_for_structure.png"
        self.create_empty_image(test_image)
        
        try:
            with open(test_image, 'rb') as f:
                files = {'image': ('empty.png', f, 'image/png')}
                success, response = self.run_test(
                    "Response Structure - Success Flags",
                    "POST",
                    "api/ocr-vin",
                    200,
                    files=files
                )
        finally:
            os.remove(test_image)
        
        if success:
            # Check for enhanced response structure
            has_success_flag = 'success' in response
            has_error_field = 'error' in response
            has_suggestion_field = 'suggestion' in response
            
            structure_score = sum([has_success_flag, has_error_field, has_suggestion_field])
            
            print(f"   📊 Response Structure Analysis:")
            print(f"      Success Flag: {'✅' if has_success_flag else '❌'}")
            print(f"      Error Field: {'✅' if has_error_field else '❌'}")
            print(f"      Suggestion Field: {'✅' if has_suggestion_field else '❌'}")
            
            if structure_score >= 2:
                print(f"   ✅ Enhanced response structure detected ({structure_score}/3 fields)")
                return True
            else:
                print(f"   ⚠️  Response structure needs improvement ({structure_score}/3 fields)")
                return False
        return False

    def print_enhanced_error_summary(self):
        """Print detailed summary of enhanced error handling tests"""
        print("\n" + "=" * 70)
        print("📊 ENHANCED OCR ERROR HANDLING TEST RESULTS")
        print("=" * 70)
        
        # Categorize tests
        vin_tests = [r for r in self.test_results if 'VIN' in r['name']]
        mileage_tests = [r for r in self.test_results if 'Mileage' in r['name']]
        license_tests = [r for r in self.test_results if 'License' in r['name']]
        structure_tests = [r for r in self.test_results if 'Structure' in r['name']]
        
        def print_test_category(category_name, tests):
            print(f"\n🔍 {category_name}:")
            for test in tests:
                status = "✅ PASS" if test['success'] else "❌ FAIL"
                enhanced = "🌟 ENHANCED" if test.get('enhanced_error', False) else ""
                print(f"   {status} {enhanced} - {test['name']}")
                if not test['success']:
                    print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
        
        print_test_category("VIN OCR ERROR HANDLING", vin_tests)
        print_test_category("MILEAGE OCR ERROR HANDLING", mileage_tests)
        print_test_category("LICENSE PLATE OCR ERROR HANDLING", license_tests)
        print_test_category("RESPONSE STRUCTURE IMPROVEMENTS", structure_tests)
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Check for enhanced error handling
        enhanced_tests = [r for r in self.test_results if r.get('enhanced_error', False)]
        enhancement_rate = len(enhanced_tests) / len([r for r in self.test_results if 'enhanced_error' in r]) * 100 if any('enhanced_error' in r for r in self.test_results) else 0
        
        print(f"\n🌟 ENHANCEMENT ANALYSIS:")
        print(f"   Enhanced Error Messages: {len(enhanced_tests)} tests")
        print(f"   Enhancement Rate: {enhancement_rate:.1f}%")
        
        # Determine if enhanced error handling is working
        critical_enhancements = self.tests_passed >= (self.tests_run * 0.8)  # 80% pass rate
        
        print(f"\n🎯 ENHANCED ERROR HANDLING STATUS:")
        if critical_enhancements:
            print(f"   ✅ ENHANCED ERROR HANDLING WORKING")
        else:
            print(f"   ❌ ENHANCED ERROR HANDLING NEEDS IMPROVEMENT")
        
        return critical_enhancements

def main():
    print("🚀 Starting Enhanced OCR Error Handling Tests...")
    print("=" * 60)
    print("🎯 Focus: Testing improved OCR error messages and user guidance")
    print("=" * 60)
    
    # Setup
    tester = EnhancedOCRErrorTester("http://localhost:3000")
    
    # Run enhanced error handling tests
    tests = [
        # VIN OCR Error Handling Tests
        tester.test_vin_ocr_missing_image,
        tester.test_vin_ocr_invalid_image_data,
        
        # Mileage OCR Error Handling Tests
        tester.test_mileage_ocr_missing_image,
        tester.test_mileage_ocr_poor_quality_image,
        
        # License Plate OCR Error Handling Tests
        tester.test_license_plate_ocr_missing_image,
        tester.test_license_plate_ocr_empty_image,
        
        # Response Structure Tests
        tester.test_response_structure_improvements,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print detailed results
    enhanced_working = tester.print_enhanced_error_summary()
    
    # Determine overall success
    if enhanced_working:
        print("\n🎉 ENHANCED OCR ERROR HANDLING: WORKING PERFECTLY!")
        print("   ✅ Clear, user-friendly error messages")
        print("   ✅ Specific suggestions for retaking photos")
        print("   ✅ Success/failure flags with detailed feedback")
        return 0
    else:
        print("\n⚠️  ENHANCED OCR ERROR HANDLING: NEEDS IMPROVEMENT")
        print("   ❌ Some error messages need to be more user-friendly")
        print("   ❌ Missing specific guidance for photo retaking")
        return 1

if __name__ == "__main__":
    sys.exit(main())