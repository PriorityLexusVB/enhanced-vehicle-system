import { NextRequest, NextResponse } from 'next/server';
import { firebaseAdmin } from '@/lib/firebase-admin';

export async function POST(request: NextRequest) {
  try {
    const { email, password, role } = await request.json();

    // Validate input
    if (!email || !password || !role) {
      return NextResponse.json(
        { error: 'Email, password, and role are required' },
        { status: 400 }
      );
    }

    if (!['sales', 'manager', 'admin'].includes(role)) {
      return NextResponse.json(
        { error: 'Invalid role. Must be sales, manager, or admin' },
        { status: 400 }
      );
    }

    // Create user using our admin operations
    const result = await firebaseAdmin.createUser(email, password, role);

    return NextResponse.json({
      success: true,
      ...result,
    });
  } catch (error: any) {
    console.error('Error creating user:', error);
    
    // Handle specific Firebase errors
    if (error.code === 'auth/email-already-in-use') {
      return NextResponse.json(
        { error: 'A user with this email already exists' },
        { status: 400 }
      );
    }
    
    if (error.code === 'auth/invalid-email') {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }
    
    if (error.code === 'auth/weak-password') {
      return NextResponse.json(
        { error: 'Password should be at least 6 characters' },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    );
  }
}