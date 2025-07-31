// Firebase Admin SDK configuration for server-side operations
import * as admin from 'firebase-admin'

// Initialize Firebase Admin SDK if not already initialized
if (!admin.apps.length) {
  try {
    const serviceAccount = {
      projectId: process.env.FIREBASE_PROJECT_ID || process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    }

    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      projectId: serviceAccount.projectId,
    })
    
    console.log('✅ Firebase Admin SDK initialized successfully')
  } catch (error) {
    console.error('❌ Firebase Admin SDK initialization error:', error)
  }
}

interface AppUser {
  uid: string
  email: string
  role: string
  createdAt: string
}

export const firebaseAdmin = {
  async getAllUsers(): Promise<AppUser[]> {
    try {
      console.log('🔍 Fetching users using Firebase Admin SDK...')
      
      if (!admin.apps.length) {
        console.error('❌ Firebase Admin SDK not initialized')
        return []
      }

      // Method 1: Try to get users from Firestore using Admin SDK
      try {
        const firestore = admin.firestore()
        const usersSnapshot = await firestore.collection('users').orderBy('createdAt', 'desc').get()
        
        if (!usersSnapshot.empty) {
          const users = usersSnapshot.docs.map(doc => ({
            uid: doc.id,
            ...doc.data(),
            createdAt: doc.data().createdAt?.toDate?.()?.toISOString() || new Date().toISOString(),
          } as AppUser))
          
          console.log(`✅ Found ${users.length} users in Firestore using Admin SDK`)
          console.log('📧 User emails:', users.map(u => u.email))
          return users
        }
      } catch (firestoreError) {
        console.log('⚠️ Firestore query failed, trying Firebase Auth method:', firestoreError)
      }

      // Method 2: Fallback to Firebase Auth listUsers (if Firestore fails)
      try {
        const auth = admin.auth()
        const listUsersResult = await auth.listUsers(1000) // Get up to 1000 users
        
        const users = listUsersResult.users.map(userRecord => ({
          uid: userRecord.uid,
          email: userRecord.email || 'no-email',
          role: 'unknown', // Role not available from Auth, would need Firestore
          createdAt: userRecord.metadata.creationTime || new Date().toISOString(),
        } as AppUser))
        
        console.log(`✅ Found ${users.length} users in Firebase Auth`)
        console.log('📧 User emails:', users.map(u => u.email))
        return users
      } catch (authError) {
        console.error('❌ Firebase Auth listUsers failed:', authError)
      }

      console.log('❌ All methods failed - returning empty array')
      return []

    } catch (error) {
      console.error('❌ Critical error in getAllUsers:', error)
      return []
    }
  },

  async createUser(email: string, password: string, role: string) {
    try {
      console.log(`🔍 Creating user: ${email} with role: ${role}`)
      
      if (!admin.apps.length) {
        throw new Error('Firebase Admin SDK not initialized')
      }

      // Create user in Firebase Auth
      const auth = admin.auth()
      const userRecord = await auth.createUser({
        email,
        password,
        emailVerified: false,
      })
      
      console.log('✅ User created in Firebase Auth:', userRecord.uid)

      // Create user document in Firestore
      const firestore = admin.firestore()
      const userData = {
        email,
        role,
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        uid: userRecord.uid
      }

      await firestore.collection('users').doc(userRecord.uid).set(userData)
      console.log('✅ User document created in Firestore')

      return {
        success: true,
        uid: userRecord.uid,
        message: 'User created successfully'
      }
    } catch (error) {
      console.error('❌ Error creating user:', error)
      throw error
    }
  },

  async deleteUser(uid: string) {
    try {
      console.log(`🔍 Deleting user: ${uid}`)
      
      if (!admin.apps.length) {
        throw new Error('Firebase Admin SDK not initialized')
      }

      // Delete from Firebase Auth
      const auth = admin.auth()
      await auth.deleteUser(uid)
      console.log('✅ User deleted from Firebase Auth')

      // Delete from Firestore
      const firestore = admin.firestore()
      await firestore.collection('users').doc(uid).delete()
      console.log('✅ User document deleted from Firestore')

      return { success: true, message: 'User deleted successfully' }
    } catch (error) {
      console.error('❌ Error deleting user:', error)
      throw error
    }
  }
}