"use client"

import { useState, useEffect } from "react"
import { onAuthStateChanged } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { getUserRole } from "@/lib/auth-utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"

export default function DebugAuth() {
  const [user, setUser] = useState<any>(null)
  const [userRole, setUserRole] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [debugInfo, setDebugInfo] = useState<any>({})
  const router = useRouter()

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user)
        console.log("Firebase User Object:", user)
        
        const debugData = {
          userEmail: user.email,
          userUID: user.uid,
          userDisplayName: user.displayName,
          userCreated: user.metadata.creationTime,
          userLastSignIn: user.metadata.lastSignInTime
        }
        
        setDebugInfo(debugData)
        console.log("Debug Info:", debugData)
        
        try {
          const role = await getUserRole(user)
          setUserRole(role)
          console.log("Retrieved User Role:", role)
        } catch (error) {
          console.error("Error getting user role:", error)
          setUserRole({ error: error.message })
        }
      } else {
        setUser(null)
        setUserRole(null)
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  if (loading) {
    return <div className="p-8">Loading debug information...</div>
  }

  if (!user) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Debug Authentication</h1>
        <p>Please log in first to debug authentication.</p>
        <Button onClick={() => router.push('/')} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Go to Login
        </Button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-6">
          <Button onClick={() => router.push('/')} variant="outline" className="mr-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold">Authentication Debug Information</h1>
        </div>

        <div className="grid gap-6">
          {/* Firebase User Info */}
          <Card>
            <CardHeader>
              <CardTitle>Firebase User Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 font-mono text-sm">
                <div><strong>Email:</strong> {debugInfo.userEmail}</div>
                <div><strong>UID:</strong> {debugInfo.userUID}</div>
                <div><strong>Display Name:</strong> {debugInfo.userDisplayName || 'null'}</div>
                <div><strong>Created:</strong> {debugInfo.userCreated}</div>
                <div><strong>Last Sign In:</strong> {debugInfo.userLastSignIn}</div>
              </div>
            </CardContent>
          </Card>

          {/* Firestore Role Info */}
          <Card>
            <CardHeader>
              <CardTitle>Firestore Role Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 font-mono text-sm">
                {userRole ? (
                  userRole.error ? (
                    <div className="text-red-600">
                      <strong>Error retrieving role:</strong> {userRole.error}
                    </div>
                  ) : (
                    <>
                      <div><strong>Email in Firestore:</strong> {userRole.email || 'null'}</div>
                      <div><strong>Role:</strong> {userRole.role || 'null'}</div>
                      <div><strong>Created At:</strong> {userRole.createdAt ? userRole.createdAt.toString() : 'null'}</div>
                      <div className="mt-4 p-4 bg-green-100 dark:bg-green-900/20 rounded">
                        <strong>Status:</strong> Role found successfully!
                      </div>
                    </>
                  )
                ) : (
                  <div className="text-yellow-600">
                    <strong>No role found in Firestore for this user</strong>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Expected Firestore Document */}
          <Card>
            <CardHeader>
              <CardTitle>Expected Firestore Document</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 font-mono text-sm">
                <div><strong>Collection:</strong> users</div>
                <div><strong>Document ID:</strong> {debugInfo.userUID}</div>
                <div><strong>Expected Fields:</strong></div>
                <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded mt-2">
{`{
  email: "${debugInfo.userEmail}",
  role: "admin",
  createdAt: (timestamp)
}`}</pre>
              </div>
            </CardContent>
          </Card>

          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>Fix Instructions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p><strong>If no role is found, you need to create a Firestore document with:</strong></p>
                <ol className="list-decimal list-inside space-y-2">
                  <li>Go to Firebase Console → Firestore Database</li>
                  <li>Navigate to the <code>users</code> collection</li>
                  <li>Create/Update document with ID: <code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">{debugInfo.userUID}</code></li>
                  <li>Add fields:
                    <ul className="list-disc list-inside ml-4 mt-2">
                      <li><code>email</code> (string): {debugInfo.userEmail}</li>
                      <li><code>role</code> (string): admin</li>
                      <li><code>createdAt</code> (timestamp): (current timestamp)</li>
                    </ul>
                  </li>
                </ol>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}