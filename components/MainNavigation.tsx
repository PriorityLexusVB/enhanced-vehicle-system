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

  // Don't show navigation if not logged in
  if (!user || !userRole) {
    return null
  }

  const canAccessSubmit = userRole?.role === 'sales' || userRole?.role === 'manager' || userRole?.role === 'admin'
  const canAccessManagerDashboard = isManagerUser(userRole) || isAdminUser(userRole)
  const canAccessAdmin = isAdminUser(userRole)

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <Car className="w-8 h-8 text-primary mr-3" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Vehicle Appraisal System
            </span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {canAccessSubmit && (
              <Button
                variant={pathname === '/submit' ? 'default' : 'ghost'}
                onClick={() => navigateToRoute('/submit')}
                className="flex items-center"
              >
                <Car className="w-4 h-4 mr-2" />
                Trade-In Form
              </Button>
            )}

            {canAccessManagerDashboard && (
              <Button
                variant={pathname === '/manager-dashboard' ? 'default' : 'ghost'}
                onClick={() => navigateToRoute('/manager-dashboard')}
                className="flex items-center"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Manager Dashboard
              </Button>
            )}

            {canAccessAdmin && (
              <Button
                variant={pathname === '/admin' ? 'default' : 'ghost'}
                onClick={() => navigateToRoute('/admin')}
                className="flex items-center"
              >
                <Users className="w-4 h-4 mr-2" />
                Admin Panel
              </Button>
            )}

            {/* User Info */}
            <div className="flex items-center space-x-3 ml-6 pl-6 border-l">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium">{user.email}</div>
                <Badge 
                  variant={userRole?.role === 'admin' ? 'destructive' : userRole?.role === 'manager' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {userRole?.role?.toUpperCase()}
                </Badge>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white dark:bg-gray-900 py-4">
            <div className="space-y-2">
              {canAccessSubmit && (
                <Button
                  variant={pathname === '/submit' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/submit')}
                  className="w-full justify-start"
                >
                  <Car className="w-4 h-4 mr-2" />
                  Trade-In Form
                </Button>
              )}

              {canAccessManagerDashboard && (
                <Button
                  variant={pathname === '/manager-dashboard' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/manager-dashboard')}
                  className="w-full justify-start"
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Manager Dashboard
                </Button>
              )}

              {canAccessAdmin && (
                <Button
                  variant={pathname === '/admin' ? 'default' : 'ghost'}
                  onClick={() => navigateToRoute('/admin')}
                  className="w-full justify-start"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Admin Panel
                </Button>
              )}

              <div className="pt-4 border-t">
                <div className="px-4 py-2">
                  <div className="text-sm font-medium">{user.email}</div>
                  <Badge 
                    variant={userRole?.role === 'admin' ? 'destructive' : userRole?.role === 'manager' ? 'default' : 'secondary'}
                    className="text-xs mt-1"
                  >
                    {userRole?.role?.toUpperCase()}
                  </Badge>
                </div>
                <Button variant="outline" onClick={handleLogout} className="w-full mt-2">
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