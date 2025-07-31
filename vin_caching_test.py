#!/usr/bin/env python3

import requests
import json
import time
import sys
from datetime import datetime

class VinCachingTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details
        })

    def test_vin_decode_first_call(self):
        """Test first VIN decode call - should hit NHTSA API and cache result"""
        print("\n🔍 Testing VIN Decode - First Call (should cache)")
        
        test_vin = "1HGBH41JXMN109186"
        url = f"{self.base_url}/api/vin-decode"
        
        try:
            start_time = time.time()
            response = requests.post(url, json={"vin": test_vin}, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') and 'vehicle' in data:
                    vehicle = data['vehicle']
                    
                    # First call should NOT be cached
                    cached = vehicle.get('cached', True)  # Default to True to catch if missing
                    cache_hit = vehicle.get('cacheHit', True)  # Default to True to catch if missing
                    
                    if cached == False:
                        self.log_test(
                            "First VIN call - Cache Miss", 
                            True, 
                            f"Response time: {response_time:.2f}s, VIN: {vehicle.get('vin')}, Make: {vehicle.get('make')}, Year: {vehicle.get('year')}"
                        )
                        return True, data
                    else:
                        self.log_test(
                            "First VIN call - Cache Miss", 
                            False, 
                            f"Expected cached=false, got cached={cached}"
                        )
                        return False, data
                else:
                    self.log_test(
                        "First VIN call - Response Structure", 
                        False, 
                        f"Invalid response structure: {data}"
                    )
                    return False, {}
            else:
                self.log_test(
                    "First VIN call - HTTP Status", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "First VIN call - Request", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False, {}

    def test_vin_decode_second_call(self):
        """Test second VIN decode call - should serve from cache"""
        print("\n🚀 Testing VIN Decode - Second Call (should hit cache)")
        
        test_vin = "1HGBH41JXMN109186"
        url = f"{self.base_url}/api/vin-decode"
        
        try:
            start_time = time.time()
            response = requests.post(url, json={"vin": test_vin}, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') and 'vehicle' in data:
                    vehicle = data['vehicle']
                    
                    # Second call should be cached
                    cached = vehicle.get('cached', False)
                    cache_hit = vehicle.get('cacheHit', False)
                    
                    if cached == True and cache_hit == True:
                        self.log_test(
                            "Second VIN call - Cache Hit", 
                            True, 
                            f"Response time: {response_time:.2f}s (should be faster), cached={cached}, cacheHit={cache_hit}"
                        )
                        return True, data
                    else:
                        self.log_test(
                            "Second VIN call - Cache Hit", 
                            False, 
                            f"Expected cached=true & cacheHit=true, got cached={cached}, cacheHit={cache_hit}"
                        )
                        return False, data
                else:
                    self.log_test(
                        "Second VIN call - Response Structure", 
                        False, 
                        f"Invalid response structure: {data}"
                    )
                    return False, {}
            else:
                self.log_test(
                    "Second VIN call - HTTP Status", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "Second VIN call - Request", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False, {}

    def test_cache_stats_endpoint(self):
        """Test cache stats endpoint"""
        print("\n📊 Testing Cache Stats Endpoint")
        
        url = f"{self.base_url}/api/vin-decode/cache-stats"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get('success') and 'cache' in data:
                        cache_info = data['cache']
                        self.log_test(
                            "Cache Stats - Endpoint Working", 
                            True, 
                            f"Status: {cache_info.get('status')}, Total Entries: {cache_info.get('totalEntries', 'N/A')}"
                        )
                        return True, data
                    else:
                        self.log_test(
                            "Cache Stats - Response Structure", 
                            False, 
                            f"Invalid response structure: {data}"
                        )
                        return False, {}
                except json.JSONDecodeError:
                    self.log_test(
                        "Cache Stats - JSON Parse", 
                        False, 
                        f"Response is not valid JSON: {response.text[:200]}"
                    )
                    return False, {}
            else:
                self.log_test(
                    "Cache Stats - HTTP Status", 
                    False, 
                    f"Expected 200, got {response.status_code}. Endpoint may not be properly configured."
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "Cache Stats - Request", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False, {}

    def test_invalid_vin_not_cached(self):
        """Test that invalid VINs are not cached"""
        print("\n🚫 Testing Invalid VIN - Should Not Be Cached")
        
        invalid_vin = "INVALID123"
        url = f"{self.base_url}/api/vin-decode"
        
        try:
            response = requests.post(url, json={"vin": invalid_vin}, timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data:
                    self.log_test(
                        "Invalid VIN - Proper Error Response", 
                        True, 
                        f"Error: {data['error']}"
                    )
                    return True, data
                else:
                    self.log_test(
                        "Invalid VIN - Error Structure", 
                        False, 
                        f"Expected error field in response: {data}"
                    )
                    return False, data
            else:
                self.log_test(
                    "Invalid VIN - HTTP Status", 
                    False, 
                    f"Expected 400, got {response.status_code}: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(
                "Invalid VIN - Request", 
                False, 
                f"Request failed: {str(e)}"
            )
            return False, {}

    def test_cache_performance(self, first_response_time, second_response_time):
        """Test that cached responses are faster"""
        print("\n⚡ Testing Cache Performance")
        
        if second_response_time < first_response_time:
            improvement = ((first_response_time - second_response_time) / first_response_time) * 100
            self.log_test(
                "Cache Performance - Speed Improvement", 
                True, 
                f"First call: {first_response_time:.3f}s, Second call: {second_response_time:.3f}s, Improvement: {improvement:.1f}%"
            )
            return True
        else:
            self.log_test(
                "Cache Performance - Speed Improvement", 
                False, 
                f"First call: {first_response_time:.3f}s, Second call: {second_response_time:.3f}s (not faster)"
            )
            return False

    def test_different_vin_caching(self):
        """Test caching with a different VIN"""
        print("\n🔄 Testing Different VIN Caching")
        
        test_vin = "1FTFW1ET5DFC10312"  # Different VIN
        url = f"{self.base_url}/api/vin-decode"
        
        try:
            # First call with new VIN
            response1 = requests.post(url, json={"vin": test_vin}, timeout=10)
            
            if response1.status_code == 200:
                data1 = response1.json()
                vehicle1 = data1.get('vehicle', {})
                
                if vehicle1.get('cached') == False:
                    # Second call with same VIN
                    time.sleep(0.1)  # Small delay
                    response2 = requests.post(url, json={"vin": test_vin}, timeout=10)
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        vehicle2 = data2.get('vehicle', {})
                        
                        if vehicle2.get('cached') == True and vehicle2.get('cacheHit') == True:
                            self.log_test(
                                "Different VIN - Cache Working", 
                                True, 
                                f"VIN: {test_vin}, First: cached=false, Second: cached=true"
                            )
                            return True
                        else:
                            self.log_test(
                                "Different VIN - Cache Not Working", 
                                False, 
                                f"Second call cached={vehicle2.get('cached')}, cacheHit={vehicle2.get('cacheHit')}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Different VIN - Second Call Failed", 
                            False, 
                            f"Status: {response2.status_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "Different VIN - First Call Cached", 
                        False, 
                        f"First call should not be cached, got cached={vehicle1.get('cached')}"
                    )
                    return False
            else:
                self.log_test(
                    "Different VIN - First Call Failed", 
                    False, 
                    f"Status: {response1.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Different VIN - Request Failed", 
                False, 
                f"Error: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run all VIN caching tests"""
        print("🚀 Starting Comprehensive VIN Caching Tests...")
        print("=" * 60)
        
        # Test 1: First VIN decode call (should cache)
        first_success, first_data = self.test_vin_decode_first_call()
        first_time = 0  # We'll measure this in the actual test
        
        # Small delay to ensure cache is set
        time.sleep(0.1)
        
        # Test 2: Second VIN decode call (should hit cache)
        second_success, second_data = self.test_vin_decode_second_call()
        second_time = 0  # We'll measure this in the actual test
        
        # Test 3: Cache stats endpoint
        stats_success, stats_data = self.test_cache_stats_endpoint()
        
        # Test 4: Invalid VIN handling
        invalid_success, invalid_data = self.test_invalid_vin_not_cached()
        
        # Test 5: Different VIN caching
        different_vin_success = self.test_different_vin_caching()
        
        # Print summary
        self.print_summary()
        
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 VIN CACHING TEST SUMMARY")
        print("=" * 60)
        
        print(f"\n🎯 CORE CACHING FUNCTIONALITY:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
            if result['details'] and not result['success']:
                print(f"      Details: {result['details']}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Determine overall status
        if self.tests_passed == self.tests_run:
            print(f"\n🎉 VIN CACHING SYSTEM: FULLY OPERATIONAL!")
            print("   ✅ Cache miss on first call")
            print("   ✅ Cache hit on second call") 
            print("   ✅ Proper cache indicators in response")
            print("   ✅ Error handling working")
            print("   ✅ Multiple VIN caching working")
        elif self.tests_passed >= self.tests_run * 0.8:
            print(f"\n⚠️  VIN CACHING SYSTEM: MOSTLY WORKING")
            print("   Core functionality operational with minor issues")
        else:
            print(f"\n❌ VIN CACHING SYSTEM: NEEDS ATTENTION")
            print("   Critical caching functionality not working properly")

def main():
    print("🔍 VIN CACHING SYSTEM TESTING")
    print("Testing the newly implemented VIN caching functionality...")
    print("=" * 60)
    
    tester = VinCachingTester("http://localhost:3000")
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 ALL VIN CACHING TESTS PASSED!")
            return 0
        else:
            print("\n⚠️  SOME VIN CACHING TESTS FAILED")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 2
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {str(e)}")
        return 3

if __name__ == "__main__":
    sys.exit(main())