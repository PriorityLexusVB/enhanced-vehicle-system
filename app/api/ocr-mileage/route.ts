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
    return NextResponse.json({ mileage: "UNREADABLE" });
  }
}

function extractMileageFromText(text: string): string {
  // Remove all non-numeric characters except spaces
  const cleanedText = text.replace(/[^\d\s]/g, " ");
  
  // Find all numeric sequences (4-6 digits typically for mileage)
  const numericMatches = cleanedText.match(/\b\d{4,6}\b/g);
  
  if (!numericMatches || numericMatches.length === 0) {
    return "UNREADABLE";
  }

  // Filter out common non-mileage numbers (like years, small numbers)
  const filteredMatches = numericMatches.filter(num => {
    const value = parseInt(num);
    // Exclude years (1900-2030) and very small numbers
    return !(value >= 1900 && value <= 2030) && value >= 1000;
  });

  if (filteredMatches.length === 0) {
    return "UNREADABLE";
  }

  // Return the longest numeric sequence as it's most likely the mileage
  const longestMatch = filteredMatches.reduce((prev, current) => 
    current.length > prev.length ? current : prev
  );

  return longestMatch;
}