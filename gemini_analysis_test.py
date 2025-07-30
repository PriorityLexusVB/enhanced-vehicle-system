#!/usr/bin/env python3
"""
Comprehensive Test for Gemini AI Photo Analysis Endpoint
Tests REAL image processing vs mock analysis
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

class GeminiAnalysisAPITester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            start_time = time.time()
            
            if method == 'POST':
                response = requests.post(url, json=data, timeout=60)
            elif method == 'GET':
                response = requests.get(url, timeout=60)
            
            end_time = time.time()
            response_time = end_time - start_time

            success = response.status_code == expected_status
            result = {
                'name': name,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'response_time': response_time,
                'success': success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} (Response time: {response_time:.2f}s)")
                try:
                    response_data = response.json()
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

    def test_gemini_analysis_with_real_images(self):
        """Test Gemini AI analysis with real vehicle images from Unsplash"""
        print("\n🚗 Testing Gemini AI Analysis with REAL vehicle images...")
        
        test_data = {
            "submissionId": "test_real_analysis_001",
            "photoUrls": [
                "https://images.unsplash.com/photo-1494905998402-395d579af36f",  # Car exterior
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d"   # Car interior
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "year": "2020",
                "make": "Honda",
                "model": "Civic", 
                "mileage": 45000,
                "notes": "Minor parking lot dings, well maintained"
            }
        }
        
        success, response = self.run_test(
            "Gemini AI Analysis - Real Images",
            "POST",
            "api/analyze-vehicle-photos",
            200,
            data=test_data
        )
        
        if success and response.get('success'):
            analysis = response.get('data', {}).get('analysis', {})
            
            # Check for comprehensive analysis components
            required_fields = [
                'overall_condition',
                'exterior_condition', 
                'interior_condition',
                'mechanical_observations',
                'severity_assessment',
                'trade_in_factors',
                'confidence_score',
                'vehicle_grade'
            ]
            
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if not missing_fields:
                print(f"   ✅ All required analysis fields present")
                print(f"   📊 Confidence Score: {analysis.get('confidence_score', 'N/A')}%")
                print(f"   🏆 Vehicle Grade: {analysis.get('vehicle_grade', 'N/A')}")
                print(f"   📸 Photos Analyzed: {response.get('data', {}).get('photosAnalyzed', 0)}")
                
                # Check if this looks like real analysis vs mock
                detailed_findings = analysis.get('detailed_findings', '')
                if len(detailed_findings) > 500:
                    print(f"   🎯 DETAILED ANALYSIS: {len(detailed_findings)} characters of analysis")
                    return True, "COMPREHENSIVE_ANALYSIS"
                else:
                    print(f"   ⚠️  Analysis seems brief ({len(detailed_findings)} characters)")
                    return True, "BASIC_ANALYSIS"
            else:
                print(f"   ❌ Missing analysis fields: {missing_fields}")
                return False, "INCOMPLETE_ANALYSIS"
        
        return False, "FAILED"

    def test_gemini_analysis_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🚫 Testing Gemini AI Analysis error handling...")
        
        # Test missing required fields
        test_data = {
            "submissionId": "test_error_001"
            # Missing photoUrls
        }
        
        success, response = self.run_test(
            "Gemini AI Analysis - Missing Photos",
            "POST",
            "api/analyze-vehicle-photos",
            400,
            data=test_data
        )
        
        if success and not response.get('success'):
            print(f"   ✅ Correctly returned error: {response.get('error', 'Unknown error')}")
            return True
        
        return False

    def test_gemini_analysis_empty_photos(self):
        """Test with empty photo array"""
        print("\n📷 Testing Gemini AI Analysis with empty photos...")
        
        test_data = {
            "submissionId": "test_empty_photos_001",
            "photoUrls": [],  # Empty array
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "year": "2020",
                "make": "Honda",
                "model": "Civic"
            }
        }
        
        success, response = self.run_test(
            "Gemini AI Analysis - Empty Photos",
            "POST",
            "api/analyze-vehicle-photos",
            400,
            data=test_data
        )
        
        if success and not response.get('success'):
            print(f"   ✅ Correctly rejected empty photos: {response.get('error', 'Unknown error')}")
            return True
        
        return False

    def test_gemini_analysis_invalid_urls(self):
        """Test with invalid photo URLs to check fallback behavior"""
        print("\n🔗 Testing Gemini AI Analysis with invalid URLs...")
        
        test_data = {
            "submissionId": "test_invalid_urls_001",
            "photoUrls": [
                "https://invalid-url-that-does-not-exist.com/photo1.jpg",
                "https://another-invalid-url.com/photo2.jpg"
            ],
            "submissionData": {
                "vin": "1HGBH41JXMN109186",
                "year": "2020",
                "make": "Honda",
                "model": "Civic"
            }
        }
        
        success, response = self.run_test(
            "Gemini AI Analysis - Invalid URLs",
            "POST",
            "api/analyze-vehicle-photos",
            200,  # Should still return 200 with fallback analysis
            data=test_data
        )
        
        if success and response.get('success'):
            analysis = response.get('data', {}).get('analysis', {})
            print(f"   ✅ Fallback analysis provided")
            print(f"   📊 Analysis Type: {response.get('data', {}).get('analysisType', 'Unknown')}")
            return True, "FALLBACK_WORKING"
        
        return False, "FALLBACK_FAILED"

    def test_python_service_availability(self):
        """Test if Python Gemini service is available"""
        print("\n🐍 Testing Python Gemini Service availability...")
        
        # Check if Python service files exist
        service_files = [
            "/app/lib/gemini_analysis_service.py",
            "/app/lib/gemini_vehicle_analysis.py"
        ]
        
        files_exist = []
        for file_path in service_files:
            if os.path.exists(file_path):
                files_exist.append(file_path)
                print(f"   ✅ Found: {file_path}")
            else:
                print(f"   ❌ Missing: {file_path}")
        
        # Check if required Python packages are available
        try:
            import subprocess
            result = subprocess.run(['python3', '-c', 'import emergentintegrations'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ emergentintegrations package available")
                return True, len(files_exist)
            else:
                print(f"   ❌ emergentintegrations package not available: {result.stderr}")
                return False, len(files_exist)
        except Exception as e:
            print(f"   ❌ Error checking Python packages: {str(e)}")
            return False, len(files_exist)

    def analyze_response_for_real_processing(self, response_data):
        """Analyze response to determine if real image processing occurred"""
        if not response_data.get('success'):
            return "ERROR", "Request failed"
        
        analysis = response_data.get('data', {}).get('analysis', {})
        analysis_type = response_data.get('data', {}).get('analysisType', '')
        
        # Check for indicators of real processing
        real_processing_indicators = [
            len(analysis.get('detailed_findings', '')) > 1000,  # Comprehensive analysis
            analysis.get('confidence_score', 0) != 87,  # Not the mock confidence score
            'gemini_vision' in analysis_type.lower(),
            analysis.get('vehicle_grade') not in ['B+'],  # Not the mock grade
        ]
        
        mock_indicators = [
            'Multiple door dings' in analysis.get('detailed_findings', ''),  # Mock text
            analysis.get('confidence_score') == 87,  # Mock confidence
            analysis.get('vehicle_grade') == 'B+',  # Mock grade
        ]
        
        real_score = sum(real_processing_indicators)
        mock_score = sum(mock_indicators)
        
        if real_score > mock_score:
            return "REAL_PROCESSING", f"Real processing indicators: {real_score}, Mock indicators: {mock_score}"
        elif mock_score > real_score:
            return "MOCK_PROCESSING", f"Mock processing indicators: {mock_score}, Real indicators: {real_score}"
        else:
            return "UNCERTAIN", f"Mixed indicators - Real: {real_score}, Mock: {mock_score}"

    def print_comprehensive_summary(self):
        """Print detailed test summary with analysis"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE GEMINI AI ANALYSIS TEST RESULTS")
        print("=" * 80)
        
        # Overall test results
        print(f"\n📈 OVERALL TEST RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Detailed analysis of each test
        print(f"\n🔍 DETAILED TEST ANALYSIS:")
        for test in self.test_results:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {status} - {test['name']}")
            if 'response_time' in test:
                print(f"      Response Time: {test['response_time']:.2f}s")
            
            if test['success'] and 'response' in test:
                response = test['response']
                if 'Gemini AI Analysis' in test['name'] and response.get('success'):
                    # Analyze if this was real or mock processing
                    processing_type, details = self.analyze_response_for_real_processing(response)
                    print(f"      Processing Type: {processing_type}")
                    print(f"      Details: {details}")
        
        # Critical functionality assessment
        gemini_tests = [r for r in self.test_results if 'Gemini AI Analysis' in r['name']]
        gemini_working = any(test['success'] for test in gemini_tests)
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        print(f"   Gemini AI Analysis: {'✅ WORKING' if gemini_working else '❌ FAILING'}")
        
        # Real vs Mock Analysis Assessment
        real_processing_detected = False
        for test in self.test_results:
            if test['success'] and 'response' in test and 'Gemini AI Analysis' in test['name']:
                processing_type, _ = self.analyze_response_for_real_processing(test['response'])
                if processing_type == "REAL_PROCESSING":
                    real_processing_detected = True
                    break
        
        print(f"\n🧠 REAL AI PROCESSING ASSESSMENT:")
        if real_processing_detected:
            print(f"   ✅ REAL IMAGE PROCESSING DETECTED")
            print(f"   🎉 Gemini AI is processing actual images, not just returning mock data")
        else:
            print(f"   ⚠️  MOCK PROCESSING DETECTED")
            print(f"   🔄 System is falling back to mock analysis (Python service may be unavailable)")
        
        return gemini_working, real_processing_detected

def main():
    print("🚀 Starting Comprehensive Gemini AI Photo Analysis Tests...")
    print("=" * 60)
    
    # Setup
    tester = GeminiAnalysisAPITester("http://localhost:3000")
    
    # Test Python service availability first
    print("\n🔧 PRELIMINARY CHECKS:")
    python_available, files_found = tester.test_python_service_availability()
    print(f"   Python Service Files: {files_found}/2 found")
    print(f"   Python Dependencies: {'✅ Available' if python_available else '❌ Missing'}")
    
    # Run all tests
    tests = [
        tester.test_gemini_analysis_with_real_images,
        tester.test_gemini_analysis_error_handling,
        tester.test_gemini_analysis_empty_photos,
        tester.test_gemini_analysis_invalid_urls,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print comprehensive results
    gemini_working, real_processing = tester.print_comprehensive_summary()
    
    # Final assessment
    print(f"\n🏁 FINAL ASSESSMENT:")
    if gemini_working and real_processing:
        print("🎉 SUCCESS: Gemini AI Photo Analysis is working with REAL image processing!")
        return 0
    elif gemini_working:
        print("⚠️  PARTIAL: Gemini AI endpoint works but using mock analysis (Python service issue)")
        return 1
    else:
        print("❌ FAILURE: Gemini AI Photo Analysis endpoint not working")
        return 2

if __name__ == "__main__":
    sys.exit(main())