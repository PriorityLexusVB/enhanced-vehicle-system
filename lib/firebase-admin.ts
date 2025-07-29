// Note: This is a simplified admin configuration
// For production, you would use Firebase Admin SDK
// For now, we'll use client-side Firebase with elevated permissions

import { auth, db } from './firebaseconfig';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc, collection, getDocs, deleteDoc, serverTimestamp, orderBy, query } from 'firebase/firestore';

export interface CreateUserData {
  email: string;
  password: string;
  role: 'sales' | 'manager' | 'admin';
}

export interface AppUser {
  uid: string;
  email: string;
  role: string;
  createdAt: string | null;
}

// Simulate admin operations using client SDK
export const adminOperations = {
  async createUser(userData: CreateUserData) {
    // Create user with Firebase Auth
    const userCredential = await createUserWithEmailAndPassword(auth, userData.email, userData.password);
    
    // Create user document in Firestore
    await setDoc(doc(db, 'users', userCredential.user.uid), {
      email: userData.email,
      role: userData.role,
      createdAt: serverTimestamp(),
    });

    return {
      uid: userCredential.user.uid,
      email: userData.email,
      role: userData.role,
    };
  },

  async getAllUsers(): Promise<AppUser[]> {
    const q = query(collection(db, 'users'), orderBy('createdAt', 'desc'));
    const querySnapshot = await getDocs(q);
    
    return querySnapshot.docs.map(doc => ({
      uid: doc.id,
      ...doc.data(),
      createdAt: doc.data().createdAt?.toDate?.()?.toISOString() || null,
    } as AppUser));
  },

  async deleteUser(uid: string) {
    // Note: This only deletes from Firestore
    // In production, you'd also delete from Firebase Auth using Admin SDK
    await deleteDoc(doc(db, 'users', uid));
    return { success: true };
  }
};