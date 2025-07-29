"use client"

import { useState } from "react"
import { signInWithEmailAndPassword } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { LogIn, Loader2, Shield, Sparkles } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface LoginFormProps {
  onLoginSuccess?: (email: string) => void
}

export default function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      console.log("✅ ENHANCED LOGIN SUCCESS:", userCredential.user.email)
      
      if (onLoginSuccess) {
        onLoginSuccess(userCredential.user.email || email)
      }
    } catch (error: any) {
      console.error("❌ Enhanced login error:", error)
      setError("Invalid credentials. Please check your email and password.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-700 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl border-0 bg-white/95 backdrop-blur">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
          </div>
          <div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🚀 Enhanced Vehicle System
            </CardTitle>
            <CardDescription className="text-base mt-2">
              Sign in to access the enhanced trade-in submission system
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2 justify-center">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <Sparkles className="w-3 h-3 mr-1" />
              Smart OCR Active
            </Badge>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              Mobile Optimized
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 bg-white/50"
                disabled={loading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-12 bg-white/50"
                disabled={loading}
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4 mr-2" />
                  Sign In to Enhanced System
                </>
              )}
            </Button>
          </form>

          <div className="pt-4 border-t">
            <div className="bg-blue-50 dark:bg-blue-950 rounded-lg p-4 text-center">
              <p className="text-sm text-blue-700 dark:text-blue-300 font-medium">
                🎯 Enhanced System Features Active
              </p>
              <ul className="text-xs text-blue-600 dark:text-blue-400 mt-2 space-y-1">
                <li>• VIN Scanner with Auto-Decode</li>
                <li>• Mobile-First Photo Guidance</li>
                <li>• Professional Analytics Dashboard</li>
                <li>• Smart OCR for Mileage & License Plates</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}