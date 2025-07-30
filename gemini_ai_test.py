#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class GeminiAITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def test_gemini_ai_photo_analysis(self):
        """Test Gemini AI photo analysis endpoint"""
        print("\n🔍 Testing Gemini AI Photo Analysis...")
        
        url = f"{self.base_url}/api/analyze-vehicle-photos"
        
        # Test data with correct format based on API structure
        test_data = {
            "submissionId": "test_submission_123",
            "photoUrls": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
                "https://example.com/photo3.jpg"
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "make": "Honda",
                "model": "Civic",
                "year": "1991",
                "mileage": "87325",
                "ownerNotes": "Minor scratches on front bumper, interior in good condition"
            }
        }
        
        try:
            response = requests.post(url, json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected fields in response
                if data.get('success') and 'data' in data:
                    analysis_data = data['data']
                    analysis = analysis_data.get('analysis', {})
                    
                    # Check for key analysis fields
                    expected_fields = ['overall_condition', 'exterior_condition', 'interior_condition', 
                                     'mechanical_observations', 'severity_assessment', 'trade_in_factors',
                                     'confidence_score', 'vehicle_grade', 'detailed_findings']
                    
                    missing_fields = [field for field in expected_fields if field not in analysis]
                    
                    if not missing_fields:
                        self.log_test(
                            "Gemini AI Photo Analysis - Complete Response",
                            True,
                            f"All expected fields present. Grade: {analysis.get('vehicle_grade', 'N/A')}, Confidence: {analysis.get('confidence_score', 'N/A')}%"
                        )
                        
                        # Print detailed analysis
                        print(f"   📊 Overall Condition: {analysis.get('overall_condition', 'N/A')[:100]}...")
                        print(f"   🎯 Vehicle Grade: {analysis.get('vehicle_grade', 'N/A')}")
                        print(f"   📈 Confidence Score: {analysis.get('confidence_score', 'N/A')}%")
                        print(f"   🔍 Severity Assessment: {analysis.get('severity_assessment', {}).get('primary_severity', 'N/A')}")
                        print(f"   💰 Trade-in Factors: {len(analysis.get('trade_in_factors', []))} factors identified")
                        print(f"   📝 Photos Analyzed: {analysis_data.get('photosAnalyzed', 'N/A')}")
                        
                        return True, data
                    else:
                        self.log_test(
                            "Gemini AI Photo Analysis - Incomplete Response",
                            False,
                            f"Missing fields: {', '.join(missing_fields)}"
                        )
                        return False, data
                else:
                    self.log_test(
                        "Gemini AI Photo Analysis - Invalid Response Structure",
                        False,
                        f"Response missing success/data fields: {data}"
                    )
                    return False, data
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Gemini AI Photo Analysis - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
                )
                return False, error_data
                
        except Exception as e:
            self.log_test(
                "Gemini AI Photo Analysis - Exception",
                False,
                f"Exception: {str(e)}"
            )
            return False, {}

    def test_gemini_ai_missing_photos(self):
        """Test Gemini AI with missing photos"""
        print("\n🔍 Testing Gemini AI with Missing Photos...")
        
        url = f"{self.base_url}/api/analyze-vehicle-photos"
        
        test_data = {
            "submissionId": "test_submission_456",
            "photoUrls": [],  # Empty photos array
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "make": "Honda",
                "model": "Civic",
                "year": "1991",
                "mileage": "87325"
            }
        }
        
        try:
            response = requests.post(url, json=test_data)
            
            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Gemini AI Missing Photos Validation",
                    True,
                    f"Correctly returned 400 error: {error_data.get('error', 'Unknown error')}"
                )
                return True, error_data
            else:
                self.log_test(
                    "Gemini AI Missing Photos Validation",
                    False,
                    f"Expected 400 error, got {response.status_code}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "Gemini AI Missing Photos Validation",
                False,
                f"Exception: {str(e)}"
            )
            return False, {}

    def test_gemini_ai_invalid_data(self):
        """Test Gemini AI with invalid data"""
        print("\n🔍 Testing Gemini AI with Invalid Data...")
        
        url = f"{self.base_url}/api/analyze-vehicle-photos"
        
        test_data = {
            "submissionId": "test_submission_789",
            "photoUrls": ["https://example.com/invalid-photo.jpg"],
            "submissionData": {
                "vin": "INVALID",
                "make": "",
                "model": "",
                "year": "invalid",
                "mileage": "invalid"
            }
        }
        
        try:
            response = requests.post(url, json=test_data)
            
            # Should either return 400 for validation error or 200 with error handling
            if response.status_code in [200, 400]:
                data = response.json() if response.content else {}
                self.log_test(
                    "Gemini AI Invalid Data Handling",
                    True,
                    f"Handled invalid data appropriately (HTTP {response.status_code})"
                )
                return True, data
            else:
                self.log_test(
                    "Gemini AI Invalid Data Handling",
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "Gemini AI Invalid Data Handling",
                False,
                f"Exception: {str(e)}"
            )
            return False, {}

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🧠 GEMINI AI PHOTO ANALYSIS TEST REPORT")
        print("=" * 80)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
            if result['details']:
                print(f"      {result['details']}")
        
        # Determine critical functionality status
        ai_analysis_working = any(
            result['success'] and 'Complete Response' in result['name'] 
            for result in self.test_results
        )
        error_handling_working = any(
            result['success'] and ('Validation' in result['name'] or 'Handling' in result['name'])
            for result in self.test_results
        )
        
        print(f"\n🎯 CRITICAL STATUS:")
        print(f"   AI Photo Analysis: {'✅ WORKING' if ai_analysis_working else '❌ FAILING'}")
        print(f"   Error Handling: {'✅ WORKING' if error_handling_working else '❌ FAILING'}")
        
        return ai_analysis_working, error_handling_working

def main():
    print("🚀 Starting Gemini AI Photo Analysis Tests...")
    print("=" * 60)
    
    tester = GeminiAITester()
    
    # Run comprehensive tests
    tests = [
        tester.test_gemini_ai_photo_analysis,
        tester.test_gemini_ai_missing_photos,
        tester.test_gemini_ai_invalid_data,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print detailed results
    ai_working, error_handling = tester.print_summary()
    
    # Determine overall success
    if ai_working and error_handling:
        print("\n🎉 GEMINI AI SYSTEM: FULLY OPERATIONAL!")
        return 0
    elif ai_working:
        print("\n⚠️  GEMINI AI SYSTEM: CORE FUNCTIONALITY WORKING")
        return 1
    else:
        print("\n❌ GEMINI AI SYSTEM: NOT WORKING")
        return 2

if __name__ == "__main__":
    sys.exit(main())