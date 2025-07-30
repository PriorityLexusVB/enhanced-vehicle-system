"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { onAuthStateChanged } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import SimpleLoginForm from "@/components/SimpleLoginForm"

export default function HomePage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser)
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const handleLoginSuccess = (email: string) => {
    // User state will be updated by onAuthStateChanged
  }

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <SimpleLoginForm onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">Enhanced Vehicle Appraisal System</h1>
            <p className="mt-2 text-gray-600">Welcome, {user.email}</p>
          </div>
          
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Trade-In Form</h2>
              <p className="text-gray-600 mb-4">Submit vehicle information for appraisal</p>
              <button 
                onClick={() => router.push('/submit')}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Start Submission
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Manager Dashboard</h2>
              <p className="text-gray-600 mb-4">View and manage submissions</p>
              <button 
                onClick={() => router.push('/manager-dashboard')}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
              >
                View Dashboard
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Admin Panel</h2>
              <p className="text-gray-600 mb-4">System administration</p>
              <button 
                onClick={() => router.push('/admin')}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
              >
                Admin Access
              </button>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <button
              onClick={() => auth.signOut()}
              className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}