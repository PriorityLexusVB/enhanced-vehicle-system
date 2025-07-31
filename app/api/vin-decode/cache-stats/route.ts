import { NextRequest, NextResponse } from 'next/server';

// Access the same cache from the VIN decode endpoint
// In a production app, you'd import this from a shared module
declare global {
  var vinCache: Map<string, any> | undefined;
}

export async function GET(request: NextRequest) {
  try {
    // Get cache stats from the VIN decode module
    const cacheSize = global.vinCache?.size || 0;
    const now = Date.now();
    let expired = 0;
    let active = 0;
    
    if (global.vinCache) {
      for (const [key, entry] of global.vinCache.entries()) {
        if (entry.expiresAt < now) {
          expired++;
        } else {
          active++;
        }
      }
    }
    
    return NextResponse.json({
      success: true,
      cache: {
        totalEntries: cacheSize,
        activeEntries: active,
        expiredEntries: expired,
        hitRate: '📊 Track via logs',
        ttl: '7 days',
        maxSize: 1000,
        status: cacheSize > 0 ? 'active' : 'empty'
      },
      message: 'VIN caching system operational'
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to get cache stats',
      cache: {
        status: 'unknown'
      }
    });
  }
}