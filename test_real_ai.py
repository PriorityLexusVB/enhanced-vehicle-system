#!/usr/bin/env python3
"""
Test with Matching Vehicle Data to Verify Real AI Processing
"""

import requests
import json

def test_with_matching_data():
    """Test with matching vehicle data"""
    
    url = "http://localhost:3000/api/analyze-vehicle-photos"
    
    # Use generic vehicle data that won't conflict with images
    test_data = {
        "submissionId": "test_matching_data_001",
        "photoUrls": [
            "https://images.unsplash.com/photo-1494905998402-395d579af36f",  # Car exterior
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d"   # Car interior
        ],
        "submissionData": {
            "vin": "UNKNOWN",  # Don't specify conflicting VIN
            "year": "Unknown",
            "make": "Unknown",
            "model": "Unknown", 
            "mileage": 0,
            "notes": "Please analyze the vehicle in the photos"
        }
    }
    
    print("🔍 Testing Gemini AI Analysis with Non-Conflicting Data...")
    
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
                print(f"   Overall Condition: {analysis.get('overall_condition', 'N/A')[:150]}...")
                print(f"   Confidence Score: {analysis.get('confidence_score', 'N/A')}%")
                print(f"   Vehicle Grade: {analysis.get('vehicle_grade', 'N/A')}")
                print(f"   Photos Analyzed: {data.get('data', {}).get('photosAnalyzed', 0)}")
                
                # Check for real AI indicators
                detailed_findings = analysis.get('detailed_findings', '')
                
                print(f"\n🔍 REAL AI PROCESSING INDICATORS:")
                
                # Real AI indicators (specific to actual image content)
                real_indicators = [
                    'mustang' in detailed_findings.lower(),
                    'ford' in detailed_findings.lower(),
                    'aftermarket' in detailed_findings.lower(),
                    'hood scoop' in detailed_findings.lower(),
                    'splitter' in detailed_findings.lower(),
                    'modified' in detailed_findings.lower(),
                    len(detailed_findings) > 1000,
                    analysis.get('confidence_score') != 87,
                    'responsible AI' in detailed_findings or 'cannot fulfill' in detailed_findings
                ]
                
                # Mock indicators
                mock_indicators = [
                    'Multiple door dings' in detailed_findings,
                    'parking lot damage' in detailed_findings,
                    analysis.get('confidence_score') == 87,
                    analysis.get('vehicle_grade') == 'B+',
                    'COMPREHENSIVE VEHICLE INSPECTION REPORT' in detailed_findings and len(detailed_findings) < 2000
                ]
                
                real_score = sum(real_indicators)
                mock_score = sum(mock_indicators)
                
                print(f"   Real AI Indicators: {real_score}/9")
                print(f"   Mock Indicators: {mock_score}/5")
                
                if real_score > mock_score:
                    print(f"   🎉 REAL AI PROCESSING CONFIRMED!")
                    print(f"   ✅ Gemini AI is analyzing actual images")
                elif mock_score > real_score:
                    print(f"   ⚠️  MOCK PROCESSING DETECTED")
                    print(f"   🔄 System is using fallback mock analysis")
                else:
                    print(f"   ❓ UNCERTAIN - Mixed indicators")
                
                # Print detailed findings
                print(f"\n📝 DETAILED FINDINGS:")
                print(f"   {detailed_findings}")
                
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
    print("🚀 Testing Real Gemini AI Processing with Matching Data...")
    print("=" * 60)
    
    is_real = test_with_matching_data()
    
    print(f"\n🏁 FINAL RESULT:")
    if is_real:
        print("🎉 SUCCESS: Real Gemini AI processing is working!")
        print("✅ The system is using actual image analysis, not mock data")
    else:
        print("⚠️  FALLBACK: System is using mock analysis")