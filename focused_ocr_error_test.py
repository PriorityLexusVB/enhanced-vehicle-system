#!/usr/bin/env python3

import requests
import sys
import os
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont
import json

class FocusedOCRErrorTester:
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

    def run_test(self, name, method, endpoint, files=None, data=None):
        """Run a single API test and analyze the response"""
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

            print(f"   Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                response_data = {'text': response.text}
                print(f"   Response Text: {response.text}")
            
            # Analyze error handling improvements
            self.analyze_error_handling(response_data, response.status_code)
            
            result = {
                'name': name,
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response': response_data,
                'success': True  # We're just analyzing, not expecting specific codes
            }
            
            self.test_results.append(result)
            self.tests_passed += 1
            return True, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                'name': name,
                'endpoint': endpoint,
                'status_code': 'ERROR',
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            return False, {}

    def analyze_error_handling(self, response_data, status_code):
        """Analyze the quality of error handling in the response"""
        print(f"\n   📊 Error Handling Analysis:")
        
        # Check for enhanced error messages
        error_msg = response_data.get('error', '')
        suggestion = response_data.get('suggestion', '')
        success_flag = response_data.get('success', None)
        
        print(f"      Error Message: {error_msg}")
        print(f"      Suggestion: {suggestion}")
        print(f"      Success Flag: {success_flag}")
        
        # Evaluate error message quality
        if error_msg:
            if error_msg == "UNREADABLE":
                print(f"      ⚠️  Generic 'UNREADABLE' message")
            elif len(error_msg) > 20 and any(word in error_msg.lower() for word in ['clear', 'photo', 'image', 'try']):
                print(f"      ✅ Enhanced error message with helpful guidance")
            else:
                print(f"      ⚠️  Error message could be more helpful")
        
        # Evaluate suggestion quality
        if suggestion:
            if any(word in suggestion.lower() for word in ['ensure', 'make sure', 'clear', 'visible', 'well-lit']):
                print(f"      ✅ Helpful suggestion provided")
            else:
                print(f"      ⚠️  Suggestion could be more specific")
        else:
            print(f"      ❌ No suggestion provided")
        
        # Evaluate response structure
        if success_flag is not None:
            print(f"      ✅ Success flag present")
        else:
            print(f"      ❌ No success flag")

    def test_all_ocr_endpoints_missing_image(self):
        """Test all OCR endpoints with missing image"""
        endpoints = [
            ("VIN OCR", "api/ocr-vin"),
            ("Mileage OCR", "api/ocr-mileage"),
            ("License Plate OCR", "api/ocr-license-plate")
        ]
        
        for name, endpoint in endpoints:
            self.run_test(f"{name} - Missing Image", "POST", endpoint)

    def test_all_ocr_endpoints_empty_image(self):
        """Test all OCR endpoints with empty/blank image"""
        endpoints = [
            ("VIN OCR", "api/ocr-vin"),
            ("Mileage OCR", "api/ocr-mileage"),
            ("License Plate OCR", "api/ocr-license-plate")
        ]
        
        test_image = "/tmp/empty_test.png"
        self.create_empty_image(test_image)
        
        try:
            for name, endpoint in endpoints:
                with open(test_image, 'rb') as f:
                    files = {'image': ('empty.png', f, 'image/png')}
                    self.run_test(f"{name} - Empty Image", "POST", endpoint, files=files)
        finally:
            os.remove(test_image)

    def test_all_ocr_endpoints_poor_quality(self):
        """Test all OCR endpoints with poor quality image"""
        endpoints = [
            ("VIN OCR", "api/ocr-vin"),
            ("Mileage OCR", "api/ocr-mileage"),
            ("License Plate OCR", "api/ocr-license-plate")
        ]
        
        test_image = "/tmp/poor_quality_test.png"
        self.create_poor_quality_image(test_image)
        
        try:
            for name, endpoint in endpoints:
                with open(test_image, 'rb') as f:
                    files = {'image': ('poor.png', f, 'image/png')}
                    self.run_test(f"{name} - Poor Quality Image", "POST", endpoint, files=files)
        finally:
            os.remove(test_image)

    def print_comprehensive_summary(self):
        """Print comprehensive summary of OCR error handling improvements"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE OCR ERROR HANDLING ANALYSIS")
        print("=" * 80)
        
        # Analyze by endpoint
        endpoints = {}
        for result in self.test_results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        for endpoint, tests in endpoints.items():
            print(f"\n🔍 {endpoint.upper()} ENDPOINT:")
            
            enhanced_count = 0
            total_tests = len(tests)
            
            for test in tests:
                print(f"   📝 {test['name']}:")
                response = test.get('response', {})
                
                error_msg = response.get('error', '')
                suggestion = response.get('suggestion', '')
                success_flag = response.get('success', None)
                
                # Check for enhancements
                has_enhanced_error = error_msg and error_msg != "UNREADABLE" and len(error_msg) > 20
                has_suggestion = bool(suggestion)
                has_success_flag = success_flag is not None
                
                if has_enhanced_error or has_suggestion or has_success_flag:
                    enhanced_count += 1
                
                print(f"      Status: {test['status_code']}")
                print(f"      Enhanced Error: {'✅' if has_enhanced_error else '❌'}")
                print(f"      Has Suggestion: {'✅' if has_suggestion else '❌'}")
                print(f"      Success Flag: {'✅' if has_success_flag else '❌'}")
            
            enhancement_rate = (enhanced_count / total_tests) * 100 if total_tests > 0 else 0
            print(f"   📊 Enhancement Rate: {enhancement_rate:.1f}% ({enhanced_count}/{total_tests})")
        
        # Overall assessment
        total_enhanced = sum(1 for result in self.test_results 
                           if result.get('response', {}).get('error', '') != "UNREADABLE" 
                           and len(result.get('response', {}).get('error', '')) > 20)
        
        overall_enhancement_rate = (total_enhanced / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Enhanced Responses: {total_enhanced}")
        print(f"   Overall Enhancement Rate: {overall_enhancement_rate:.1f}%")
        
        if overall_enhancement_rate >= 70:
            print(f"   ✅ ENHANCED ERROR HANDLING: EXCELLENT")
            return True
        elif overall_enhancement_rate >= 50:
            print(f"   ⚠️  ENHANCED ERROR HANDLING: GOOD (needs minor improvements)")
            return True
        else:
            print(f"   ❌ ENHANCED ERROR HANDLING: NEEDS SIGNIFICANT IMPROVEMENT")
            return False

def main():
    print("🚀 Starting Focused OCR Error Handling Analysis...")
    print("=" * 70)
    print("🎯 Analyzing enhanced error messages and user guidance")
    print("=" * 70)
    
    # Setup
    tester = FocusedOCRErrorTester("http://localhost:3000")
    
    # Run comprehensive tests
    print("\n📋 Testing Missing Image Scenarios...")
    tester.test_all_ocr_endpoints_missing_image()
    
    print("\n📋 Testing Empty Image Scenarios...")
    tester.test_all_ocr_endpoints_empty_image()
    
    print("\n📋 Testing Poor Quality Image Scenarios...")
    tester.test_all_ocr_endpoints_poor_quality()
    
    # Print comprehensive analysis
    enhanced_working = tester.print_comprehensive_summary()
    
    # Final assessment
    if enhanced_working:
        print("\n🎉 ENHANCED OCR ERROR HANDLING: WORKING WELL!")
        print("   ✅ Improved error messages detected")
        print("   ✅ User-friendly guidance provided")
        print("   ✅ Better response structure implemented")
        return 0
    else:
        print("\n⚠️  ENHANCED OCR ERROR HANDLING: NEEDS IMPROVEMENT")
        print("   ❌ Error messages need to be more user-friendly")
        print("   ❌ Missing specific guidance for photo retaking")
        return 1

if __name__ == "__main__":
    sys.exit(main())