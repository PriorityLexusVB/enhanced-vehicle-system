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
  console.log('Extracting mileage from text:', text);
  
  // Split text into lines for better analysis
  const lines = text.split('\n').map(line => line.trim());
  
  // Words to ignore (odometer-related but not the actual mileage)
  const ignoreWords = ['ODO', 'ODOMETER', 'MILES', 'MI', 'MPH', 'KM', 'KMH', 
                       'TRIP', 'RESET', 'TOTAL', 'ENGINE', 'HOURS', 'AVG', 'MAX'];
  
  // Look for lines that might contain mileage
  const candidateLines = lines.filter(line => {
    const upperLine = line.toUpperCase();
    
    // Skip lines with ignore words only
    if (ignoreWords.some(word => upperLine.includes(word) && !(/\d{4,}/.test(line)))) {
      return false;
    }
    
    // Must contain at least 4 consecutive digits
    return /\d{4,}/.test(line);
  });
  
  console.log('Candidate mileage lines:', candidateLines);
  
  // Extract all numeric sequences from candidate lines
  let allNumbers = [];
  
  for (const line of candidateLines) {
    // Find sequences of 4-6 digits (typical mileage range)
    const numbers = line.match(/\d{4,6}/g) || [];
    allNumbers.push(...numbers);
  }
  
  // If no candidates from filtered lines, check all text
  if (allNumbers.length === 0) {
    allNumbers = text.match(/\d{4,6}/g) || [];
  }
  
  console.log('All found numbers:', allNumbers);
  
  if (allNumbers.length === 0) {
    return "UNREADABLE";
  }

  // Filter out obvious non-mileage numbers
  const filteredNumbers = allNumbers.filter(num => {
    const value = parseInt(num);
    // Exclude:
    // - Years (1900-2030)
    // - Numbers too small (< 10,000 is unusual for mileage)
    // - Numbers too large (> 999,999 is unrealistic)
    // - Obvious speedometer readings (> 200 and < 1000)
    return !(value >= 1900 && value <= 2030) && 
           value >= 10000 && 
           value <= 999999 &&
           !(value >= 200 && value < 1000);
  });
  
  console.log('Filtered mileage numbers:', filteredNumbers);

  if (filteredNumbers.length === 0) {
    // Fallback: look for any 5-6 digit number (most likely mileage)
    const fallbackNumbers = allNumbers.filter(num => {
      const value = parseInt(num);
      return num.length >= 5 && value >= 10000 && value <= 999999;
    });
    
    if (fallbackNumbers.length > 0) {
      return fallbackNumbers[0]; // Take first reasonable number
    }
    
    return "UNREADABLE";
  }

  // If multiple candidates, prefer:
  // 1. Numbers in the middle range (50k-300k is common)
  // 2. Longer numbers (6 digits over 5, 5 over 4)
  const sortedNumbers = filteredNumbers.sort((a, b) => {
    const valA = parseInt(a);
    const valB = parseInt(b);
    
    // Prefer numbers in typical mileage range
    const isTypicalA = valA >= 50000 && valA <= 300000;
    const isTypicalB = valB >= 50000 && valB <= 300000;
    
    if (isTypicalA && !isTypicalB) return -1;
    if (!isTypicalA && isTypicalB) return 1;
    
    // Then prefer longer numbers
    if (a.length !== b.length) return b.length - a.length;
    
    // Finally prefer smaller numbers (less likely to be errors)
    return valA - valB;
  });

  console.log('Final mileage selection:', sortedNumbers[0]);
  return sortedNumbers[0];
}