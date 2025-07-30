#!/usr/bin/env python3
"""
Detailed Test to Verify Real vs Mock Gemini AI Processing
"""

import requests
import json

def test_real_vs_mock_processing():
    """Test to determine if real AI processing is happening"""
    
    url = "http://localhost:3000/api/analyze-vehicle-photos"
    
    test_data = {
        "submissionId": "test_real_vs_mock_001",
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
    
    print("🔍 Testing Gemini AI Analysis for Real vs Mock Processing...")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                analysis = data.get('data', {}).get('analysis', {})
                
                print(f"✅ Request successful")
                print(f"📊 Response time: {response.elapsed.total_seconds():.2f}s")
                print(f"🎯 Analysis type: {data.get('data', {}).get('analysisType', 'Unknown')}")
                
                # Print key analysis components
                print(f"\n📋 ANALYSIS DETAILS:")
                print(f"   Overall Condition: {analysis.get('overall_condition', 'N/A')[:100]}...")
                print(f"   Confidence Score: {analysis.get('confidence_score', 'N/A')}%")
                print(f"   Vehicle Grade: {analysis.get('vehicle_grade', 'N/A')}")
                print(f"   Photos Analyzed: {data.get('data', {}).get('photosAnalyzed', 0)}")
                
                # Check for mock indicators
                detailed_findings = analysis.get('detailed_findings', '')
                
                print(f"\n🔍 MOCK VS REAL ANALYSIS:")
                
                # Mock indicators
                mock_indicators = [
                    'Multiple door dings' in detailed_findings,
                    'parking lot damage' in detailed_findings,
                    analysis.get('confidence_score') == 87,
                    analysis.get('vehicle_grade') == 'B+',
                    'COMPREHENSIVE VEHICLE INSPECTION REPORT' in detailed_findings
                ]
                
                # Real processing indicators
                real_indicators = [
                    len(detailed_findings) > 2000,  # Real AI tends to be more verbose
                    'Ford Mustang' in detailed_findings or 'modified' in detailed_findings.lower(),
                    'aftermarket' in detailed_findings.lower(),
                    'hood scoop' in detailed_findings.lower(),
                    analysis.get('confidence_score') != 87
                ]
                
                mock_score = sum(mock_indicators)
                real_score = sum(real_indicators)
                
                print(f"   Mock Indicators: {mock_score}/5")
                print(f"   Real Processing Indicators: {real_score}/5")
                
                if real_score > mock_score:
                    print(f"   🎉 REAL AI PROCESSING DETECTED!")
                    print(f"   ✅ The system is using actual Gemini AI to analyze images")
                elif mock_score > real_score:
                    print(f"   ⚠️  MOCK PROCESSING DETECTED")
                    print(f"   🔄 The system is falling back to mock analysis")
                else:
                    print(f"   ❓ UNCERTAIN - Mixed indicators")
                
                # Print a sample of the detailed findings
                print(f"\n📝 DETAILED FINDINGS SAMPLE (first 500 chars):")
                print(f"   {detailed_findings[:500]}...")
                
                return real_score > mock_score
                
            else:
                print(f"❌ Request failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Real vs Mock Gemini AI Processing...")
    print("=" * 60)
    
    is_real = test_real_vs_mock_processing()
    
    print(f"\n🏁 FINAL RESULT:")
    if is_real:
        print("🎉 SUCCESS: Real Gemini AI processing is working!")
    else:
        print("⚠️  FALLBACK: System is using mock analysis")