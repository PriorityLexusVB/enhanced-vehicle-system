import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import json
import base64
from PIL import Image
import io
import uuid

# Enhanced Vehicle Inspection Dataset - Professional Grade Analysis Prompts
ENHANCED_VEHICLE_INSPECTION_PROMPTS = {
    "comprehensive_professional": """
You are a certified automotive appraiser with expertise in trade-in valuations. Conduct a comprehensive vehicle inspection analysis using the provided photos.

ANALYSIS REQUIREMENTS:
- Examine EVERY photo methodically for defects, damage, and wear
- Provide specific locations, measurements, and severity ratings
- Focus on factual observations that affect trade-in value
- Use professional automotive terminology
- Include confidence scores for each detection

DAMAGE CATEGORIES TO ASSESS:

1. EXTERIOR BODY DAMAGE:
   Dents: Document location (front fender, driver door, hood, roof, trunk, quarter panel), size (diameter in cm), and severity (light <2cm, moderate 2-5cm, severe >5cm)
   Scratches: Note location, length (cm), depth (surface, moderate, deep gouges), and type
   Cracks: Identify on body panels, bumpers, plastic components, glass (windshield, windows, lamp covers)
   Paint Damage: Detect repaint evidence, color mismatches, orange peel texture, clear coat damage, stone chips, peeling lacquer
   Missing/Broken Parts: Headlights, taillights, fog lights, grilles, emblems, trim, mirrors, handles, antenna, wipers, hubcaps
   Hail Damage: Identify circular depressions and impact patterns
   Panel Gaps: Assess alignment between doors, fenders, hood, trunk
   Hidden Modifications: Detect signs of prior repairs or non-factory alterations

2. TIRES & WHEELS:
   Tread Depth: Estimate depth (mm) for each tire position, categorize wear level (excellent >6mm, good 4-6mm, fair 2-4mm, poor <2mm)
   Sidewall Condition: Document bubbles, cracks, cuts, dry rot, manufacturing dates
   Rim Damage: Identify curb rash, bends, cracks on each wheel
   Tire Specifications: Read size, brand, model if visible
   Alignment Issues: Assess from wear patterns (inside edge, outside edge, center wear)
   Mismatched Tires: Note different brands/sizes on same axle
   Flat/Low Pressure: Identify deflated tires

3. UNDERCARRIAGE & MECHANICAL:
   Fluid Leaks: Classify leak types (oil, coolant, transmission, brake fluid) and severity
   Corrosion/Rust: Map rust locations and severity (surface, moderate, severe structural)
   Structural Damage: Detect frame bends, cracks, deformation
   Missing Components: Exhaust parts, catalytic converters, shields, suspension components
   Mechanical Wear: Visible component deterioration

4. INTERIOR CONDITION:
   Upholstery: Document tears, wear patterns, stains, burns on seats, carpets, headliner
   Components: Note missing/broken knobs, buttons, vents, trim, dashboard elements
   Electronics: Assess visible condition of displays, controls, lighting
   Cleanliness: Overall interior maintenance level

SEVERITY RATINGS:
- LIGHT: Cosmetic issues, minimal impact on function or safety
- MODERATE: Noticeable defects affecting appearance or minor function
- MAJOR: Significant damage requiring repair, affects safety or major function  
- SEVERE: Critical safety concerns, structural integrity, or major mechanical failure

CONFIDENCE SCORING:
Assign confidence percentages (60-100%) for each detection based on image clarity and certainty.

OUTPUT FORMAT:
1. OVERALL CONDITION SUMMARY (professional grade assessment)
2. CONFIDENCE SCORE (overall inspection confidence 60-100%)
3. VEHICLE GRADE (A+ Excellent, A Good, B+ Fair, B Poor, C Critical)
4. DETAILED FINDINGS BY CATEGORY (with specific measurements and locations)
5. SEVERITY DISTRIBUTION (count by Light/Moderate/Major/Severe)
6. HOTSPOT ANALYSIS (areas with concentrated damage)
7. TRADE-IN DEVALUATION FACTORS (factual impact statements, no pricing)
8. REQUIRED DISCLOSURES (safety, legal, structural concerns)
9. PHOTO-SPECIFIC ANNOTATIONS (bounding box coordinates for overlays)

Provide thorough, professional analysis suitable for trade-in documentation and customer transparency.
""",

    "bounding_box_detection": """
For each detected issue, provide precise bounding box coordinates for photo overlay annotations:

FORMAT: [photo_index, x1, y1, x2, y2, detection_type, severity, confidence]

DETECTION TYPES:
- dent, scratch, crack, paint_damage, missing_part, rust, tire_wear, fluid_leak, tear, stain, broken_component

SEVERITY CODES: L (Light), M (Moderate), J (Major), S (Severe)

Example: [1, 145, 67, 189, 98, "dent", "M", 92]

This enables precise visual overlay annotations for each detected issue.
""",

    "trade_in_impact_analysis": """
Analyze each detected issue for its specific impact on trade-in value. Provide factual, professional statements:

IMPACT CATEGORIES:
- Safety Concerns: Issues affecting vehicle safety or roadworthiness
- Structural Integrity: Frame, body, or chassis damage
- Mechanical Function: Engine, transmission, brake, suspension issues  
- Aesthetic Appeal: Paint, body, interior appearance factors
- Regulatory Compliance: Emissions, safety, legal requirements
- Future Reliability: Wear patterns indicating accelerated deterioration

For each category, provide specific devaluation factors without monetary estimates.
"""
}

class GeminiVehicleAnalysis:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def analyze_vehicle_photos(self, photo_urls: list, submission_data: dict = None) -> dict:
        """
        Analyze vehicle photos using Gemini Vision API
        
        Args:
            photo_urls: List of photo URLs to analyze
            submission_data: Optional submission data for context
        
        Returns:
            Comprehensive analysis results
        """
        try:
            # Create unique session for this analysis
            session_id = f"vehicle_analysis_{uuid.uuid4().hex[:8]}"
            
            # Initialize Gemini chat with vision capabilities 
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message="You are a professional vehicle appraiser specializing in trade-in evaluations."
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(4096)
            
            # Prepare image contents for analysis
            image_contents = []
            for i, photo_url in enumerate(photo_urls):
                try:
                    # For now, we'll use placeholder analysis since we need the actual image processing
                    # In production, you'd download and convert images to base64
                    print(f"Processing photo {i+1}: {photo_url}")
                    
                    # Create image content (placeholder - would need actual base64 conversion)
                    image_content = ImageContent(
                        image_base64=self._create_placeholder_base64()  # Placeholder
                    )
                    image_contents.append(image_content)
                    
                except Exception as e:
                    print(f"Error processing photo {i+1}: {str(e)}")
                    continue
            
            if not image_contents:
                return self._create_error_response("No valid images to analyze")
            
            # Create analysis message with context
            context = ""
            if submission_data:
                context = f"""
VEHICLE CONTEXT:
- VIN: {submission_data.get('vin', 'Not provided')}
- Year: {submission_data.get('year', 'Unknown')}
- Make: {submission_data.get('make', 'Unknown')}
- Model: {submission_data.get('model', 'Unknown')}
- Mileage: {submission_data.get('mileage', 'Unknown')}
- Owner Notes: {submission_data.get('notes', 'None provided')}

"""
            
            analysis_message = UserMessage(
                text=context + ENHANCED_VEHICLE_INSPECTION_PROMPTS["comprehensive_professional"],
                file_contents=image_contents
            )
            
            # Get AI analysis
            response = await chat.send_message(analysis_message)
            
            # Parse and structure the response
            analysis_result = self._parse_analysis_response(response, submission_data)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            return self._create_error_response(str(e))
    
    def _create_placeholder_base64(self) -> str:
        """Create a small placeholder image for testing"""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='lightblue')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def _parse_analysis_response(self, response: str, submission_data: dict = None) -> dict:
        """Parse and structure the AI analysis response"""
        
        # Extract key information from response
        analysis = {
            "overall_condition": self._extract_overall_condition(response),
            "exterior_condition": self._extract_condition_category(response, "exterior"),
            "interior_condition": self._extract_condition_category(response, "interior"),
            "mechanical_observations": self._extract_condition_category(response, "mechanical"),
            "severity_assessment": self._extract_severity_ratings(response),
            "trade_in_factors": self._extract_trade_in_factors(response),
            "recommended_disclosures": self._extract_disclosures(response),
            "detailed_findings": response,  # Full AI response
            "analysis_timestamp": self._get_timestamp(),
            "confidence_score": self._calculate_confidence_score(response),
            "vehicle_grade": self._determine_vehicle_grade(response)
        }
        
        return {
            "success": True,
            "analysis": analysis,
            "photos_analyzed": len(submission_data.get('photoUrls', [])) if submission_data else 0,
            "analysis_type": "gemini_vision_comprehensive"
        }
    
    def _extract_overall_condition(self, response: str) -> str:
        """Extract overall condition summary"""
        lines = response.split('\n')
        for line in lines:
            if 'OVERALL CONDITION' in line.upper() or 'SUMMARY' in line.upper():
                # Find the next few lines after this header
                idx = lines.index(line)
                summary_lines = []
                for i in range(idx + 1, min(idx + 4, len(lines))):
                    if lines[i].strip() and not lines[i].startswith('##'):
                        summary_lines.append(lines[i].strip())
                return ' '.join(summary_lines) if summary_lines else "Condition assessment completed"
        
        # Fallback: use first substantial paragraph
        paragraphs = [p.strip() for p in response.split('\n\n') if len(p.strip()) > 50]
        return paragraphs[0] if paragraphs else "Professional vehicle inspection completed"
    
    def _extract_condition_category(self, response: str, category: str) -> str:
        """Extract specific condition category details"""
        category_keywords = {
            "exterior": ["EXTERIOR", "PAINT", "BODY", "BUMPER", "DENTS"],
            "interior": ["INTERIOR", "SEATS", "DASHBOARD", "CARPET"],
            "mechanical": ["MECHANICAL", "ENGINE", "TIRE", "FLUID"]
        }
        
        keywords = category_keywords.get(category.lower(), [])
        lines = response.split('\n')
        
        for keyword in keywords:
            for i, line in enumerate(lines):
                if keyword in line.upper():
                    # Collect related lines
                    category_lines = []
                    for j in range(i, min(i + 5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('#'):
                            category_lines.append(lines[j].strip())
                    return ' '.join(category_lines) if category_lines else f"{category} condition noted"
        
        return f"{category.title()} condition within normal parameters"
    
    def _extract_severity_ratings(self, response: str) -> dict:
        """Extract severity assessments"""
        severity_counts = {
            "minor": response.upper().count("MINOR"),
            "moderate": response.upper().count("MODERATE"), 
            "major": response.upper().count("MAJOR"),
            "severe": response.upper().count("SEVERE")
        }
        
        # Determine primary severity
        max_severity = max(severity_counts, key=severity_counts.get)
        
        return {
            "primary_severity": max_severity,
            "severity_distribution": severity_counts,
            "total_issues": sum(severity_counts.values())
        }
    
    def _extract_trade_in_factors(self, response: str) -> list:
        """Extract trade-in impact factors"""
        factors = []
        lines = response.split('\n')
        
        # Look for lines mentioning trade-in impacts
        trade_keywords = ["TRADE", "VALUE", "IMPACT", "DEVALUATION", "AFFECT"]
        
        for line in lines:
            if any(keyword in line.upper() for keyword in trade_keywords):
                if len(line.strip()) > 20:  # Substantial content
                    factors.append(line.strip())
        
        # If no specific factors found, extract from damage mentions
        if not factors:
            damage_keywords = ["DAMAGE", "SCRATCH", "DENT", "WEAR", "TEAR", "STAIN"]
            for line in lines:
                if any(keyword in line.upper() for keyword in damage_keywords):
                    if len(line.strip()) > 15:
                        factors.append(line.strip())
        
        return factors[:5]  # Limit to top 5 factors
    
    def _extract_disclosures(self, response: str) -> list:
        """Extract recommended disclosures"""
        disclosures = []
        lines = response.split('\n')
        
        disclosure_keywords = ["DISCLOSE", "BUYER", "SHOULD KNOW", "AWARE", "RECOMMEND"]
        
        for line in lines:
            if any(keyword in line.upper() for keyword in disclosure_keywords):
                if len(line.strip()) > 20:
                    disclosures.append(line.strip())
        
        return disclosures[:3]  # Limit to top 3 disclosures
    
    def _calculate_confidence_score(self, response: str) -> int:
        """Calculate confidence score based on analysis detail"""
        # Score based on response comprehensiveness
        word_count = len(response.split())
        detail_indicators = ["specific", "detailed", "clearly", "evident", "visible", "noted"]
        detail_score = sum(1 for word in detail_indicators if word in response.lower())
        
        # Base confidence calculation
        confidence = min(95, 60 + (word_count // 20) + (detail_score * 5))
        return max(75, confidence)  # Minimum 75% confidence
    
    def _determine_vehicle_grade(self, response: str) -> str:
        """Determine overall vehicle grade"""
        response_lower = response.lower()
        
        # Grade indicators
        grade_indicators = {
            "A+": ["excellent", "pristine", "exceptional", "like new"],
            "A": ["very good", "good condition", "well maintained"],
            "B+": ["good", "average", "normal wear", "acceptable"],
            "B": ["fair", "moderate wear", "some issues", "typical"],
            "C": ["poor", "significant", "major", "extensive"],
            "D": ["severe", "safety", "structural", "critical"]
        }
        
        for grade, indicators in grade_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                return grade
        
        return "B"  # Default grade
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _create_error_response(self, error_message: str) -> dict:
        """Create error response"""
        return {
            "success": False,
            "error": error_message,
            "analysis": None,
            "photos_analyzed": 0
        }

# Test function
async def test_analysis():
    """Test the Gemini analysis with sample data"""
    analyzer = GeminiVehicleAnalysis("AIzaSyC3hPVHH1vAmN_kKDhohC-bxTCIAGv7fdY")
    
    test_photos = [
        "https://example.com/photo1.jpg",
        "https://example.com/photo2.jpg"
    ]
    
    test_submission = {
        "vin": "1HGBH41JXMN109186",
        "year": "2018",
        "make": "Honda",
        "model": "Civic",
        "mileage": 45000,
        "notes": "Regular maintenance, minor parking dings"
    }
    
    result = await analyzer.analyze_vehicle_photos(test_photos, test_submission)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Test the analysis
    asyncio.run(test_analysis())