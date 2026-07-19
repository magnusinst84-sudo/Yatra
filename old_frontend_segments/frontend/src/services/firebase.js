import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

// Vite exposes env variables through import.meta.env
// We first try to parse the VITE_FIREBASE_CONFIG as JSON.
// If it fails or isn't set, we fall back to manual object parsing or throw an error.

let firebaseConfig = {};
const configString = import.meta.env.VITE_FIREBASE_CONFIG;

if (configString) {
  try {
    // If properly formatted JSON in .env:
    firebaseConfig = JSON.parse(configString);
  } catch (e) {
    console.warn("VITE_FIREBASE_CONFIG could not be parsed as JSON. It may be improperly formatted in .env.");
    
    // Quick fallback to try and extract values if it's a JS object string (like in .env currently)
    // Note: It's heavily recommended to store valid JSON in the .env file!
    try {
      const extract = (key) => {
        const match = configString.match(new RegExp(`${key}:\\s*"([^"]+)"`));
        return match ? match[1] : undefined;
      };
      
      firebaseConfig = {
        apiKey: extract("apiKey"),
        authDomain: extract("authDomain"),
        projectId: extract("projectId"),
        storageBucket: extract("storageBucket"),
        messagingSenderId: extract("messagingSenderId"),
        appId: extract("appId")
      };
      console.log("Successfully extracted Firebase config manually.");
    } catch (err) {
      console.error("Failed to extract Firebase config.", err);
    }
  }
} else {
  console.warn("VITE_FIREBASE_CONFIG environment variable is not set.");
}

// Initialize Firebase App
const app = initializeApp(firebaseConfig);

// Export Auth instance and Provider
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

/**
 * Sign in using Google OAuth Popup
 */
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  } catch (error) {
    console.error("Error signing in with Google:", error);
    throw error;
  }
};

/**
 * Log out the current user
 */
export const logoutUser = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("Error signing out:", error);
    throw error;
  }
};
