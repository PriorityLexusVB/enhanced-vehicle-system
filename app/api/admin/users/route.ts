import { NextRequest, NextResponse } from 'next/server';
import { adminOperations } from '@/lib/firebase-admin';

export async function GET(request: NextRequest) {
  try {
    // Get all users using our admin operations
    const users = await adminOperations.getAllUsers();

    return NextResponse.json({ users });
  } catch (error: any) {
    console.error('Error fetching users:', error);
    return NextResponse.json(
      { error: 'Failed to fetch users' },
      { status: 500 }
    );
  }
}