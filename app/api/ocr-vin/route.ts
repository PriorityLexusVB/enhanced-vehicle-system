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
        vin: 'UNREADABLE',
        confidence: 0,
        error: 'No text detected in image'
      })
    }

    // Extract all detected text
    const fullText = detections[0]?.description || ''
    console.log('Detected text:', fullText)

    if (!fullText.trim()) {
      return NextResponse.json({
        vin: 'UNREADABLE',
        confidence: 0,
        success: false,
        error: 'Could not detect any text in the image. Please try a clearer photo of the VIN plate.',
        suggestion: 'Ensure the VIN plate is clearly visible and well-lit. The VIN should be 17 characters long.'
      })
    }

    // ENHANCED VIN EXTRACTION - Advanced Pattern Recognition
    console.log('Raw detected text:', fullText)
    
    // Step 1: Extract ALL possible alphanumeric sequences
    const allSequences = fullText.match(/[A-HJ-NPR-Z0-9]+/gi) || []
    console.log('All alphanumeric sequences found:', allSequences)
    
    // Step 2: Filter sequences that could be VINs (exactly 17 characters)
    const candidateVINs = allSequences
      .map(seq => seq.toUpperCase().replace(/[^A-HJ-NPR-Z0-9]/g, ''))
      .filter(seq => seq.length === 17)
      .filter(seq => /^[A-HJ-NPR-Z0-9]{17}$/.test(seq)) // No I, O, Q allowed
    
    console.log('17-character VIN candidates:', candidateVINs)
    
    // Step 3: Advanced VIN validation using check digit algorithm
    const validateVIN = (vin: string): boolean => {
      if (vin.length !== 17) return false
      
      // VIN character values for check digit calculation
      const values: { [key: string]: number } = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
      }
      
      // Weight factors for each position
      const weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
      
      let sum = 0
      for (let i = 0; i < 17; i++) {
        if (i === 8) continue // Skip check digit position
        const char = vin[i]
        if (values[char] === undefined) return false
        sum += values[char] * weights[i]
      }
      
      const checkDigit = sum % 11
      const expectedCheckChar = checkDigit === 10 ? 'X' : checkDigit.toString()
      
      return vin[8] === expectedCheckChar
    }
    
    // Step 4: Find valid VINs using check digit validation
    let extractedVin = 'UNREADABLE'
    let confidence = 0
    
    for (const candidate of candidateVINs) {
      if (validateVIN(candidate)) {
        extractedVin = candidate
        confidence = 98 // Very high confidence for valid check digit
        console.log('✅ Valid VIN found with check digit validation:', extractedVin)
        break
      }
    }
    
    // Step 5: Fallback - if no valid check digit found, use pattern matching
    if (extractedVin === 'UNREADABLE' && candidateVINs.length > 0) {
      // Look for VINs with realistic manufacturer codes (1st character)
      const validFirstChars = ['1', '2', '3', '4', '5', 'J', 'K', 'W', 'Y', 'Z'] // Common countries
      
      for (const candidate of candidateVINs) {
        if (validFirstChars.includes(candidate[0])) {
          extractedVin = candidate
          confidence = 85 // Good confidence for pattern match
          console.log('✅ VIN found with pattern matching:', extractedVin)
          break
        }
      }
      
      // Final fallback - take first 17-char sequence
      if (extractedVin === 'UNREADABLE') {
        extractedVin = candidateVINs[0]
        confidence = 70
        console.log('⚠️ VIN found with basic matching:', extractedVin)
      }
    }
    
    // Step 6: Final validation - ensure it's exactly 17 characters
    if (extractedVin !== 'UNREADABLE' && extractedVin.length !== 17) {
      console.log('❌ Invalid VIN length, marking as unreadable')
      extractedVin = 'UNREADABLE'
      confidence = 0
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

    if (extractedVin === 'UNREADABLE') {
      return NextResponse.json({
        vin: 'UNREADABLE',
        confidence: 0,
        rawText: fullText.substring(0, 200),
        success: false,
        error: 'Could not find a valid 17-character VIN in the image. Please try a clearer photo.',
        suggestion: 'Make sure the entire VIN plate is visible and the characters are clear. VINs are exactly 17 characters long.',
        detectedText: fullText.substring(0, 100)
      })
    }

    return NextResponse.json({
      vin: extractedVin,
      confidence: confidence,
      rawText: fullText.substring(0, 200),
      success: true
    })

  } catch (error) {
    console.error('VIN OCR error:', error)
    return NextResponse.json({ 
      vin: 'UNREADABLE',
      confidence: 0,
      success: false,
      error: 'Failed to process the VIN image. Please try again with a different photo.',
      suggestion: 'Ensure the image is clear, well-lit, and shows the complete VIN plate'
    }, { status: 500 })
  }
}