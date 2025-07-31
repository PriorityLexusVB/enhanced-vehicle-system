import { NextRequest, NextResponse } from "next/server";
import { firebaseAdmin } from '../../../lib/firebase-admin';

export async function POST(request: NextRequest) {
  try {
    console.log('🔍 Admin Add User API called...');
    
    const { email, password, role } = await request.json();

    if (!email || !password || !role) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required fields: email, password, role' 
        },
        { status: 400 }
      );
    }

    console.log(`📧 Creating user: ${email} with role: ${role}`);
    const result = await firebaseAdmin.createUser(email, password, role);

    console.log('✅ User created successfully');
    return NextResponse.json({
      success: true,
      user: result,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error in admin add user API:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to create user',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}