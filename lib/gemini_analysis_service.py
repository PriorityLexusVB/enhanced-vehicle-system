#!/usr/bin/env python3
"""
Gemini Vehicle Analysis Service - HTTP Wrapper
Provides HTTP interface for the Gemini vehicle analysis Python module
"""

import asyncio
import json
import sys
import os
from typing import List, Dict, Any

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from gemini_vehicle_analysis import GeminiVehicleAnalysis

async def analyze_photos(photo_urls: List[str], submission_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze vehicle photos using Gemini Vision API
    
    Args:
        photo_urls: List of photo URLs to analyze
        submission_data: Optional submission data for context
    
    Returns:
        Analysis results dictionary
    """
    try:
        # Get Gemini API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY environment variable not set"
            }
        
        # Initialize analyzer
        analyzer = GeminiVehicleAnalysis(api_key)
        
        # Perform analysis
        result = await analyzer.analyze_vehicle_photos(photo_urls, submission_data)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python gemini_analysis_service.py '<json_input>'")
        print("JSON input should contain 'photoUrls' and optional 'submissionData'")
        sys.exit(1)
    
    try:
        # Parse input JSON
        input_data = json.loads(sys.argv[1])
        photo_urls = input_data.get('photoUrls', [])
        submission_data = input_data.get('submissionData', {})
        
        if not photo_urls:
            print(json.dumps({
                "success": False,
                "error": "No photo URLs provided"
            }))
            sys.exit(1)
        
        # Run analysis
        result = asyncio.run(analyze_photos(photo_urls, submission_data))
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Service error: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()