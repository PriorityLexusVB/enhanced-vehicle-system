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

    if (!fullText.trim()) {
      return NextResponse.json({
        licensePlate: 'UNREADABLE',
        confidence: 0,
        success: false,
        error: 'Could not detect any text in the image. Please try a clearer photo of the license plate.',
        suggestion: 'Ensure the license plate is clearly visible, well-lit, and the characters are not obscured'
      })
    }

    // Enhanced license plate extraction - ignore stickers, state names, etc.
    console.log('Detected license plate text:', fullText)
    
    // Split into lines and filter out common non-plate text
    const lines = fullText.split('\n').map(line => line.trim().toUpperCase())
    
    // Words to ignore (registration stickers, state names, slogans)
    const ignoreWords = [
      'MONTH', 'YEAR', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC', 'EXPIRES', 'EXPIRE',
      'CALIFORNIA', 'TEXAS', 'FLORIDA', 'NEW YORK', 'ILLINOIS', 'PENNSYLVANIA',
      'OHIO', 'GEORGIA', 'NORTH CAROLINA', 'MICHIGAN', 'NEW JERSEY', 'VIRGINIA',
      'WASHINGTON', 'ARIZONA', 'MASSACHUSETTS', 'TENNESSEE', 'INDIANA', 'MISSOURI',
      'MARYLAND', 'WISCONSIN', 'COLORADO', 'MINNESOTA', 'SOUTH CAROLINA', 'ALABAMA',
      'LOUISIANA', 'KENTUCKY', 'OREGON', 'OKLAHOMA', 'CONNECTICUT', 'UTAH', 'IOWA',
      'NEVADA', 'ARKANSAS', 'MISSISSIPPI', 'KANSAS', 'NEW MEXICO', 'NEBRASKA',
      'WEST VIRGINIA', 'IDAHO', 'HAWAII', 'NEW HAMPSHIRE', 'MAINE', 'MONTANA',
      'RHODE ISLAND', 'DELAWARE', 'SOUTH DAKOTA', 'NORTH DAKOTA', 'ALASKA',
      'VERMONT', 'WYOMING', 'CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC',
      'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI', 'CO',
      'MN', 'SC', 'AL', 'LA', 'KY', 'OR', 'OK', 'CT', 'UT', 'IA', 'NV', 'AR',
      'MS', 'KS', 'NM', 'NE', 'WV', 'ID', 'HI', 'NH', 'ME', 'MT', 'RI', 'DE',
      'SD', 'ND', 'AK', 'VT', 'WY', 'REGISTRATION', 'RENEWAL', 'STICKER',
      'GOLDEN STATE', 'LONE STAR', 'SUNSHINE', 'EMPIRE STATE', 'LAND OF LINCOLN'
    ]
    
    // Filter lines to find potential plate numbers
    const candidateLines = lines.filter(line => {
      // Skip empty lines
      if (!line || line.length < 3) return false
      
      // Skip lines that are just years or months
      if (/^(19|20)\d{2}$/.test(line)) return false
      if (/^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)$/.test(line)) return false
      
      // Skip lines containing ignore words
      if (ignoreWords.some(word => line.includes(word))) return false
      
      // Must contain both letters and numbers (typical plate format)
      if (!/[A-Z]/.test(line) || !/[0-9]/.test(line)) {
        // Exception: some plates are all numbers or all letters
        if (line.length >= 4 && line.length <= 8) return true
        return false
      }
      
      return true
    })
    
    console.log('Candidate plate lines:', candidateLines)
    
    // License plate patterns (enhanced)
    const platePatterns = [
      /^[A-Z0-9]{2,3}[A-Z0-9]{3,4}$/, // ABC1234, AB1234, etc. (no spaces/dashes)
      /^[A-Z]{1,3}[0-9]{1,4}[A-Z]{0,2}$/, // A123B, ABC123, etc.
      /^[0-9]{1,3}[A-Z]{2,3}[0-9]{1,3}$/, // 123ABC45, etc.
      /^[A-Z0-9]{4,8}$/ // Any 4-8 character alphanumeric
    ]
    
    let extractedPlate = 'UNREADABLE'
    let confidence = 0

    // Try to match patterns in candidate lines
    for (const line of candidateLines) {
      const cleanLine = line.replace(/[^A-Z0-9]/g, '') // Remove spaces, dashes
      
      for (const pattern of platePatterns) {
        if (pattern.test(cleanLine) && cleanLine.length >= 4 && cleanLine.length <= 8) {
          extractedPlate = cleanLine
          confidence = 90
          console.log('Found plate match:', extractedPlate)
          break
        }
      }
      
      if (extractedPlate !== 'UNREADABLE') break
    }

    // Fallback: look for any sequence of 4-8 alphanumeric characters in full text
    if (extractedPlate === 'UNREADABLE') {
      const cleanText = fullText.replace(/[^A-Z0-9]/g, '').toUpperCase()
      const sequences = cleanText.match(/[A-Z0-9]{4,8}/g) || []
      
      for (const seq of sequences) {
        // Skip obvious non-plates (all same character, obvious years, etc.)
        if (!/^(.)\1+$/.test(seq) && !/^(19|20)\d{2}/.test(seq)) {
          extractedPlate = seq
          confidence = 70 // Lower confidence for fallback
          console.log('Fallback plate match:', extractedPlate)
          break
        }
      }
    }

    // Validate length (US plates typically 5-8 characters)
    if (extractedPlate !== 'UNREADABLE' && (extractedPlate.length < 4 || extractedPlate.length > 8)) {
      extractedPlate = 'UNREADABLE'
      confidence = 0
    }

    if (extractedPlate === 'UNREADABLE') {
      return NextResponse.json({
        licensePlate: 'UNREADABLE',
        confidence: 0,
        rawText: fullText.substring(0, 100),
        success: false,
        error: 'Could not find a valid license plate in the image. Please try a clearer photo.',
        suggestion: 'Make sure the license plate is clearly visible, well-lit, and not partially obscured. License plates are typically 4-8 characters long.',
        detectedText: fullText.substring(0, 100)
      })
    }

    return NextResponse.json({
      licensePlate: extractedPlate,
      confidence: confidence,
      rawText: fullText.substring(0, 100),
      success: true,
      note: 'License plate OCR active - vehicle lookup requires registration database access'
    })

  } catch (error) {
    console.error('License plate OCR error:', error)
    return NextResponse.json({ 
      licensePlate: 'UNREADABLE',
      confidence: 0,
      success: false,
      error: 'Failed to process the license plate image. Please try again with a different photo.',
      suggestion: 'Ensure the image is clear, well-lit, and shows the complete license plate'
    }, { status: 500 })
  }
}