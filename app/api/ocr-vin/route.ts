import { NextRequest, NextResponse } from 'next/server'
import { ImageAnnotatorClient } from '@google-cloud/vision'

// Initialize Google Vision API client using environment variables
const vision = new ImageAnnotatorClient({
  projectId: 'trade-in-vision-api',
  credentials: {
    client_email: process.env.FIREBASE_CLIENT_EMAIL,
    private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  },
})

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const image = formData.get('image') as File
    
    if (!image) {
      return NextResponse.json({ error: 'No image provided' }, { status: 400 })
    }

    // Convert image to buffer
    const imageBuffer = await image.arrayBuffer()
    const buffer = Buffer.from(imageBuffer)

    // Use Google Vision API for text detection
    const [result] = await vision.textDetection({
      image: { content: buffer }
    })

    const detections = result.textAnnotations || []
    
    if (detections.length === 0) {
      return NextResponse.json({ 
        vin: 'UNREADABLE',
        confidence: 0,
        error: 'No text detected in image'
      })
    }

    // Extract all detected text
    const fullText = detections[0]?.description || ''
    console.log('Detected text:', fullText)

    // VIN pattern: 17 characters, alphanumeric (excluding I, O, Q)
    const vinPattern = /[A-HJ-NPR-Z0-9]{17}/g
    const vinMatches = fullText.replace(/\s/g, '').match(vinPattern)
    
    let extractedVin = 'UNREADABLE'
    let confidence = 0

    if (vinMatches && vinMatches.length > 0) {
      // Take the first valid VIN match
      extractedVin = vinMatches[0].toUpperCase()
      confidence = 95 // High confidence for pattern match
      
      console.log('Extracted VIN:', extractedVin)
    } else {
      // Try to find 17-character sequences that might be VINs
      const sequences = fullText.replace(/\s/g, '').match(/.{17}/g) || []
      
      for (const seq of sequences) {
        // Check if it contains typical VIN characters
        if (/^[A-HJ-NPR-Z0-9]{17}$/.test(seq.toUpperCase())) {
          extractedVin = seq.toUpperCase()
          confidence = 75 // Medium confidence
          break
        }
      }
    }

    // Additional validation for VIN format
    if (extractedVin !== 'UNREADABLE') {
      // VINs don't contain I, O, or Q
      if (/[IOQ]/.test(extractedVin)) {
        // Try to correct common OCR mistakes
        extractedVin = extractedVin
          .replace(/I/g, '1')
          .replace(/O/g, '0')
          .replace(/Q/g, '0')
      }
      
      // Final length check
      if (extractedVin.length !== 17) {
        extractedVin = 'UNREADABLE'
        confidence = 0
      }
    }

    return NextResponse.json({
      vin: extractedVin,
      confidence: confidence,
      rawText: fullText.substring(0, 200), // First 200 chars for debugging
      success: extractedVin !== 'UNREADABLE'
    })

  } catch (error) {
    console.error('VIN OCR error:', error)
    return NextResponse.json({ 
      vin: 'UNREADABLE',
      confidence: 0,
      error: 'OCR processing failed'
    }, { status: 500 })
  }
}