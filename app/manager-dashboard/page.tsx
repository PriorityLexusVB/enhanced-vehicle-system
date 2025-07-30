"use client"

import { useEffect, useState, Suspense } from "react"
import { onAuthStateChanged } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { checkUserRole, isAdminUser, isManagerUser } from "@/lib/auth-utils"
import EnhancedManagerDashboard from "@/components/EnhancedManagerDashboard"
import LoginForm from "@/components/login-form"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, Users, Loader2 } from "lucide-react"

function ManagerDashboardContent() {
  const [user, setUser] = useState<any>(null)
  const [userRole, setUserRole] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        setUser(currentUser)
        try {
          const role = await checkUserRole(currentUser.uid)
          setUserRole(role)
          
          // Check if user has manager or admin access
          if (!isManagerUser(role) && !isAdminUser(role)) {
            setAccessDenied(true)
          }
        } catch (error) {
          console.error("Error checking user role:", error)
          setAccessDenied(true)
        }
      } else {
        setUser(null)
        setUserRole(null)
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const handleLogout = () => {
    auth.signOut()
    setUser(null)
    setUserRole(null)
    setAccessDenied(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-96 shadow-xl">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Loading dashboard...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-xl">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <Users className="w-6 h-6 text-primary" />
              </div>
            </div>
            <CardTitle className="text-2xl">Manager Access Required</CardTitle>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (accessDenied) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 dark:from-red-950 dark:to-orange-950 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-xl border-red-200">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
            </div>
            <CardTitle className="text-2xl text-red-800 dark:text-red-200">Access Denied</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-red-600 dark:text-red-400 mb-4">
              Manager or Admin role required to access this dashboard.
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              Current role: <span className="font-medium">{userRole?.role || 'None'}</span>
            </p>
            <button
              onClick={handleLogout}
              className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg font-medium"
            >
              Switch Account
            </button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <EnhancedManagerDashboard userEmail={user.email} onLogout={handleLogout} />
}

export default function ManagerDashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading Manager Dashboard...</p>
        </div>
      </div>
    }>
      <ManagerDashboardContent />
    </Suspense>
  )
}