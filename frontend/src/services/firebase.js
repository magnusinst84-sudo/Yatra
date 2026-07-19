import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

// Each Firebase field is its own VITE_ env var — paste the values directly from
// Firebase Console → Project Settings → Your Apps → Web app → firebaseConfig.
//
// frontend/.env should look like:
//   VITE_FIREBASE_API_KEY=AIzaSy...
//   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
//   VITE_FIREBASE_PROJECT_ID=your-project
//   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
//   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
//   VITE_FIREBASE_APP_ID=1:123456789:web:abc123

const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket:     import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
};

// Only initialize if the API key is present
const hasConfig = !!firebaseConfig.apiKey;

if (!hasConfig) {
  console.warn(
    '[YATRA] Firebase is not configured.\n' +
    'Add the following to frontend/.env and restart the dev server:\n' +
    '  VITE_FIREBASE_API_KEY=...\n' +
    '  VITE_FIREBASE_AUTH_DOMAIN=...\n' +
    '  VITE_FIREBASE_PROJECT_ID=...\n' +
    '  VITE_FIREBASE_STORAGE_BUCKET=...\n' +
    '  VITE_FIREBASE_MESSAGING_SENDER_ID=...\n' +
    '  VITE_FIREBASE_APP_ID=...'
  );
}

const app             = hasConfig ? initializeApp(firebaseConfig) : null;
export const auth     = hasConfig ? getAuth(app) : null;
export const googleProvider = hasConfig ? new GoogleAuthProvider() : null;

/**
 * Sign in using Google OAuth Popup.
 */
export const signInWithGoogle = async () => {
  if (!auth || !googleProvider) {
    throw new Error('[YATRA] Firebase not configured — add VITE_FIREBASE_* vars to frontend/.env');
  }
  const result = await signInWithPopup(auth, googleProvider);
  return result.user;
};

/**
 * Log out the current user.
 */
export const logoutUser = async () => {
  if (!auth) return;
  await signOut(auth);
};
