"use client"

import { useState, useEffect } from "react"
import { addDoc, collection, serverTimestamp } from "firebase/firestore"
import { ref, uploadBytes, getDownloadURL } from "firebase/storage"
import { db, storage } from "@/lib/firebaseconfig"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Camera, Upload, Car, CheckCircle, Loader2, Zap, Target, FileText } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import PhotoGuidance from "@/components/PhotoGuidance"

export default function EnhancedVehicleTradeInForm() {
  const [formData, setFormData] = useState({
    year: "",
    make: "",
    model: "",
    vin: "",
    mileage: "",
    notes: "",
    exterior1: null as File | null,
    exterior2: null as File | null,
    interior1: null as File | null,
    interior2: null as File | null,
    odometer: null as File | null,
    vinPhoto: null as File | null,
    licensePlate: null as File | null,
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [submitError, setSubmitError] = useState("")
  const [userEmail, setUserEmail] = useState("user@example.com")
  const [ocrProcessing, setOcrProcessing] = useState(false)
  const [ocrResult, setOcrResult] = useState("")
  const [vinOcrProcessing, setVinOcrProcessing] = useState(false)
  const [vinOcrResult, setVinOcrResult] = useState("")
  const [plateOcrProcessing, setPlateOcrProcessing] = useState(false)
  const [plateOcrResult, setPlateOcrResult] = useState("")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [isMobile, setIsMobile] = useState(false)
  const [vehicleInfo, setVehicleInfo] = useState<any>(null)
  const [vinDecoding, setVinDecoding] = useState(false)

  useEffect(() => {
    setIsMobile(window.innerWidth < 768)
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const steps = [
    { title: "Vehicle Info", icon: Car },
    { title: "Photos", icon: Camera },
    { title: "Review", icon: CheckCircle }
  ]

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (field === "vin" && value.length === 17) {
      decodeVIN(value)
    }
  }

  const decodeVIN = async (vin: string) => {
    setVinDecoding(true)
    try {
      const response = await fetch('/api/vin-decode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vin }),
      })
      const result = await response.json()
      if (result.success && result.vehicle) {
        setVehicleInfo(result.vehicle)
        setFormData(prev => ({
          ...prev,
          year: result.vehicle.year || prev.year,
          make: result.vehicle.make || prev.make,
          model: result.vehicle.model || prev.model,
        }))
        toast({
          title: "🚗 VIN Decoded!",
          description: `${result.vehicle.year} ${result.vehicle.make} ${result.vehicle.model}`,
        })
      }
    } catch (error) {
      console.error("VIN decode error:", error)
    } finally {
      setVinDecoding(false)
    }
  }

  const processOdometorOCR = async (file: File) => {
    setOcrProcessing(true)
    setOcrResult("")
    try {
      const formDataOCR = new FormData()
      formDataOCR.append("image", file)
      const response = await fetch("/api/ocr-mileage", {
        method: "POST",
        body: formDataOCR,
      })
      const result = await response.json()
      const mileage = result.mileage || "UNREADABLE"
      setOcrResult(mileage)
      if (mileage !== "UNREADABLE") {
        setFormData(prev => ({ ...prev, mileage }))
        toast({
          title: "🎯 Mileage Detected!",
          description: `Auto-read: ${mileage} miles`,
        })
      }
    } catch (error) {
      setOcrResult("UNREADABLE")
    } finally {
      setOcrProcessing(false)
    }
  }

  const processVinOCR = async (file: File) => {
    setVinOcrProcessing(true)
    setVinOcrResult("")
    try {
      const formDataOCR = new FormData()
      formDataOCR.append("image", file)
      const response = await fetch("/api/ocr-vin", {
        method: "POST",
        body: formDataOCR,
      })
      const result = await response.json()
      const vin = result.vin || "UNREADABLE"
      setVinOcrResult(vin)
      if (vin !== "UNREADABLE") {
        setFormData(prev => ({ ...prev, vin }))
        decodeVIN(vin)
        toast({
          title: "🎯 VIN Scanned!",
          description: `Extracted: ${vin}`,
        })
      }
    } catch (error) {
      setVinOcrResult("UNREADABLE")
    } finally {
      setVinOcrProcessing(false)
    }
  }

  const processLicensePlateOCR = async (file: File) => {
    setPlateOcrProcessing(true)
    setPlateOcrResult("")
    try {
      const formDataOCR = new FormData()
      formDataOCR.append("image", file)
      const response = await fetch("/api/ocr-license-plate", {
        method: "POST",
        body: formDataOCR,
      })
      const result = await response.json()
      const plate = result.licensePlate || "UNREADABLE"
      setPlateOcrResult(plate)
      if (plate !== "UNREADABLE") {
        toast({
          title: "📋 License Plate Scanned!",
          description: `Plate: ${plate}`,
        })
      }
    } catch (error) {
      setPlateOcrResult("UNREADABLE")
    } finally {
      setPlateOcrProcessing(false)
    }
  }

  const handleFileChange = async (field: string, file: File | null) => {
    setFormData(prev => ({ ...prev, [field]: file }))
    
    if (field === "odometer" && file) {
      await processOdometorOCR(file)
    } else if (field === "vinPhoto" && file) {
      await processVinOCR(file)
    } else if (field === "licensePlate" && file) {
      await processLicensePlateOCR(file)
    }
  }

  const PhotoUploadField = ({ field, label, description, processing, result, icon: Icon }: any) => (
    <div className="space-y-3">
      <Label className="text-base font-medium flex items-center">
        <Icon className="w-5 h-5 mr-2 text-primary" />
        {label}
        {processing && (
          <Badge variant="secondary" className="ml-2">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Scanning...
          </Badge>
        )}
      </Label>
      {description && <p className="text-sm text-muted-foreground">{description}</p>}
      
      <div className="relative">
        <Input
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => handleFileChange(field, e.target.files?.[0] || null)}
          className="hidden"
          id={field}
        />
        <Label
          htmlFor={field}
          className={`flex items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all hover:border-primary/50 hover:bg-accent/50 ${
            processing ? "opacity-50" : ""
          } ${formData[field] ? "border-primary bg-primary/10" : "border-border"}`}
        >
          <div className="text-center">
            {processing ? (
              <>
                <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-2" />
                <span className="text-sm font-medium">Scanning...</span>
              </>
            ) : formData[field] ? (
              <>
                <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <span className="text-sm font-medium text-green-600">Photo Captured</span>
                {result && result !== "UNREADABLE" && (
                  <div className="mt-2">
                    <Badge variant="default" className="text-xs">
                      {field === "odometer" ? `${result} miles` : 
                       field === "vinPhoto" ? result :
                       field === "licensePlate" ? result : result}
                    </Badge>
                  </div>
                )}
              </>
            ) : (
              <>
                <Icon className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <span className="text-sm">📸 Tap to Take Photo</span>
                {field === "odometer" && (
                  <Badge variant="secondary" className="text-xs mt-2">
                    <Zap className="w-3 h-3 mr-1" />
                    Auto-reads mileage
                  </Badge>
                )}
                {field === "vinPhoto" && (
                  <Badge variant="secondary" className="text-xs mt-2">
                    <Car className="w-3 h-3 mr-1" />
                    Auto-decodes VIN
                  </Badge>
                )}
                {field === "licensePlate" && (
                  <Badge variant="secondary" className="text-xs mt-2">
                    <FileText className="w-3 h-3 mr-1" />
                    Scans plate number
                  </Badge>
                )}
              </>
            )}
          </div>
        </Label>
      </div>
    </div>
  )

  const uploadFiles = async (submissionId: string) => {
    const photoUrls: string[] = []
    const files = Object.values(formData).filter(f => f instanceof File) as File[]
    const totalFiles = files.length
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const fieldName = Object.keys(formData)[Object.values(formData).indexOf(file)]
      try {
        const storageRef = ref(storage, `tradeins/${submissionId}/${fieldName}.jpg`)
        await uploadBytes(storageRef, file)
        const url = await getDownloadURL(storageRef)
        photoUrls.push(url)
        setUploadProgress(((i + 1) / totalFiles) * 100)
      } catch (error) {
        console.error(`Upload error for ${fieldName}:`, error)
      }
    }
    return photoUrls
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setUploadProgress(0)

    try {
      const submissionId = `submission_${Date.now()}`
      const photoUrls = await uploadFiles(submissionId)

      const submission = {
        submittedBy: userEmail,
        vin: formData.vin,
        year: formData.year,
        make: formData.make,
        model: formData.model,
        mileage: parseInt(formData.mileage) || 0,
        notes: formData.notes,
        photoUrls,
        createdAt: serverTimestamp(),
        submissionId,
        vehicleInfo,
        ocrResults: {
          mileage: ocrResult,
          vin: vinOcrResult,
          licensePlate: plateOcrResult
        }
      }

      await addDoc(collection(db, "appraisals"), submission)
      setSubmitSuccess(true)
      
    } catch (error) {
      setSubmitError("Submission failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (submitSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-xl">
          <CardContent className="pt-8 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-4 text-green-800">Success! 🎉</h2>
            {vehicleInfo && (
              <div className="bg-green-50 p-4 rounded-lg mb-4">
                <h3 className="font-semibold">{vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}</h3>
                <p className="text-sm text-green-700">Trade-in Value: {vehicleInfo.tradeInValue}</p>
              </div>
            )}
            <p className="text-muted-foreground mb-6">Vehicle submitted for appraisal review</p>
            <Button onClick={() => setSubmitSuccess(false)} className="w-full">
              Submit Another Vehicle
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const MobileStepIndicator = () => (
    <div className="flex justify-between items-center mb-6">
      {steps.map((step, index) => (
        <div key={index} className="flex flex-col items-center">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            index <= currentStep ? 'bg-primary text-primary-foreground' : 'bg-muted'
          }`}>
            <step.icon className="w-5 h-5" />
          </div>
          <span className={`text-xs mt-1 ${index <= currentStep ? 'text-primary font-medium' : 'text-muted-foreground'}`}>
            {step.title}
          </span>
        </div>
      ))}
    </div>
  )

  if (isMobile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="sticky top-0 bg-white/95 backdrop-blur border-b p-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🚀 Enhanced Trade-In v6.0
            </h1>
            <Badge variant="default" className="bg-green-100 text-green-800">
              ✨ Smart OCR Active
            </Badge>
          </div>
          <MobileStepIndicator />
        </div>

        <div className="p-4 pb-20">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 0: Vehicle Info */}
            {currentStep === 0 && (
              <Card className="shadow-lg">
                <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                  <CardTitle className="flex items-center">
                    <Car className="w-5 h-5 mr-2" />
                    Vehicle Details
                    {vehicleInfo && (
                      <Badge className="ml-2 bg-white text-blue-600">
                        Auto-filled
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-4">
                  <div>
                    <Label className="flex items-center mb-2">
                      🔍 VIN Number {vinDecoding && <Loader2 className="w-4 h-4 ml-2 animate-spin" />}
                    </Label>
                    <Input
                      placeholder="Enter 17-digit VIN"
                      value={formData.vin}
                      onChange={(e) => handleInputChange("vin", e.target.value.toUpperCase())}
                      maxLength={17}
                      className="text-center font-mono"
                      required
                    />
                    {vehicleInfo && (
                      <div className="mt-2 p-3 bg-green-50 rounded-lg border border-green-200">
                        <div className="text-sm font-medium text-green-800">
                          ✅ {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}
                        </div>
                        <div className="text-xs text-green-600">
                          Trade-in: {vehicleInfo.tradeInValue}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <Label>Year</Label>
                      <Input
                        type="number"
                        value={formData.year}
                        onChange={(e) => handleInputChange("year", e.target.value)}
                        className="text-center"
                        required
                      />
                    </div>
                    <div>
                      <Label>Make</Label>
                      <Input
                        value={formData.make}
                        onChange={(e) => handleInputChange("make", e.target.value)}
                        className="text-center"
                        required
                      />
                    </div>
                    <div>
                      <Label>Model</Label>
                      <Input
                        value={formData.model}
                        onChange={(e) => handleInputChange("model", e.target.value)}
                        className="text-center"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Mileage</Label>
                    <Input
                      type="number"
                      placeholder="Enter mileage or scan odometer"
                      value={formData.mileage}
                      onChange={(e) => handleInputChange("mileage", e.target.value)}
                      className="text-center"
                      required
                    />
                  </div>

                  <div>
                    <Label>Notes (Optional)</Label>
                    <Textarea
                      placeholder="Additional vehicle details..."
                      value={formData.notes}
                      onChange={(e) => handleInputChange("notes", e.target.value)}
                      rows={3}
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 1: Smart Photo Capture */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <Card className="shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white">
                    <CardTitle className="flex items-center">
                      <Camera className="w-5 h-5 mr-2" />
                      Smart Photo Capture
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 space-y-6">
                    <PhotoUploadField
                      field="vinPhoto"
                      label="VIN Plate Scanner"
                      description="📸 Scan VIN plate → Auto-extract VIN → Auto-decode vehicle"
                      processing={vinOcrProcessing}
                      result={vinOcrResult}
                      icon={Target}
                    />
                    
                    <PhotoUploadField
                      field="licensePlate"
                      label="License Plate Scanner"
                      description="📋 Alternative vehicle identification method"
                      processing={plateOcrProcessing}
                      result={plateOcrResult}
                      icon={FileText}
                    />
                    
                    <PhotoUploadField
                      field="odometer"
                      label="Odometer Scanner"
                      description="🤖 Auto-read mileage from odometer display"
                      processing={ocrProcessing}
                      result={ocrResult}
                      icon={Zap}
                    />
                    
                    <PhotoUploadField
                      field="exterior1"
                      label="Front/Side Exterior"
                      description="Front and driver side view"
                      processing={false}
                      result=""
                      icon={Camera}
                    />
                    
                    <PhotoUploadField
                      field="exterior2"
                      label="Rear Exterior"
                      description="Back view of vehicle"
                      processing={false}
                      result=""
                      icon={Camera}
                    />
                    
                    <PhotoUploadField
                      field="interior1"
                      label="Interior Dashboard"
                      description="Dashboard and front seats"
                      processing={false}
                      result=""
                      icon={Camera}
                    />
                    
                    <PhotoUploadField
                      field="interior2"
                      label="Interior Rear"
                      description="Back seats and cargo area"
                      processing={false}
                      result=""
                      icon={Camera}
                    />
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Step 2: Review */}
            {currentStep === 2 && (
              <Card className="shadow-lg">
                <CardHeader className="bg-gradient-to-r from-green-500 to-emerald-600 text-white">
                  <CardTitle className="flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Review & Submit
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-4">
                  {vehicleInfo && (
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h3 className="font-medium">🚗 Vehicle Information</h3>
                      <p><strong>Vehicle:</strong> {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}</p>
                      <p><strong>VIN:</strong> {formData.vin}</p>
                      <p><strong>Mileage:</strong> {formData.mileage} miles</p>
                      <p><strong>Trade-in Value:</strong> <span className="text-green-600 font-semibold">{vehicleInfo.tradeInValue}</span></p>
                    </div>
                  )}
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">📸 Capture Summary</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {[
                        { key: 'vinPhoto', label: 'VIN Plate' },
                        { key: 'licensePlate', label: 'License Plate' },
                        { key: 'odometer', label: 'Odometer' },
                        { key: 'exterior1', label: 'Front/Side' },
                        { key: 'exterior2', label: 'Rear' },
                        { key: 'interior1', label: 'Dashboard' },
                        { key: 'interior2', label: 'Interior' }
                      ].map(({ key, label }) => (
                        <div key={key} className="flex items-center">
                          {formData[key as keyof typeof formData] ? 
                            <CheckCircle className="w-4 h-4 text-green-600 mr-1" /> : 
                            <div className="w-4 h-4 border border-gray-400 rounded mr-1" />
                          }
                          <span className={formData[key as keyof typeof formData] ? 'text-green-600' : 'text-gray-500'}>
                            {label}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-green-50 p-3 rounded-lg text-center">
                    <span className="text-green-700 text-sm">
                      ✨ Smart OCR System Active • Ready for submission
                    </span>
                  </div>
                </CardContent>
              </Card>
            )}

            {uploadProgress > 0 && uploadProgress < 100 && (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading Photos...</span>
                      <span>{Math.round(uploadProgress)}%</span>
                    </div>
                    <Progress value={uploadProgress} />
                  </div>
                </CardContent>
              </Card>
            )}
          </form>
        </div>

        {/* Mobile Navigation */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
          <div className="flex gap-3">
            {currentStep > 0 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => setCurrentStep(currentStep - 1)}
                className="flex-1"
              >
                ← Previous
              </Button>
            )}
            
            {currentStep < 2 ? (
              <Button
                type="button"
                onClick={() => setCurrentStep(currentStep + 1)}
                className="flex-1"
                disabled={currentStep === 0 && (!formData.vin || !formData.year || !formData.make)}
              >
                Next →
              </Button>
            ) : (
              <Button
                type="submit"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Submit Vehicle
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Desktop version
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <Card className="max-w-4xl mx-auto shadow-xl">
        <CardHeader className="text-center bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <CardTitle className="text-3xl font-bold">
            🚀 Enhanced Trade-In System v6.0
          </CardTitle>
          <p className="text-blue-100">Smart OCR • VIN Scanner • License Plate Reader</p>
        </CardHeader>
        <CardContent className="p-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <h3 className="text-xl font-semibold">Vehicle Information</h3>
                
                <div>
                  <Label className="flex items-center mb-2">
                    VIN Number {vinDecoding && <Loader2 className="w-4 h-4 ml-2 animate-spin" />}
                  </Label>
                  <Input
                    placeholder="Enter 17-digit VIN"
                    value={formData.vin}
                    onChange={(e) => handleInputChange("vin", e.target.value.toUpperCase())}
                    maxLength={17}
                    className="font-mono"
                  />
                  {vehicleInfo && (
                    <div className="mt-2 p-3 bg-green-50 rounded-lg">
                      <div className="font-medium text-green-800">
                        ✅ {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}
                      </div>
                      <div className="text-sm text-green-600">
                        Trade-in Value: {vehicleInfo.tradeInValue}
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Year</Label>
                    <Input
                      type="number"
                      value={formData.year}
                      onChange={(e) => handleInputChange("year", e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Make</Label>
                    <Input
                      value={formData.make}
                      onChange={(e) => handleInputChange("make", e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Model</Label>
                    <Input
                      value={formData.model}
                      onChange={(e) => handleInputChange("model", e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <Label>Mileage</Label>
                  <Input
                    type="number"
                    placeholder="Enter mileage or scan odometer"
                    value={formData.mileage}
                    onChange={(e) => handleInputChange("mileage", e.target.value)}
                  />
                </div>

                <div>
                  <Label>Notes</Label>
                  <Textarea
                    placeholder="Additional vehicle details..."
                    value={formData.notes}
                    onChange={(e) => handleInputChange("notes", e.target.value)}
                    rows={4}
                  />
                </div>
              </div>

              <div className="space-y-6">
                <h3 className="text-xl font-semibold">Smart Photo Capture</h3>
                <div className="space-y-4">
                  <PhotoUploadField
                    field="vinPhoto"
                    label="VIN Plate Scanner"
                    description="Scan VIN → Auto-decode vehicle info"
                    processing={vinOcrProcessing}
                    result={vinOcrResult}
                    icon={Target}
                  />
                  
                  <PhotoUploadField
                    field="licensePlate"
                    label="License Plate Scanner"
                    description="Alternative vehicle identification"
                    processing={plateOcrProcessing}
                    result={plateOcrResult}
                    icon={FileText}
                  />
                  
                  <PhotoUploadField
                    field="odometer"
                    label="Odometer Scanner"
                    description="Auto-read mileage display"
                    processing={ocrProcessing}
                    result={ocrResult}
                    icon={Zap}
                  />
                </div>
              </div>
            </div>

            {uploadProgress > 0 && (
              <div>
                <Progress value={uploadProgress} />
                <p className="text-center text-sm mt-2">{Math.round(uploadProgress)}% uploaded</p>
              </div>
            )}

            <Button type="submit" disabled={isSubmitting} className="w-full h-12 text-lg">
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Submitting Enhanced Trade-In...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  Submit Enhanced Vehicle
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}