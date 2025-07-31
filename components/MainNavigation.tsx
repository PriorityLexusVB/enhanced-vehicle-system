"use client"

import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { onAuthStateChanged } from "firebase/auth"
import { auth } from "@/lib/firebaseconfig"
import { checkUserRole, isAdminUser, isManagerUser } from "@/lib/auth-utils"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Car, BarChart3, Users, LogOut, Menu, X } from "lucide-react"

export default function MainNavigation() {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<any>(null)
  const [userRole, setUserRole] = useState<any>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

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
        } catch (error) {
          console.error("Error checking user role:", error)
        }
      } else {
        setUser(null)
        setUserRole(null)
      }
    })

    return () => unsubscribe()
  }, [])

  const handleLogout = () => {
    auth.signOut()
    router.push('/')
  }

  const navigateToRoute = (route: string) => {
    router.push(route)
    setMobileMenuOpen(false)
  }

  // Don't show navigation if not logged in or not mounted (prevent hydration mismatch)
  if (!mounted || !user || !userRole) {
    return null
  }

  const canAccessSubmit = userRole?.role === 'sales' || userRole?.role === 'manager' || userRole?.role === 'admin'
  const canAccessManagerDashboard = isManagerUser(userRole) || isAdminUser(userRole)
  const canAccessAdmin = isAdminUser(userRole)

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-12">
          {/* Logo/Brand - Simplified */}
          <div className="flex items-center">
            <Button
              variant="ghost"
              onClick={() => navigateToRoute('/')}
              className="text-lg font-bold text-primary p-0"
            >
              Priority Appraisal
            </Button>
          </div>

          {/* Desktop Navigation - Simplified */}
          <div className="hidden md:flex items-center space-x-4">
            {canAccessSubmit && (
              <Button
                variant={pathname === '/submit' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => navigateToRoute('/submit')}
              >
                Submit
              </Button>
            )}

            {canAccessManagerDashboard && (
              <Button
                variant={pathname === '/manager-dashboard' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => navigateToRoute('/manager-dashboard')}
              >
                Dashboard
              </Button>
            )}

            {canAccessAdmin && (
              <Button
                variant={pathname === '/admin' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => navigateToRoute('/admin')}
              >
                Admin
              </Button>
            )}

            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu - Simplified */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white dark:bg-gray-900 py-2">
            <div className="space-y-1">
              {canAccessSubmit && (
                <Button
                  variant={pathname === '/submit' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/submit')}
                  className="w-full justify-start h-10"
                >
                  Submit Trade-In
                </Button>
              )}

              {canAccessManagerDashboard && (
                <Button
                  variant={pathname === '/manager-dashboard' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/manager-dashboard')}
                  className="w-full justify-start h-10"
                >
                  Manager Dashboard
                </Button>
              )}

              {canAccessAdmin && (
                <Button
                  variant={pathname === '/admin' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/admin')}
                  className="w-full justify-start h-10"
                >
                  Admin Panel
                </Button>
              )}

              <div className="pt-2 border-t">
                <Button 
                  variant="outline" 
                  onClick={handleLogout}
                  className="w-full justify-start h-10"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}