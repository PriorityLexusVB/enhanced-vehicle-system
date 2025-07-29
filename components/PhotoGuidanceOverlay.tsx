"use client"

import React from 'react'
import { Camera, Target, AlertCircle, CheckCircle, Zap } from 'lucide-react'
import { Badge } from "@/components/ui/badge"

interface PhotoGuidanceOverlayProps {
  photoType: 'exterior1' | 'exterior2' | 'interior1' | 'interior2' | 'odometer' | 'vinPhoto'
  isActive: boolean
  hasPhoto: boolean
}

export default function PhotoGuidanceOverlay({ photoType, isActive, hasPhoto }: PhotoGuidanceOverlayProps) {
  const getGuidanceConfig = (type: string) => {
    switch (type) {
      case 'exterior1':
        return {
          title: "Front/Side Exterior",
          instructions: "Position car at 45° angle showing front and driver side",
          overlayPath: "M20 40 L80 40 L85 60 L75 80 L25 80 L15 60 Z", // Car outline
          checkpoints: [
            "✓ Front bumper visible",
            "✓ Driver side panel",
            "✓ Headlights clear",
            "✓ Front tires visible"
          ],
          damageZones: ["Bumper", "Hood", "Fender", "Headlights"],
          color: "#10B981"
        }
      
      case 'exterior2':
        return {
          title: "Rear Exterior",
          instructions: "Full rear view showing bumper, taillights, and license plate",
          overlayPath: "M25 40 L75 40 L80 60 L70 80 L30 80 L20 60 Z",
          checkpoints: [
            "✓ Rear bumper centered",
            "✓ Taillights visible",
            "✓ License plate readable",
            "✓ Rear tires visible"
          ],
          damageZones: ["Rear Bumper", "Trunk", "Taillights"],
          color: "#8B5CF6"
        }

      case 'interior1':
        return {
          title: "Interior Dashboard",
          instructions: "Clear view of dashboard, steering wheel, and front seats",
          overlayPath: "M20 30 L80 30 L80 70 L20 70 Z",
          checkpoints: [
            "✓ Dashboard visible",
            "✓ Steering wheel centered",
            "✓ Front seats in frame",
            "✓ Good lighting"
          ],
          damageZones: ["Dashboard", "Seats", "Console", "Steering"],
          color: "#F59E0B"
        }

      case 'interior2':
        return {
          title: "Interior Rear",
          instructions: "Rear seats and cargo area condition",
          overlayPath: "M15 35 L85 35 L85 65 L15 65 Z",
          checkpoints: [
            "✓ Rear seats visible",
            "✓ Cargo area clear",
            "✓ Upholstery condition",
            "✓ No obstructions"
          ],
          damageZones: ["Rear Seats", "Cargo Area", "Door Panels"],
          color: "#EF4444"
        }

      case 'odometer':
        return {
          title: "Odometer Reading",
          instructions: "Crystal clear shot of mileage display - AI will auto-read",
          overlayPath: "M30 45 L70 45 L70 55 L30 55 Z",
          checkpoints: [
            "✓ Numbers clearly visible",
            "✓ No glare on screen",
            "✓ Full display in frame",
            "✓ High contrast"
          ],
          damageZones: ["Display Quality"],
          color: "#06B6D4",
          isSpecial: true
        }

      case 'vinPhoto':
        return {
          title: "VIN Plate",
          instructions: "Sharp photo of VIN number - will auto-populate vehicle info",
          overlayPath: "M25 45 L75 45 L75 55 L25 55 Z",
          checkpoints: [
            "✓ All 17 digits visible",
            "✓ No shadows/glare",
            "✓ Straight angle",
            "✓ Sharp focus"
          ],
          damageZones: ["VIN Legibility"],
          color: "#8B5CF6",
          isSpecial: true
        }

      default:
        return {
          title: "Photo Capture",
          instructions: "Position subject clearly in frame",
          overlayPath: "",
          checkpoints: [],
          damageZones: [],
          color: "#6B7280"
        }
    }
  }

  const config = getGuidanceConfig(photoType)

  if (!isActive) return null

  return (
    <div className="absolute inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
        {/* Header */}
        <div className="text-center mb-4">
          <div className="flex items-center justify-center mb-2">
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: config.color + '20' }}
            >
              <Camera className="w-6 h-6" style={{ color: config.color }} />
            </div>
          </div>
          <h3 className="text-lg font-bold">{config.title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{config.instructions}</p>
          
          {config.isSpecial && (
            <Badge variant="secondary" className="mt-2">
              <Zap className="w-3 h-3 mr-1" />
              Auto-Detection
            </Badge>
          )}
        </div>

        {/* Visual Guide */}
        <div className="relative bg-gray-100 dark:bg-gray-800 rounded-lg h-32 mb-4 overflow-hidden">
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full"
            fill="none"
            stroke={config.color}
            strokeWidth="2"
            strokeDasharray="5,5"
          >
            {config.overlayPath && (
              <path
                d={config.overlayPath}
                fill={config.color + '20'}
                stroke={config.color}
                strokeWidth="2"
                strokeDasharray="5,5"
              />
            )}
            
            {/* Targeting guides */}
            <circle cx="50" cy="50" r="3" fill={config.color} />
            <line x1="45" y1="50" x2="55" y2="50" stroke={config.color} strokeWidth="1" />
            <line x1="50" y1="45" x2="50" y2="55" stroke={config.color} strokeWidth="1" />
          </svg>
          
          <div className="absolute top-2 left-2">
            <Badge variant="outline" className="text-xs">
              <Target className="w-3 h-3 mr-1" />
              Position Guide
            </Badge>
          </div>
        </div>

        {/* Checklist */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold mb-2 flex items-center">
            <CheckCircle className="w-4 h-4 mr-1 text-green-600" />
            Photo Checklist:
          </h4>
          <div className="space-y-1">
            {config.checkpoints.map((point, index) => (
              <div key={index} className="text-xs text-muted-foreground flex items-center">
                <div className="w-1 h-1 bg-green-600 rounded-full mr-2" />
                {point}
              </div>
            ))}
          </div>
        </div>

        {/* Damage Assessment Zones */}
        {config.damageZones.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1 text-orange-500" />
              Focus Areas:
            </h4>
            <div className="flex flex-wrap gap-1">
              {config.damageZones.map((zone, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {zone}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Tips */}
        <div className="bg-blue-50 dark:bg-blue-950 rounded-lg p-3 mb-4">
          <div className="flex items-start">
            <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 mr-2 mt-0.5">
              <span className="text-white text-xs font-bold">💡</span>
            </div>
            <div className="text-xs text-blue-700 dark:text-blue-300">
              {photoType === 'odometer' && "Hold steady for 2-3 seconds. AI will automatically read the mileage."}
              {photoType === 'vinPhoto' && "Position phone directly above VIN plate. All 17 characters must be visible."}
              {photoType === 'exterior1' && "Step back 8-10 feet. Ensure entire vehicle section fits in frame."}
              {photoType === 'exterior2' && "Center the vehicle. Look for any visible damage or dents."}
              {photoType.includes('interior') && "Use natural lighting when possible. Avoid flash if screens are visible."}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          className="w-full py-3 px-4 rounded-lg font-medium text-white transition-all"
          style={{ backgroundColor: config.color }}
        >
          📸 I'm Ready - Take Photo
        </button>
      </div>
    </div>
  )
}