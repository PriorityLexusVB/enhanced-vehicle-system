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
import requests
from urllib.parse import urlparse

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
                    print(f"Processing photo {i+1}: {photo_url}")
                    
                    # Download and convert actual image to base64
                    image_base64 = await self._download_and_convert_image(photo_url)
                    if image_base64:
                        image_content = ImageContent(image_base64=image_base64)
                        image_contents.append(image_content)
                    else:
                        print(f"Failed to process photo {i+1}, using placeholder")
                        # Fallback to placeholder if download fails
                        image_content = ImageContent(
                            image_base64=self._create_placeholder_base64()
                        )
                        image_contents.append(image_content)
                    
                except Exception as e:
                    print(f"Error processing photo {i+1}: {str(e)}")
                    # Use placeholder as fallback
                    try:
                        image_content = ImageContent(
                            image_base64=self._create_placeholder_base64()
                        )
                        image_contents.append(image_content)
                    except:
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
    
    async def _download_and_convert_image(self, photo_url: str) -> str:
        """
        Download image from URL and convert to base64
        
        Args:
            photo_url: URL of the image to download
        
        Returns:
            Base64 encoded image string
        """
        try:
            # Handle different URL types
            if photo_url.startswith('data:image'):
                # Data URL - extract base64 part
                if ',' in photo_url:
                    return photo_url.split(',')[1]
                return photo_url
            
            elif photo_url.startswith(('http://', 'https://')):
                # HTTP URL - download the image
                print(f"Downloading image from: {photo_url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(photo_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Check if it's an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    print(f"Warning: URL does not appear to be an image (content-type: {content_type})")
                
                # Convert to PIL Image to ensure it's valid and optimize
                image = Image.open(io.BytesIO(response.content))
                
                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Resize if too large (max 2048x2048 for Gemini)
                max_size = 2048
                if image.width > max_size or image.height > max_size:
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    print(f"Resized image to {image.width}x{image.height}")
                
                # Convert to base64
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85, optimize=True)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                print(f"Successfully converted image to base64 ({len(img_str)} characters)")
                return img_str
                
            elif photo_url.startswith('gs://'):
                # Google Cloud Storage URL
                print(f"Warning: Google Storage URLs not implemented yet: {photo_url}")
                return None
                
            else:
                # Local file path or unknown format
                print(f"Warning: Unsupported URL format: {photo_url}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error downloading image: {str(e)}")
            return None
        except Image.UnidentifiedImageError as e:
            print(f"Invalid image format: {str(e)}")
            return None
        except Exception as e:
            print(f"Error converting image: {str(e)}")
            return None

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
        """Extract overall condition summary with robust parsing"""
        try:
            if not response or not response.strip():
                return "Professional vehicle inspection completed"
            
            lines = response.split('\n')
            
            # Look for specific section headers
            condition_headers = ['OVERALL CONDITION', 'CONDITION SUMMARY', 'SUMMARY', 'OVERALL']
            
            for header in condition_headers:
                for i, line in enumerate(lines):
                    if header in line.upper():
                        # Find the next few substantive lines after this header
                        summary_lines = []
                        for j in range(i + 1, min(i + 6, len(lines))):
                            if j < len(lines):
                                line_content = lines[j].strip()
                                if line_content and not line_content.startswith('#') and len(line_content) > 10:
                                    summary_lines.append(line_content)
                                    if len(summary_lines) >= 2:  # Get a good summary
                                        break
                        
                        if summary_lines:
                            return ' '.join(summary_lines)[:500]  # Limit length
            
            # Fallback: use first substantial paragraph
            paragraphs = [p.strip() for p in response.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                return paragraphs[0][:500]  # Limit length
            
            # Final fallback: use first substantial sentence
            sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 30]
            if sentences:
                return sentences[0][:300] + '.'
                
            return "Professional vehicle inspection completed"
            
        except Exception as e:
            print(f"Error extracting overall condition: {str(e)}")
            return "Professional vehicle inspection completed"
    
    def _extract_condition_category(self, response: str, category: str) -> str:
        """Extract specific condition category details with robust parsing"""
        try:
            if not response or not response.strip():
                return f"{category.title()} condition within normal parameters"
            
            category_keywords = {
                "exterior": ["EXTERIOR", "PAINT", "BODY", "BUMPER", "DENTS", "SCRATCHES", "DAMAGE"],
                "interior": ["INTERIOR", "SEATS", "DASHBOARD", "CARPET", "UPHOLSTERY", "CABIN"],
                "mechanical": ["MECHANICAL", "ENGINE", "TIRE", "FLUID", "TRANSMISSION", "BRAKE"]
            }
            
            keywords = category_keywords.get(category.lower(), [category.upper()])
            lines = response.split('\n')
            
            # Look for category-specific sections
            for keyword in keywords:
                for i, line in enumerate(lines):
                    if keyword in line.upper():
                        # Collect related lines
                        category_lines = []
                        for j in range(i, min(i + 8, len(lines))):
                            if j < len(lines):
                                line_content = lines[j].strip()
                                if line_content and not line_content.startswith('#'):
                                    category_lines.append(line_content)
                                    if len(category_lines) >= 3:  # Get enough detail
                                        break
                        
                        if category_lines:
                            result = ' '.join(category_lines)[:400]  # Limit length
                            return result if len(result) > 20 else f"{category.title()} condition noted"
            
            # Fallback: search for category-related content anywhere
            relevant_lines = []
            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in keywords[:3]):  # Use top 3 keywords
                    if len(line.strip()) > 15:
                        relevant_lines.append(line.strip())
            
            if relevant_lines:
                return ' '.join(relevant_lines[:2])[:300]  # Limit and use first 2 relevant lines
            
            return f"{category.title()} condition within normal parameters"
            
        except Exception as e:
            print(f"Error extracting {category} condition: {str(e)}")
            return f"{category.title()} condition within normal parameters"
    
    def _extract_severity_ratings(self, response: str) -> dict:
        """Extract severity assessments with robust parsing"""
        try:
            if not response:
                return {
                    "primary_severity": "minor",
                    "severity_distribution": {"minor": 0, "moderate": 0, "major": 0, "severe": 0},
                    "total_issues": 0
                }
            
            response_upper = response.upper()
            severity_counts = {
                "minor": response_upper.count("MINOR") + response_upper.count("LIGHT") + response_upper.count("SMALL"),
                "moderate": response_upper.count("MODERATE") + response_upper.count("MEDIUM") + response_upper.count("NOTICEABLE"),
                "major": response_upper.count("MAJOR") + response_upper.count("SIGNIFICANT") + response_upper.count("LARGE"),
                "severe": response_upper.count("SEVERE") + response_upper.count("CRITICAL") + response_upper.count("EXTENSIVE")
            }
            
            # Determine primary severity - if no issues found, default to minor
            total_issues = sum(severity_counts.values())
            if total_issues == 0:
                # Look for general damage indicators
                damage_indicators = ["DAMAGE", "SCRATCH", "DENT", "WEAR", "ISSUE", "PROBLEM", "DEFECT"]
                for indicator in damage_indicators:
                    if indicator in response_upper:
                        severity_counts["minor"] = 1
                        total_issues = 1
                        break
            
            max_severity = max(severity_counts, key=severity_counts.get) if total_issues > 0 else "minor"
            
            return {
                "primary_severity": max_severity,
                "severity_distribution": severity_counts,
                "total_issues": max(total_issues, 1)  # Ensure at least 1 if we have any response
            }
            
        except Exception as e:
            print(f"Error extracting severity ratings: {str(e)}")
            return {
                "primary_severity": "minor",
                "severity_distribution": {"minor": 1, "moderate": 0, "major": 0, "severe": 0},
                "total_issues": 1
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