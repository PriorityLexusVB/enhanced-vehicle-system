"use client"

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Smartphone, Wifi, WifiOff, Battery, BatteryLow, Signal, MapPin, Clock, AlertTriangle } from 'lucide-react'
import { toast } from "@/hooks/use-toast"

export default function MobileSalesOptimizer() {
  const [isOnline, setIsOnline] = useState(true)
  const [batteryLevel, setBatteryLevel] = useState(100)
  const [connectionSpeed, setConnectionSpeed] = useState('fast')
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null)
  const [lastSubmission, setLastSubmission] = useState<Date | null>(null)

  useEffect(() => {
    // Network status monitoring
    const handleOnline = () => {
      setIsOnline(true)
      toast({
        title: "📶 Back Online",
        description: "Internet connection restored",
      })
    }

    const handleOffline = () => {
      setIsOnline(false)
      toast({
        title: "📵 No Connection",
        description: "Working offline - data will sync when connected",
        variant: "destructive"
      })
    }

    // Battery API (if supported)
    if ('getBattery' in navigator) {
      // @ts-ignore
      navigator.getBattery().then((battery) => {
        setBatteryLevel(Math.round(battery.level * 100))
        
        battery.addEventListener('levelchange', () => {
          const level = Math.round(battery.level * 100)
          setBatteryLevel(level)
          
          if (level < 20) {
            toast({
              title: "🔋 Low Battery",
              description: "Consider charging your device",
              variant: "destructive"
            })
          }
        })
      })
    }

    // Connection speed estimation
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection
    if (connection) {
      const updateConnectionSpeed = () => {
        const speed = connection.effectiveType
        setConnectionSpeed(speed)
        
        if (speed === 'slow-2g' || speed === '2g') {
          toast({
            title: "🐌 Slow Connection",
            description: "Upload may take longer",
          })
        }
      }
      
      updateConnectionSpeed()
      connection.addEventListener('change', updateConnectionSpeed)
    }

    // Geolocation for sales tracking
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        (error) => {
          console.log('Location access denied:', error)
        }
      )
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const getConnectionIcon = () => {
    if (!isOnline) return <WifiOff className="w-4 h-4 text-red-500" />
    
    switch (connectionSpeed) {
      case '4g':
      case '5g':
        return <Wifi className="w-4 h-4 text-green-500" />
      case '3g':
        return <Signal className="w-4 h-4 text-yellow-500" />
      default:
        return <Signal className="w-4 h-4 text-orange-500" />
    }
  }

  const getBatteryIcon = () => {
    if (batteryLevel < 20) {
      return <BatteryLow className="w-4 h-4 text-red-500" />
    }
    return <Battery className="w-4 h-4 text-green-500" />
  }

  return (
    <div className="fixed top-4 right-4 z-50">
      <Card className="w-64 shadow-lg border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <Smartphone className="w-4 h-4 mr-2" />
            Sales Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Connection Status */}
          <div className="flex items-center justify-between">
            <span className="text-sm">Connection:</span>
            <div className="flex items-center">
              {getConnectionIcon()}
              <Badge 
                variant={isOnline ? "default" : "destructive"} 
                className="ml-2 text-xs"
              >
                {isOnline ? connectionSpeed.toUpperCase() : 'OFFLINE'}
              </Badge>
            </div>
          </div>

          {/* Battery Status */}
          <div className="flex items-center justify-between">
            <span className="text-sm">Battery:</span>
            <div className="flex items-center">
              {getBatteryIcon()}
              <span className="ml-2 text-sm font-medium">{batteryLevel}%</span>
            </div>
          </div>

          {/* Location Status */}
          {location && (
            <div className="flex items-center justify-between">
              <span className="text-sm">Location:</span>
              <div className="flex items-center">
                <MapPin className="w-4 h-4 text-blue-500" />
                <span className="ml-2 text-xs text-muted-foreground">Captured</span>
              </div>
            </div>
          )}

          {/* Last Submission */}
          {lastSubmission && (
            <div className="flex items-center justify-between">
              <span className="text-sm">Last Submit:</span>
              <div className="flex items-center">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span className="ml-2 text-xs text-muted-foreground">
                  {lastSubmission.toLocaleTimeString()}
                </span>
              </div>
            </div>
          )}

          {/* Warnings */}
          {(!isOnline || batteryLevel < 20) && (
            <div className="flex items-center p-2 bg-yellow-50 dark:bg-yellow-950 rounded border border-yellow-200">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              <span className="ml-2 text-xs text-yellow-700 dark:text-yellow-300">
                {!isOnline ? 'Working offline' : 'Low battery'}
              </span>
            </div>
          )}

          {/* Tips */}
          <div className="text-xs text-muted-foreground">
            💡 Tips: Take photos in good lighting, ensure clear VIN/odometer shots
          </div>
        </CardContent>
      </Card>
    </div>
  )
}