"use client"

import { useState, useEffect, Suspense } from "react"
import { onAuthStateChanged, User } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { getUserRole, UserRole } from "@/lib/auth-utils"
import { useRouter, useSearchParams } from "next/navigation"
import EnhancedVehicleTradeInForm from "@/components/EnhancedTradeInForm"
import LoginForm from "@/components/login-form"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Shield, ArrowLeft, Loader2 } from "lucide-react"

function SubmitPageContent() {
  const [user, setUser] = useState<User | null>(null)
  const [userRole, setUserRole] = useState<UserRole | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user)
        const role = await getUserRole(user)
        setUserRole(role)
        
        // Check RBAC: sales, manager, admin can access /submit
        if (role && !['sales', 'manager', 'admin'].includes(role.role)) {
          router.push('/?error=Access Denied - Insufficient privileges for submission')
          return
        }
      } else {
        setUser(null)
        setUserRole(null)
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [router])

  if (!mounted || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-xl">Loading...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background">
        {error && (
          <div className="bg-destructive/15 border border-destructive text-destructive p-4 text-center">
            {error}
          </div>
        )}
        <div className="flex items-center justify-center min-h-screen p-4">
          <Card className="w-full max-w-md">
            <CardContent className="pt-6">
              <div className="text-center mb-6">
                <Shield className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h1 className="text-2xl font-bold mb-2">Login Required</h1>
                <p className="text-muted-foreground">
                  Please log in to submit a vehicle for appraisal
                </p>
              </div>
              <LoginForm onLoginSuccess={() => {}} />
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <EnhancedVehicleTradeInForm />
    </div>
  )
}

export default function SubmitPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-xl">Loading...</span>
        </div>
      </div>
    }>
      <SubmitPageContent />
    </Suspense>
  )
}