"use client"

import { useState, useEffect, Suspense } from "react"
import { onAuthStateChanged, signOut } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { getUserRole, isAdmin, UserRole } from "@/lib/auth-utils"
import LoginForm from "@/components/login-form"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Shield, Car, BarChart3, Users, ArrowRight, Loader2 } from "lucide-react"
import MobileSalesOptimizer from "@/components/MobileSalesOptimizer"

function PageContent() {
  const [user, setUser] = useState<any>(null)
  const [userRole, setUserRole] = useState<UserRole | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user)
        console.log("🔧 DEBUG: Firebase User:", {
          email: user.email,
          uid: user.uid,
          displayName: user.displayName
        })
        
        const role = await getUserRole(user)
        console.log("🔧 DEBUG: Retrieved Role:", role)
        setUserRole(role)
      } else {
        setUser(null)
        setUserRole(null)
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const handleLogout = async () => {
    try {
      await signOut(auth)
      setUser(null)
      setUserRole(null)
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  if (loading) {
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
      <>
        {error && (
          <div className="bg-destructive/15 border border-destructive text-destructive p-4 text-center">
            {error}
          </div>
        )}
        <LoginForm onLoginSuccess={(email) => setUser({ email })} />
      </>
    )
  }

  const canAccessSubmit = userRole && ['sales', 'manager', 'admin'].includes(userRole.role)
  const canAccessManagerDashboard = userRole && ['manager', 'admin'].includes(userRole.role)
  const canAccessAdmin = userRole && isAdmin(userRole)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold">Vehicle Trade-In Management</h1>
            <Badge variant="secondary">
              Priority Appraisal AI Tool
            </Badge>
          </div>
          <div className="flex items-center space-x-4">
            {userRole && (
              <Badge 
                variant={
                  userRole.role === 'admin' ? 'destructive' :
                  userRole.role === 'manager' ? 'default' : 'secondary'
                }
              >
                {userRole.role.toUpperCase()}
              </Badge>
            )}
            <span className="text-sm text-muted-foreground">
              {user.email}
            </span>
            <Button
              onClick={handleLogout}
              variant="outline"
              size="sm"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Debug Information - Show when there's an error or no role */}
        {(error || !userRole) && (
          <div className="mb-8 p-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-yellow-800 dark:text-yellow-200">
              🔧 Debug Information
            </h3>
            <div className="space-y-2 font-mono text-sm">
              <div><strong>User Email:</strong> {user?.email}</div>
              <div><strong>User UID:</strong> {user?.uid}</div>
              <div><strong>Role Retrieved:</strong> {userRole ? JSON.stringify(userRole) : 'NULL'}</div>
              {error && <div><strong>Error:</strong> {error}</div>}
            </div>
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Fix Needed:</strong> Create a Firestore document in the <code>users</code> collection with:
              </p>
              <ul className="mt-2 text-sm text-blue-700 dark:text-blue-300 list-disc list-inside">
                <li><strong>Document ID:</strong> {user?.uid}</li>
                <li><strong>email:</strong> {user?.email}</li>
                <li><strong>role:</strong> admin</li>
                <li><strong>createdAt:</strong> (current timestamp)</li>
              </ul>
            </div>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Welcome Back!</h2>
          <p className="text-muted-foreground">
            Access your tools and manage vehicle trade-in submissions efficiently
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Submit Vehicle Card */}
          {canAccessSubmit && (
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/submit')}>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Car className="w-6 h-6 mr-3 text-primary" />
                  Submit Vehicle
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Submit a new vehicle for trade-in appraisal with photos and details
                </p>
                <div className="flex items-center text-sm text-primary">
                  <span>Start submission</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Manager Dashboard Card */}
          {canAccessManagerDashboard && (
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/manager-dashboard')}>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-6 h-6 mr-3 text-primary" />
                  Manager Dashboard
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  View analytics, track submissions, and manage the appraisal workflow
                </p>
                <div className="flex items-center text-sm text-primary">
                  <span>View dashboard</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Admin Panel Card */}
          {canAccessAdmin && (
            <Card className="hover:shadow-lg transition-shadow cursor-pointer border-red-200 dark:border-red-900" onClick={() => router.push('/admin')}>
              <CardHeader>
                <CardTitle className="flex items-center text-red-600 dark:text-red-400">
                  <Shield className="w-6 h-6 mr-3" />
                  Admin Panel
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Manage users, roles, and system administration tasks
                </p>
                <div className="flex items-center text-sm text-red-600 dark:text-red-400">
                  <span>Admin access</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Access Information */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Your Access Level
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Role:</span>
                  <Badge 
                    variant={
                      userRole?.role === 'admin' ? 'destructive' :
                      userRole?.role === 'manager' ? 'default' : 'secondary'
                    }
                  >
                    {userRole?.role.toUpperCase() || 'UNKNOWN'}
                  </Badge>
                </div>
                
                <Separator />
                
                <div className="space-y-2">
                  <p className="text-sm font-medium">Available Features:</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {canAccessSubmit && (
                      <li className="flex items-center">
                        <Car className="w-4 h-4 mr-2 text-green-600" />
                        Vehicle submission form
                      </li>
                    )}
                    {canAccessManagerDashboard && (
                      <li className="flex items-center">
                        <BarChart3 className="w-4 h-4 mr-2 text-blue-600" />
                        Manager dashboard and analytics
                      </li>
                    )}
                    {canAccessAdmin && (
                      <li className="flex items-center">
                        <Shield className="w-4 h-4 mr-2 text-red-600" />
                        Admin panel and user management
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* OCR Test Link */}
        <div className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Developer Tools</CardTitle>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => router.push('/test-ocr')} 
                variant="outline" 
                size="sm"
              >
                Test OCR Functionality
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Mobile Sales Optimizer - Only show for logged-in users */}
      <MobileSalesOptimizer />
    </div>
  )
}

export default function Page() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-xl">Loading...</span>
        </div>
      </div>
    }>
      <PageContent />
    </Suspense>
  )
}