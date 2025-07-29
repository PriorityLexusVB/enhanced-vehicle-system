import { User } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebaseconfig';

export interface UserRole {
  email: string;
  role: 'sales' | 'manager' | 'admin';
  createdAt: any;
}

export async function getUserRole(user: User): Promise<UserRole | null> {
  try {
    const userDocRef = doc(db, 'users', user.uid);
    const userDoc = await getDoc(userDocRef);
    
    if (userDoc.exists()) {
      return userDoc.data() as UserRole;
    }
    return null;
  } catch (error) {
    console.error('Error fetching user role:', error);
    return null;
  }
}

export function isAdmin(userRole: UserRole | null): boolean {
  return userRole?.role === 'admin';
}