import { NextRequest, NextResponse } from "next/server";
import { firebaseAdmin } from '../../../lib/firebase-admin';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Admin Users API called - fetching users...');
    
    const users = await firebaseAdmin.getAllUsers();
    
    console.log(`✅ Successfully fetched ${users.length} users`);
    return NextResponse.json({
      users: users,
      success: true,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error in admin users API:', error);
    return NextResponse.json(
      { 
        users: [],
        success: false,
        error: 'Failed to fetch users',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}