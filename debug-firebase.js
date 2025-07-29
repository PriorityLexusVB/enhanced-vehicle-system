// Debug script to test Firebase connection and Firestore access
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, getDoc, connectFirestoreEmulator } = require('firebase/firestore');

const firebaseConfig = {
  apiKey: "AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8",
  authDomain: "priority-appraisal-ai-tool.firebaseapp.com",
  projectId: "priority-appraisal-ai-tool",
  storageBucket: "priority-appraisal-ai-tool.appspot.com",
  messagingSenderId: "155312316711",
  appId: "1:155312316711:web:5728ed9367b192cc968902"
};

async function debugFirebase() {
  try {
    console.log("🔧 Initializing Firebase...");
    const app = initializeApp(firebaseConfig);
    const db = getFirestore(app);
    
    console.log("✅ Firebase initialized successfully");
    console.log("🏪 Project ID:", firebaseConfig.projectId);
    
    // Try to read from users collection (this will likely fail due to security rules)
    console.log("\n🔍 Testing Firestore access...");
    
    // Test with a known user ID (replace with the actual user ID from your admin document)
    const testUserId = "17mmiuZDbtwsXUmjM9Ju"; // Replace with actual user ID
    const userDocRef = doc(db, 'users', testUserId);
    
    try {
      const userDoc = await getDoc(userDocRef);
      if (userDoc.exists()) {
        console.log("✅ Successfully read user document:", userDoc.data());
      } else {
        console.log("⚠️  User document does not exist");
      }
    } catch (firestoreError) {
      console.log("❌ Firestore access error:", firestoreError.message);
      console.log("🔒 This is likely due to Firebase Security Rules blocking access");
      
      if (firestoreError.message.includes('Missing or insufficient permissions')) {
        console.log("\n🛠️  SOLUTION NEEDED:");
        console.log("1. Go to Firebase Console > Firestore Database > Rules");
        console.log("2. Temporarily set rules to allow read/write for testing:");
        console.log(`
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}`);
        console.log("3. Or for immediate testing (INSECURE - only for testing):");
        console.log(`
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}`);
      }
    }
    
  } catch (error) {
    console.error("❌ Firebase initialization error:", error);
  }
}

debugFirebase();