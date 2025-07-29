"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, Camera, CheckCircle } from "lucide-react"

export default function TestOCRPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [ocrResult, setOcrResult] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState("")

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)
    setOcrResult("")
    setError("")
  }

  const processOCR = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError("")
    setOcrResult("")

    try {
      const formData = new FormData()
      formData.append("image", selectedFile)

      const response = await fetch("/api/ocr-mileage", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setOcrResult(result.mileage || "UNREADABLE")
    } catch (err) {
      console.error("OCR processing failed:", err)
      setError("Failed to process image. Please try again.")
      setOcrResult("UNREADABLE")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-2xl mx-auto">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-white">
              OCR Mileage Extraction Test
            </CardTitle>
            <p className="text-gray-400">
              Upload an odometer photo to test Google Vision OCR
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-200">
                Odometer Photo
              </Label>
              <div className="relative">
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="bg-gray-700 border-gray-600 text-white file:bg-blue-600 file:text-white file:border-none file:rounded"
                />
              </div>
              {selectedFile && (
                <p className="text-xs text-green-400">
                  ✓ Selected: {selectedFile.name}
                </p>
              )}
            </div>

            {/* Process Button */}
            <Button
              onClick={processOCR}
              disabled={!selectedFile || isProcessing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing OCR...
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4 mr-2" />
                  Extract Mileage
                </>
              )}
            </Button>

            {/* Results */}
            {ocrResult && (
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-200">Result:</Label>
                <div 
                  className={`p-4 rounded border ${
                    ocrResult === "UNREADABLE" 
                      ? "border-red-600 bg-red-900/20" 
                      : "border-green-600 bg-green-900/20"
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {ocrResult === "UNREADABLE" ? (
                      <>
                        <span className="text-red-400">⚠️</span>
                        <span className="text-red-400">Could not extract mileage from image</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-green-400">Extracted Mileage: </span>
                        <span className="text-white font-bold text-xl">{ocrResult}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="p-4 rounded border border-red-600 bg-red-900/20">
                <p className="text-red-400">{error}</p>
              </div>
            )}

            {/* Instructions */}
            <div className="p-4 rounded border border-blue-600 bg-blue-900/20">
              <h3 className="text-blue-400 font-medium mb-2">Instructions:</h3>
              <ul className="text-blue-300 text-sm space-y-1">
                <li>• Upload a clear photo of your vehicle's odometer</li>
                <li>• Works with both digital and analog odometers</li>
                <li>• Ensure numbers are clearly visible</li>
                <li>• Returns "UNREADABLE" if mileage cannot be detected</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}