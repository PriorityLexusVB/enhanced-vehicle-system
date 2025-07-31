import { NextRequest, NextResponse } from "next/server";
import { ImageAnnotatorClient } from "@google-cloud/vision";
import path from "path";

// Initialize Google Vision client using environment variables
const client = new ImageAnnotatorClient({
  projectId: 'priority-appraisal-ai-tool',
  credentials: {
    client_email: process.env.FIREBASE_CLIENT_EMAIL,
    private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  },
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("image") as File;

    if (!file) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 });
    }

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Call Google Vision API for text detection
    const [result] = await client.textDetection({
      image: {
        content: buffer,
      },
    });

    const detectedText = result.textAnnotations?.[0]?.description || "";

    if (!detectedText) {
      return NextResponse.json({ 
        mileage: "UNREADABLE",
        success: false,
        error: "Could not detect any text in the image. Please try a clearer photo of the odometer display.",
        suggestion: "Ensure the odometer numbers are clearly visible and well-lit"
      });
    }

    // Extract numeric values from detected text
    const mileage = extractMileageFromText(detectedText);

    if (mileage === "UNREADABLE") {
      return NextResponse.json({ 
        mileage: "UNREADABLE",
        success: false,
        error: "Could not find valid mileage numbers in the image. Please take a clearer photo of the odometer.",
        suggestion: "Make sure the mileage numbers are clearly visible and in focus",
        detectedText: detectedText.substring(0, 100) // Show what was detected for debugging
      });
    }

    return NextResponse.json({ 
      mileage,
      success: true,
      detectedText: detectedText.substring(0, 100)
    });
  } catch (error) {
    console.error("OCR processing error:", error);
    return NextResponse.json({ 
      mileage: "UNREADABLE",
      success: false,
      error: "Failed to process the image. Please try again with a different photo.",
      suggestion: "Ensure the image is clear, well-lit, and shows the odometer display"
    }, { status: 500 });
  }
}

function extractMileageFromText(text: string): string {
  console.log('🔍 ADVANCED MILEAGE EXTRACTION from text:', text);
  
  // Step 1: Split text into lines and clean them
  const lines = text.split(/[\n\r]+/).map(line => line.trim()).filter(line => line.length > 0);
  console.log('Text lines:', lines);
  
  // Step 2: Advanced pattern matching for mileage displays
  const mileagePatterns = [
    /(\d{1,3}[,.]?\d{3}[,.]?\d{3})/g,  // 123,456,789 or 123.456.789
    /(\d{1,3},\d{3},\d{3})/g,          // 123,456,789
    /(\d{1,3}\s\d{3}\s\d{3})/g,        // 123 456 789
    /(\d{4,6})/g,                      // 123456 (simple 4-6 digits)
    /ODO[\s:]*(\d{4,6})/gi,            // ODO: 123456
    /MILES[\s:]*(\d{4,6})/gi,          // MILES: 123456
    /(\d+)\s*MI/gi,                    // 123456 MI
    /(\d+)\s*MILES/gi                  // 123456 MILES
  ];
  
  let allCandidates: string[] = [];
  
  // Step 3: Extract numbers using all patterns
  for (const pattern of mileagePatterns) {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(match => {
        // Extract just the numbers from the match
        const numbers = match.replace(/[^\d]/g, '');
        if (numbers.length >= 4 && numbers.length <= 7) {
          allCandidates.push(numbers);
        }
      });
    }
  }
  
  // Step 4: Look for clustered digits (common in digital odometers)
  const digitClusters = text.match(/\d{4,7}/g) || [];
  allCandidates.push(...digitClusters);
  
  // Remove duplicates
  allCandidates = [...new Set(allCandidates)];
  console.log('All mileage candidates found:', allCandidates);
  
  if (allCandidates.length === 0) {
    return "UNREADABLE";
  }
  
  // Step 5: Advanced filtering and scoring
  const scoredCandidates = allCandidates.map(candidate => {
    const value = parseInt(candidate);
    let score = 0;
    
    // Length scoring (5-6 digits most common)
    if (candidate.length === 5) score += 30;
    else if (candidate.length === 6) score += 25;
    else if (candidate.length === 4) score += 15;
    else if (candidate.length === 7) score += 10;
    
    // Realistic mileage range scoring
    if (value >= 10000 && value <= 300000) score += 40;      // Very realistic
    else if (value >= 5000 && value <= 500000) score += 25;  // Realistic
    else if (value >= 1000 && value <= 999999) score += 10;  // Possible
    
    // Avoid obvious non-mileage numbers
    if (value >= 1900 && value <= 2030) score -= 50;         // Years
    if (value < 1000) score -= 30;                           // Too low
    if (value > 999999) score -= 30;                         // Too high
    
    // Common mileage patterns bonus
    if (value % 1000 === 0) score += 5;                      // Round thousands
    if (candidate.endsWith('000')) score += 3;               // Ends in 000
    
    // Penalize obviously wrong patterns
    if (/^(\d)\1{3,}$/.test(candidate)) score -= 20;         // All same digits (1111)
    if (candidate === '12345' || candidate === '54321') score -= 30; // Sequential
    
    console.log(`Candidate ${candidate} (${value}): score ${score}`);
    
    return { candidate, value, score };
  });
  
  // Step 6: Sort by score and return best candidate
  scoredCandidates.sort((a, b) => b.score - a.score);
  
  if (scoredCandidates.length > 0 && scoredCandidates[0].score > 0) {
    const winner = scoredCandidates[0];
    console.log(`✅ Selected mileage: ${winner.candidate} (score: ${winner.score})`);
    return winner.candidate;
  }
  
  console.log('❌ No suitable mileage candidate found');
  return "UNREADABLE";
}