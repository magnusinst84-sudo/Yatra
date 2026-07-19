import { useState, useEffect, createContext } from 'react';
import type { User } from 'firebase/auth';
import { LandingPage } from './landing/components/LandingPage';
import Dashboard from './Dashboard';
import WalkthroughModal from './components/WalkthroughModal';
import { auth } from './services/firebase';
import { getSharedWalkthrough } from './services/api';
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
  const [sharedWalkthrough, setSharedWalkthrough] = useState<any>(null);

  useEffect(() => {
    // Check for shared link in URL (e.g., /shared/aB3x9Q21)
    const path = window.location.pathname;
    if (path.startsWith('/shared/')) {
      const slug = path.split('/')[2];
      if (slug) {
        getSharedWalkthrough(slug)
          .then(setSharedWalkthrough)
          .catch(err => console.error('Shared link failed:', err));
      }
    }

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

  const handleCloseShared = () => {
    setSharedWalkthrough(null);
    window.history.replaceState({}, '', '/');
  };

  return (
    <AuthContext.Provider value={{ user, idToken }}>
      <div className="w-full min-h-screen landing-wrapper relative">
        {user ? <Dashboard /> : <LandingPage />}
        
        {/* Render shared walkthrough directly on top if opened via link */}
        {sharedWalkthrough && (
           <WalkthroughModal 
              walkthrough={sharedWalkthrough} 
              onClose={handleCloseShared} 
           />
        )}
      </div>
    </AuthContext.Provider>
  );
}

export default App;
