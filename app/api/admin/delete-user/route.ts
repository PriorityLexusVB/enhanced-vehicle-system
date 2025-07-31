import { NextRequest, NextResponse } from "next/server";
import { firebaseAdmin } from '../../../../lib/firebase-admin';

export async function DELETE(request: NextRequest) {
  try {
    console.log('🔍 Admin Delete User API called...');
    
    const { uid } = await request.json();

    if (!uid) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required field: uid' 
        },
        { status: 400 }
      );
    }

    console.log(`🗑️ Deleting user: ${uid}`);
    const result = await firebaseAdmin.deleteUser(uid);

    console.log('✅ User deleted successfully');
    return NextResponse.json({
      success: true,
      result: result,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error in admin delete user API:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to delete user',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}