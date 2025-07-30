#!/usr/bin/env python3

import requests
import sys
import os
import json
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont

class EnhancedVehicleAppraisalTester:
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

    # ========== NEW GEMINI AI PHOTO ANALYSIS TESTS ==========
    
    def test_gemini_analyze_vehicle_photos_valid_request(self):
        """Test NEW Gemini AI photo analysis with valid request"""
        test_data = {
            "submissionId": "test_submission_001",
            "photoUrls": [
                "https://example.com/exterior1.jpg",
                "https://example.com/interior1.jpg",
                "https://example.com/damage1.jpg"
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "year": "2018",
                "make": "Honda",
                "model": "Civic",
                "mileage": 45000,
                "notes": "Minor parking dings, regular maintenance"
            }
        }
        
        success, response = self.run_test(
            "NEW Gemini AI Photo Analysis - Valid Request",
            "POST",
            "api/analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and response.get('success'):
            analysis_data = response.get('data', {})
            analysis = analysis_data.get('analysis', {})
            
            # Verify comprehensive analysis structure
            required_fields = [
                'overall_condition', 'exterior_condition', 'interior_condition',
                'mechanical_observations', 'severity_assessment', 'trade_in_factors',
                'recommended_disclosures', 'detailed_findings', 'confidence_score',
                'vehicle_grade'
            ]
            
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if not missing_fields:
                print(f"   ✅ Complete analysis structure with {len(required_fields)} components")
                print(f"   📊 Vehicle Grade: {analysis.get('vehicle_grade')}")
                print(f"   🎯 Confidence Score: {analysis.get('confidence_score')}%")
                print(f"   📸 Photos Analyzed: {analysis_data.get('photosAnalyzed', 0)}")
                return True
            else:
                print(f"   ⚠️  Missing analysis fields: {missing_fields}")
                return False
        return False

    def test_gemini_analyze_vehicle_photos_missing_fields(self):
        """Test Gemini AI photo analysis with missing required fields"""
        test_data = {
            "submissionId": "test_submission_002"
            # Missing photoUrls
        }
        
        success, response = self.run_test(
            "NEW Gemini AI Photo Analysis - Missing Fields",
            "POST",
            "api/analyze-vehicle-photos",
            400,
            data=test_data
        )
        
        if success and not response.get('success') and 'error' in response:
            print(f"   ✅ Correctly returned error: {response['error']}")
            return True
        return False

    def test_gemini_analyze_vehicle_photos_empty_photos(self):
        """Test Gemini AI photo analysis with empty photo array"""
        test_data = {
            "submissionId": "test_submission_003",
            "photoUrls": [],  # Empty array
            "submissionData": {"vin": "1HGBH41JXMN109186"}
        }
        
        success, response = self.run_test(
            "NEW Gemini AI Photo Analysis - Empty Photos",
            "POST",
            "api/analyze-vehicle-photos",
            400,
            data=test_data
        )
        
        if success and not response.get('success') and 'error' in response:
            print(f"   ✅ Correctly returned error: {response['error']}")
            return True
        return False

    def test_gemini_analyze_vehicle_photos_comprehensive_data(self):
        """Test Gemini AI photo analysis with comprehensive vehicle data"""
        test_data = {
            "submissionId": "test_submission_comprehensive",
            "photoUrls": [
                "https://example.com/front_exterior.jpg",
                "https://example.com/rear_exterior.jpg", 
                "https://example.com/driver_side.jpg",
                "https://example.com/passenger_side.jpg",
                "https://example.com/interior_front.jpg",
                "https://example.com/interior_rear.jpg",
                "https://example.com/engine_bay.jpg",
                "https://example.com/trunk.jpg",
                "https://example.com/damage_detail.jpg"
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "year": "2020",
                "make": "Toyota",
                "model": "Camry",
                "mileage": 32500,
                "notes": "Vehicle has minor door dings from parking lot incidents. Regular oil changes performed. Small scratch on rear bumper from backing incident. Interior shows normal wear for mileage.",
                "ownerType": "individual",
                "maintenanceRecords": "available"
            }
        }
        
        success, response = self.run_test(
            "NEW Gemini AI Photo Analysis - Comprehensive Data",
            "POST",
            "api/analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and response.get('success'):
            analysis_data = response.get('data', {})
            analysis = analysis_data.get('analysis', {})
            
            # Verify detailed analysis components
            severity_assessment = analysis.get('severity_assessment', {})
            trade_in_factors = analysis.get('trade_in_factors', [])
            
            print(f"   ✅ Comprehensive analysis completed")
            print(f"   📊 Severity Distribution: {severity_assessment.get('severity_distribution', {})}")
            print(f"   💰 Trade-in Factors: {len(trade_in_factors)} identified")
            print(f"   📝 Analysis Type: {analysis_data.get('analysisType')}")
            
            # Check if analysis includes context from submission data
            detailed_findings = analysis.get('detailed_findings', '')
            context_found = any(term in detailed_findings.upper() for term in ['TOYOTA', 'CAMRY', '2020', 'PARKING'])
            
            if context_found:
                print(f"   ✅ Analysis incorporates vehicle context data")
                return True
            else:
                print(f"   ⚠️  Analysis may not be incorporating context data")
                return False
        return False

    # ========== EXISTING OCR ENDPOINTS VERIFICATION ==========
    
    def test_ocr_vin_with_clear_image(self):
        """Test VIN OCR with clear image - EXISTING FUNCTIONALITY"""
        print("\n📸 Creating test image with clear VIN...")
        test_image = self.create_test_image_with_text("1HGBH41JXMN109186", "/tmp/clear_vin.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_vin.png', f, 'image/png')}
            success, response = self.run_test(
                "EXISTING OCR VIN - Clear Image",
                "POST",
                "api/ocr-vin",
                200,
                files=files
            )
        
        # Clean up
        os.remove(test_image)
        
        if success and 'vin' in response:
            vin = response['vin']
            confidence = response.get('confidence', 0)
            if vin != "UNREADABLE" and len(vin) == 17:
                print(f"   ✅ Successfully extracted VIN: {vin} (Confidence: {confidence}%)")
                return True
            else:
                print(f"   ⚠️  Unexpected VIN result: {vin}")
                return False
        return False

    def test_ocr_license_plate_with_clear_image(self):
        """Test License Plate OCR with clear image - EXISTING FUNCTIONALITY"""
        print("\n📸 Creating test image with clear license plate...")
        test_image = self.create_test_image_with_text("ABC1234", "/tmp/clear_plate.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_plate.png', f, 'image/png')}
            success, response = self.run_test(
                "EXISTING OCR License Plate - Clear Image",
                "POST",
                "api/ocr-license-plate",
                200,
                files=files
            )
        
        # Clean up
        os.remove(test_image)
        
        if success and 'licensePlate' in response:
            plate = response['licensePlate']
            confidence = response.get('confidence', 0)
            if plate != "UNREADABLE" and len(plate) >= 4:
                print(f"   ✅ Successfully extracted license plate: {plate} (Confidence: {confidence}%)")
                return True
            else:
                print(f"   ⚠️  Unexpected license plate result: {plate}")
                return False
        return False

    def test_ocr_mileage_with_clear_image(self):
        """Test Mileage OCR with clear image - EXISTING FUNCTIONALITY"""
        print("\n📸 Creating test image with clear mileage...")
        test_image = self.create_test_image_with_text("87325", "/tmp/clear_mileage.png")
        
        with open(test_image, 'rb') as f:
            files = {'image': ('clear_mileage.png', f, 'image/png')}
            success, response = self.run_test(
                "EXISTING OCR Mileage - Clear Image",
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

    # ========== CORE VIN DECODE VERIFICATION ==========
    
    def test_vin_decode_api_working_perfectly(self):
        """Test VIN decode API - CORE FUNCTIONALITY"""
        success, response = self.run_test(
            "CORE VIN Decode API - Working Perfectly",
            "POST",
            "api/vin-decode",
            200,
            data={"vin": "1HGBH41JXMN109186"}
        )
        
        if success and response.get('success'):
            vehicle = response.get('vehicle', {})
            if vehicle.get('make') and vehicle.get('year'):
                print(f"   ✅ Successfully decoded VIN: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
                print(f"   💰 Trade-in Value: {vehicle.get('tradeInValue', 'N/A')}")
                return True
            else:
                print(f"   ⚠️  VIN decoded but missing vehicle info")
                return False
        return False

    def test_vin_decode_invalid_format(self):
        """Test VIN decode with invalid format"""
        success, response = self.run_test(
            "CORE VIN Decode - Invalid Format",
            "POST",
            "api/vin-decode",
            400,
            data={"vin": "INVALID"}
        )
        
        if success and 'error' in response:
            print(f"   ✅ Correctly returned error for invalid VIN: {response['error']}")
            return True
        return False

    # ========== ERROR HANDLING TESTS ==========
    
    def test_ocr_endpoints_no_image(self):
        """Test all OCR endpoints without providing images"""
        endpoints = [
            ("api/ocr-vin", "VIN OCR"),
            ("api/ocr-license-plate", "License Plate OCR"),
            ("api/ocr-mileage", "Mileage OCR")
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            success, response = self.run_test(
                f"{name} - No Image Error Handling",
                "POST",
                endpoint,
                400
            )
            
            if success and 'error' in response:
                print(f"   ✅ {name} correctly handles missing image")
            else:
                print(f"   ❌ {name} error handling failed")
                all_passed = False
        
        return all_passed

    def print_comprehensive_summary(self):
        """Print comprehensive test summary focusing on NEW Gemini AI functionality"""
        print("\n" + "=" * 80)
        print("📊 ENHANCED VEHICLE APPRAISAL SYSTEM - COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        # Categorize tests
        gemini_tests = [r for r in self.test_results if 'Gemini AI' in r['name']]
        ocr_tests = [r for r in self.test_results if 'OCR' in r['name'] and 'Gemini' not in r['name']]
        vin_tests = [r for r in self.test_results if 'VIN Decode' in r['name']]
        
        print(f"\n🤖 NEW GEMINI AI PHOTO ANALYSIS TESTING:")
        print(f"   Priority Focus: Testing NEW AI-powered vehicle damage assessment")
        for test in gemini_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
                if 'error' in test:
                    error_msg = test['error'] if isinstance(test['error'], str) else str(test['error'])
                    print(f"      Error: {error_msg[:100]}...")
        
        print(f"\n🔍 EXISTING OCR ENDPOINTS STATUS CHECK:")
        print(f"   Verification: Ensuring existing OCR functionality still works")
        for test in ocr_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if not test['success']:
                print(f"      Expected: {test['expected_status']}, Got: {test['actual_status']}")
        
        print(f"\n🚗 CORE VIN DECODE VERIFICATION:")
        print(f"   Status: Previously working perfectly - quick verification")
        for test in vin_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
        
        # Overall statistics
        print(f"\n📈 OVERALL TEST RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Critical functionality assessment
        gemini_working = any(test['success'] and 'Valid Request' in test['name'] for test in gemini_tests)
        ocr_working = any(test['success'] and 'Clear Image' in test['name'] for test in ocr_tests)
        vin_working = any(test['success'] and 'Working Perfectly' in test['name'] for test in vin_tests)
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        print(f"   🤖 NEW Gemini AI Analysis: {'✅ WORKING' if gemini_working else '❌ FAILING'}")
        print(f"   🔍 Existing OCR Processing: {'✅ WORKING' if ocr_working else '❌ FAILING'}")
        print(f"   🚗 Core VIN Decode: {'✅ WORKING' if vin_working else '❌ FAILING'}")
        
        # Environment check
        print(f"\n🔧 ENVIRONMENT VARIABLES STATUS:")
        gemini_key = os.getenv('GEMINI_API_KEY', 'Not found')
        firebase_email = os.getenv('FIREBASE_CLIENT_EMAIL', 'Not found')
        firebase_key = os.getenv('FIREBASE_PRIVATE_KEY', 'Not found')
        
        print(f"   GEMINI_API_KEY: {'✅ Present' if gemini_key != 'Not found' else '❌ Missing'}")
        print(f"   FIREBASE_CLIENT_EMAIL: {'✅ Present' if firebase_email != 'Not found' else '❌ Missing'}")
        print(f"   FIREBASE_PRIVATE_KEY: {'✅ Present' if firebase_key != 'Not found' else '❌ Missing'}")
        
        return gemini_working, ocr_working, vin_working

def main():
    print("🚀 Starting Enhanced Vehicle Appraisal System Backend Testing...")
    print("🎯 PRIORITY: Testing NEW Gemini AI Photo Analysis Functionality")
    print("=" * 80)
    
    # Setup
    tester = EnhancedVehicleAppraisalTester("http://localhost:3000")
    
    # Run tests in priority order
    tests = [
        # 1. NEW GEMINI AI PHOTO ANALYSIS (PRIORITY)
        tester.test_gemini_analyze_vehicle_photos_valid_request,
        tester.test_gemini_analyze_vehicle_photos_comprehensive_data,
        tester.test_gemini_analyze_vehicle_photos_missing_fields,
        tester.test_gemini_analyze_vehicle_photos_empty_photos,
        
        # 2. EXISTING OCR ENDPOINTS STATUS CHECK
        tester.test_ocr_vin_with_clear_image,
        tester.test_ocr_license_plate_with_clear_image,
        tester.test_ocr_mileage_with_clear_image,
        tester.test_ocr_endpoints_no_image,
        
        # 3. CORE VIN DECODE QUICK VERIFICATION
        tester.test_vin_decode_api_working_perfectly,
        tester.test_vin_decode_invalid_format,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print comprehensive results
    gemini_working, ocr_working, vin_working = tester.print_comprehensive_summary()
    
    # Determine overall success based on priorities
    if gemini_working and vin_working:
        if ocr_working:
            print("\n🎉 COMPLETE SUCCESS: All functionality working perfectly!")
            return 0
        else:
            print("\n✅ PRIMARY SUCCESS: NEW Gemini AI and Core VIN Decode working!")
            print("⚠️  OCR endpoints need attention but core functionality intact")
            return 0
    elif gemini_working:
        print("\n🎯 PARTIAL SUCCESS: NEW Gemini AI working, other issues detected")
        return 1
    else:
        print("\n❌ CRITICAL: NEW Gemini AI functionality not working")
        return 2

if __name__ == "__main__":
    sys.exit(main())