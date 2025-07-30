import React from 'react'

interface PhotoGuidanceProps {
  photoType: 'front' | 'rear' | 'driver-side' | 'passenger-side' | 'interior-front' | 'interior-rear' | 'dashboard' | 'odometer' | 'vin' | 'license-plate' | 'engine-bay' | 'undercarriage'
  isActive: boolean
}

const PhotoGuidance: React.FC<PhotoGuidanceProps> = ({ photoType, isActive }) => {
  const guidanceData = {
    'front': {
      title: 'Front View',
      instruction: 'Center the vehicle front, include full width of car and headlights',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          {/* Car Front Silhouette */}
          <path 
            d="M50 120 L50 100 Q50 90 60 90 L90 90 L90 70 Q90 60 100 60 L200 60 Q210 60 210 70 L210 90 L240 90 Q250 90 250 100 L250 120 L250 140 Q250 150 240 150 L220 150 Q210 150 210 140 L210 130 L90 130 L90 140 Q90 150 80 150 L60 150 Q50 150 50 140 Z" 
            fill="none" 
            stroke="#3b82f6" 
            strokeWidth="2" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          {/* Headlights */}
          <circle cx="80" cy="90" r="8" fill="none" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="220" cy="90" r="8" fill="none" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3" />
          {/* Wheels */}
          <circle cx="80" cy="140" r="15" fill="none" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="220" cy="140" r="15" fill="none" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3" />
        </svg>
      )
    },
    'rear': {
      title: 'Rear View',
      instruction: 'Center the vehicle rear, include full width and taillights',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <path 
            d="M50 120 L50 100 Q50 90 60 90 L90 90 L90 70 Q90 60 100 60 L200 60 Q210 60 210 70 L210 90 L240 90 Q250 90 250 100 L250 120 L250 140 Q250 150 240 150 L220 150 Q210 150 210 140 L210 130 L90 130 L90 140 Q90 150 80 150 L60 150 Q50 150 50 140 Z" 
            fill="none" 
            stroke="#ef4444" 
            strokeWidth="2" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <circle cx="80" cy="90" r="6" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="220" cy="90" r="6" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="80" cy="140" r="15" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="220" cy="140" r="15" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="3,3" />
        </svg>
      )
    },
    'driver-side': {
      title: 'Driver Side Profile',
      instruction: 'Capture full side profile, all doors and wheels visible',
      silhouette: (
        <svg viewBox="0 0 400 200" className="w-full h-full">
          <path 
            d="M50 140 L80 140 L80 120 Q80 110 90 110 L120 110 L120 80 Q120 70 130 70 L270 70 Q280 70 280 80 L280 110 L310 110 Q320 110 320 120 L320 140 L350 140 L350 150 Q350 160 340 160 L320 160 Q310 160 310 150 L310 145 L90 145 L90 150 Q90 160 80 160 L60 160 Q50 160 50 150 Z" 
            fill="none" 
            stroke="#10b981" 
            strokeWidth="2" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <circle cx="100" cy="150" r="18" fill="none" stroke="#10b981" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="300" cy="150" r="18" fill="none" stroke="#10b981" strokeWidth="2" strokeDasharray="3,3" />
          {/* Door lines */}
          <line x1="160" y1="70" x2="160" y2="140" stroke="#10b981" strokeWidth="1" strokeDasharray="2,2" />
          <line x1="220" y1="70" x2="220" y2="140" stroke="#10b981" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    },
    'passenger-side': {
      title: 'Passenger Side Profile',
      instruction: 'Capture full side profile from passenger side',
      silhouette: (
        <svg viewBox="0 0 400 200" className="w-full h-full">
          <path 
            d="M50 140 L80 140 L80 120 Q80 110 90 110 L120 110 L120 80 Q120 70 130 70 L270 70 Q280 70 280 80 L280 110 L310 110 Q320 110 320 120 L320 140 L350 140 L350 150 Q350 160 340 160 L320 160 Q310 160 310 150 L310 145 L90 145 L90 150 Q90 160 80 160 L60 160 Q50 160 50 150 Z" 
            fill="none" 
            stroke="#8b5cf6" 
            strokeWidth="2" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <circle cx="100" cy="150" r="18" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="300" cy="150" r="18" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="3,3" />
          <line x1="160" y1="70" x2="160" y2="140" stroke="#8b5cf6" strokeWidth="1" strokeDasharray="2,2" />
          <line x1="220" y1="70" x2="220" y2="140" stroke="#8b5cf6" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    },
    'interior-front': {
      title: 'Interior - Front Seats',
      instruction: 'Capture front seats, dashboard, and steering wheel clearly',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="50" y="60" width="200" height="120" rx="10" fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          {/* Seats */}
          <rect x="70" y="100" width="40" height="60" rx="5" fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="3,3" />
          <rect x="190" y="100" width="40" height="60" rx="5" fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="3,3" />
          {/* Steering wheel */}
          <circle cx="90" cy="90" r="15" fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="3,3" />
          {/* Dashboard */}
          <line x1="60" y1="80" x2="240" y2="80" stroke="#f59e0b" strokeWidth="2" strokeDasharray="3,3" />
        </svg>
      )
    },
    'interior-rear': {
      title: 'Interior - Rear Seats',
      instruction: 'Capture rear seats and interior condition',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="50" y="60" width="200" height="120" rx="10" fill="none" stroke="#ec4899" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <rect x="80" y="100" width="140" height="60" rx="5" fill="none" stroke="#ec4899" strokeWidth="2" strokeDasharray="3,3" />
          <line x1="150" y1="100" x2="150" y2="160" stroke="#ec4899" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    },
    'dashboard': {
      title: 'Dashboard & Controls',
      instruction: 'Focus on dashboard, gauges, and control systems',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <path d="M50 120 Q50 100 70 100 L230 100 Q250 100 250 120 L250 160 L50 160 Z" fill="none" stroke="#06b6d4" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <circle cx="120" cy="130" r="20" fill="none" stroke="#06b6d4" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="180" cy="130" r="20" fill="none" stroke="#06b6d4" strokeWidth="2" strokeDasharray="3,3" />
          <rect x="140" y="110" width="20" height="10" fill="none" stroke="#06b6d4" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    },
    'odometer': {
      title: 'Odometer Reading',
      instruction: 'Clear, close-up shot of odometer display',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="100" y="80" width="100" height="40" rx="5" fill="none" stroke="#84cc16" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <text x="150" y="105" textAnchor="middle" className="text-sm fill-green-500 font-mono">123456</text>
          <rect x="80" y="70" width="140" height="60" rx="10" fill="none" stroke="#84cc16" strokeWidth="1" strokeDasharray="3,3" />
        </svg>
      )
    },
    'vin': {
      title: 'VIN Number',
      instruction: 'Clear shot of VIN plate or dashboard VIN',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="75" y="90" width="150" height="20" rx="3" fill="none" stroke="#f97316" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <text x="150" y="105" textAnchor="middle" className="text-xs fill-orange-500 font-mono">1HGBH41JXMN109186</text>
          <rect x="60" y="80" width="180" height="40" rx="5" fill="none" stroke="#f97316" strokeWidth="1" strokeDasharray="3,3" />
        </svg>
      )
    },
    'license-plate': {
      title: 'License Plate',
      instruction: 'Clear, straight-on shot of license plate',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="100" y="90" width="100" height="40" rx="5" fill="none" stroke="#dc2626" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <text x="150" y="110" textAnchor="middle" className="text-sm fill-red-600 font-bold">ABC 123</text>
          <rect x="90" y="80" width="120" height="60" rx="8" fill="none" stroke="#dc2626" strokeWidth="1" strokeDasharray="3,3" />
        </svg>
      )
    },
    'engine-bay': {
      title: 'Engine Bay',
      instruction: 'Full engine bay overview, include fluid checks',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="50" y="60" width="200" height="120" rx="10" fill="none" stroke="#7c3aed" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <rect x="80" y="90" width="60" height="40" rx="5" fill="none" stroke="#7c3aed" strokeWidth="2" strokeDasharray="3,3" />
          <rect x="160" y="90" width="60" height="40" rx="5" fill="none" stroke="#7c3aed" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="110" cy="150" r="10" fill="none" stroke="#7c3aed" strokeWidth="1" strokeDasharray="2,2" />
          <circle cx="190" cy="150" r="10" fill="none" stroke="#7c3aed" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    },
    'undercarriage': {
      title: 'Undercarriage',
      instruction: 'Underside view for leaks, rust, and structural damage',
      silhouette: (
        <svg viewBox="0 0 300 200" className="w-full h-full">
          <rect x="50" y="70" width="200" height="80" rx="8" fill="none" stroke="#059669" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <line x1="70" y1="90" x2="230" y2="90" stroke="#059669" strokeWidth="2" strokeDasharray="3,3" />
          <line x1="70" y1="110" x2="230" y2="110" stroke="#059669" strokeWidth="2" strokeDasharray="3,3" />
          <line x1="70" y1="130" x2="230" y2="130" stroke="#059669" strokeWidth="2" strokeDasharray="3,3" />
          <circle cx="90" cy="100" r="5" fill="none" stroke="#059669" strokeWidth="1" strokeDasharray="2,2" />
          <circle cx="210" cy="120" r="5" fill="none" stroke="#059669" strokeWidth="1" strokeDasharray="2,2" />
        </svg>
      )
    }
  }

  const data = guidanceData[photoType]

  return (
    <div className={`photo-guidance ${isActive ? 'active' : 'inactive'} transition-all duration-300`}>
      <div className="guidance-container bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg border-2 border-dashed border-blue-300">
        <div className="text-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">{data.title}</h3>
          <p className="text-sm text-gray-600">{data.instruction}</p>
        </div>
        
        <div className="silhouette-container h-40 w-full flex items-center justify-center bg-white/50 rounded-lg">
          {data.silhouette}
        </div>
        
        <div className="tips mt-4">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Position vehicle within dotted outline</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Ensure good lighting and clear focus</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PhotoGuidance