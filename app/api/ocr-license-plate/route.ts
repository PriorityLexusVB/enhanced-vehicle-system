import { NextRequest, NextResponse } from 'next/server'
import { ImageAnnotatorClient } from '@google-cloud/vision'

// Initialize Google Vision API client using environment variables
const vision = new ImageAnnotatorClient({
  projectId: 'priority-appraisal-ai-tool',
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
        licensePlate: 'UNREADABLE',
        confidence: 0,
        error: 'No text detected in image'
      })
    }

    // Extract all detected text
    const fullText = detections[0]?.description || ''
    console.log('Detected license plate text:', fullText)

    // License plate patterns (US format variations)
    const platePatterns = [
      /[A-Z0-9]{2,3}[\s-]?[A-Z0-9]{3,4}/g, // ABC-1234, AB-1234, etc.
      /[A-Z]{1,3}[\s-]?[0-9]{1,4}[\s-]?[A-Z]{0,2}/g, // A-123-B, etc.
      /[0-9]{1,3}[\s-]?[A-Z]{2,3}[\s-]?[0-9]{1,3}/g, // 123-ABC-45, etc.
    ]
    
    let extractedPlate = 'UNREADABLE'
    let confidence = 0

    // Clean text: remove spaces, special chars except letters/numbers
    const cleanText = fullText.replace(/[^A-Z0-9\s]/g, '').replace(/\s+/g, '')
    
    // Try different patterns
    for (const pattern of platePatterns) {
      const matches = cleanText.match(pattern)
      if (matches && matches.length > 0) {
        extractedPlate = matches[0].replace(/[\s-]/g, '').toUpperCase()
        confidence = 85
        break
      }
    }

    // Fallback: look for any sequence of 5-8 alphanumeric characters
    if (extractedPlate === 'UNREADABLE') {
      const sequences = cleanText.match(/[A-Z0-9]{5,8}/g) || []
      if (sequences.length > 0) {
        extractedPlate = sequences[0]
        confidence = 60 // Lower confidence for fallback
      }
    }

    // Validate length (US plates typically 5-8 characters)
    if (extractedPlate !== 'UNREADABLE' && (extractedPlate.length < 4 || extractedPlate.length > 8)) {
      extractedPlate = 'UNREADABLE'
      confidence = 0
    }

    return NextResponse.json({
      licensePlate: extractedPlate,
      confidence: confidence,
      rawText: fullText.substring(0, 100), // First 100 chars for debugging
      success: extractedPlate !== 'UNREADABLE',
      note: 'License plate OCR active - vehicle lookup requires registration database access'
    })

  } catch (error) {
    console.error('License plate OCR error:', error)
    return NextResponse.json({ 
      licensePlate: 'UNREADABLE',
      confidence: 0,
      error: 'OCR processing failed'
    }, { status: 500 })
  }
}