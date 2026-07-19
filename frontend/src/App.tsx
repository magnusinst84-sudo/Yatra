import { useState, useEffect, createContext } from 'react';
import type { User } from 'firebase/auth';
import { LandingPage } from './landing/components/LandingPage';
import Dashboard from './Dashboard';
import { auth } from './services/firebase';
import './landing/index.css';
import './index.css';

// ── Auth Context ──────────────────────────────────────────────────────────────
interface AuthContextType {
  user: User | null;
  idToken: string | null;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  idToken: null,
});
// ─────────────────────────────────────────────────────────────────────────────

function App() {
  const [user, setUser]       = useState<User | null>(null);
  const [idToken, setIdToken] = useState<string | null>(null);

  useEffect(() => {
    // auth is null when VITE_FIREBASE_* vars are missing — stay on landing page
    if (!auth) return;

    const unsub = auth.onAuthStateChanged(async (firebaseUser) => {
      setUser(firebaseUser ?? null);
      if (firebaseUser) {
        const token = await firebaseUser.getIdToken();
        setIdToken(token);
      } else {
        setIdToken(null);
      }
    });

    return () => unsub();
  }, []);

  return (
    <AuthContext.Provider value={{ user, idToken }}>
      <div className="w-full min-h-screen landing-wrapper">
        {user ? <Dashboard /> : <LandingPage />}
      </div>
    </AuthContext.Provider>
  );
}

export default App;
