import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Mail, Lock } from 'lucide-react';
import { InputField } from './InputField';
import {
  signInWithGoogle,
  auth,
} from '../../services/firebase';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  updateProfile,
} from 'firebase/auth';

// ── helpers ──────────────────────────────────────────────────────────────────
const friendlyError = (code: string): string => {
  switch (code) {
    case 'auth/email-already-in-use': return 'This email is already registered. Try logging in.';
    case 'auth/invalid-email': return 'Please enter a valid email address.';
    case 'auth/weak-password': return 'Password must be at least 6 characters.';
    case 'auth/user-not-found': return 'No account found with this email.';
    case 'auth/wrong-password': return 'Incorrect password. Try again.';
    case 'auth/invalid-credential': return 'Invalid email or password.';
    case 'auth/too-many-requests': return 'Too many attempts. Please wait and try again.';
    case 'auth/network-request-failed': return 'Network error. Check your connection.';
    default: return 'Something went wrong. Please try again.';
  }
};
// ─────────────────────────────────────────────────────────────────────────────

export const AuthForm = () => {
  const [activeTab, setActiveTab] = useState<'signup' | 'login'>('signup');

  // Sign Up fields
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Log In fields
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resetSent, setResetSent] = useState(false);

  // ── Animation variants ────────────────────────────────────────────────────
  const formContainerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.06, delayChildren: 0.05 } },
  };
  const formItemVariants = {
    hidden: { opacity: 0, y: 18 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 120, damping: 16 } },
  };
  // ─────────────────────────────────────────────────────────────────────────

  const switchTab = (tab: 'signup' | 'login') => {
    setActiveTab(tab);
    setError('');
    setResetSent(false);
  };

  // ── Sign Up ───────────────────────────────────────────────────────────────
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!auth) {
      setError('Firebase is not configured. Add your VITE_FIREBASE_* keys to frontend/.env.');
      return;
    }
    if (signupPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (signupPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    try {
      const { user } = await createUserWithEmailAndPassword(auth, signupEmail, signupPassword);
      // Save display name
      if (firstName || lastName) {
        await updateProfile(user, { displayName: `${firstName} ${lastName}`.trim() });
      }
      // onAuthStateChanged in App.tsx will detect the new user and swap to Dashboard
    } catch (err: unknown) {
      const code = (err as { code?: string }).code ?? '';
      setError(friendlyError(code));
    } finally {
      setLoading(false);
    }
  };

  // ── Log In ────────────────────────────────────────────────────────────────
  const handleLogIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!auth) {
      setError('Firebase is not configured. Add your VITE_FIREBASE_* keys to frontend/.env.');
      return;
    }

    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, loginEmail, loginPassword);
      // onAuthStateChanged in App.tsx will detect the user and swap to Dashboard
    } catch (err: unknown) {
      const code = (err as { code?: string }).code ?? '';
      setError(friendlyError(code));
    } finally {
      setLoading(false);
    }
  };

  // ── Password Reset ────────────────────────────────────────────────────────
  const handleForgotPassword = async () => {
    setError('');
    if (!auth) {
      setError('Firebase is not configured.');
      return;
    }
    if (!loginEmail) {
      setError('Enter your email above first, then click Forgot Password.');
      return;
    }
    setLoading(true);
    try {
      await sendPasswordResetEmail(auth, loginEmail);
      setResetSent(true);
    } catch (err: unknown) {
      const code = (err as { code?: string }).code ?? '';
      setError(friendlyError(code));
    } finally {
      setLoading(false);
    }
  };

  // ── Google ────────────────────────────────────────────────────────────────
  const handleGoogle = async () => {
    setError('');
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (err: unknown) {
      const code = (err as { code?: string }).code ?? '';
      if (code !== 'auth/popup-closed-by-user') {
        setError(friendlyError(code));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[480px] p-8 sm:p-10 rounded-[30px] bg-cinematic-800/40 backdrop-blur-xl border border-white/5 shadow-2xl flex flex-col gap-8 text-center select-none">

      {/* 1. Pill Switch Tab Toggle */}
      <div className="flex p-1 bg-cinematic-950/70 rounded-full border border-white/5">
        <button
          onClick={() => switchTab('signup')}
          className="relative flex-1 py-2 text-[11px] font-sans font-bold tracking-[0.2em] uppercase rounded-full outline-none transition-colors duration-300"
          style={{ color: activeTab === 'signup' ? '#07070a' : '#9ca3af' }}
        >
          {activeTab === 'signup' && (
            <motion.div
              layoutId="activeTabPill"
              className="absolute inset-0 bg-gold rounded-full shadow-gold-glow"
              transition={{ type: 'spring', stiffness: 220, damping: 24 }}
            />
          )}
          <span className="relative z-10">Sign Up</span>
        </button>

        <button
          onClick={() => switchTab('login')}
          className="relative flex-1 py-2 text-[11px] font-sans font-bold tracking-[0.2em] uppercase rounded-full outline-none transition-colors duration-300"
          style={{ color: activeTab === 'login' ? '#07070a' : '#9ca3af' }}
        >
          {activeTab === 'login' && (
            <motion.div
              layoutId="activeTabPill"
              className="absolute inset-0 bg-gold rounded-full shadow-gold-glow"
              transition={{ type: 'spring', stiffness: 220, damping: 24 }}
            />
          )}
          <span className="relative z-10">Log In</span>
        </button>
      </div>

      {/* 2. Heading title */}
      <div className="flex flex-col gap-1.5 text-left">
        <h2 className="font-serif text-3xl font-bold tracking-wide text-white">
          {activeTab === 'signup' ? 'Create Your Account' : 'Welcome Back'}
        </h2>
        <p className="text-xs text-gray-400 font-sans tracking-wide">
          {activeTab === 'signup'
            ? 'Fill in the chronicles to register your passage.'
            : 'Enter your credentials to resume your journey.'}
        </p>
      </div>

      {/* 3. Error / Reset-sent banner */}
      <AnimatePresence>
        {(error || resetSent) && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className={`text-left px-4 py-3 rounded-xl text-xs font-sans tracking-wide border ${resetSent
                ? 'bg-green-900/30 border-green-500/30 text-green-300'
                : 'bg-red-900/30 border-red-500/30 text-red-300'
              }`}
          >
            {resetSent
              ? `Password reset email sent to ${loginEmail}. Check your inbox.`
              : error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 4. Form fields */}
      <form
        onSubmit={(e) => { e.preventDefault(); (activeTab === 'signup' ? handleSignUp : handleLogIn)(e); }}
        className="flex flex-col gap-5"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={formContainerVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            className="flex flex-col gap-4.5"
          >
            {activeTab === 'signup' ? (
              <>
                {/* First / Last name row */}
                <motion.div variants={formItemVariants} className="grid grid-cols-2 gap-3.5">
                  <InputField
                    label="First Name"
                    type="text"
                    id="firstName"
                    placeholder="firstName"
                    icon={<User className="w-4 h-4" />}
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    autoComplete="given-name"
                  />
                  <InputField
                    label="Last Name"
                    type="text"
                    id="lastName"
                    placeholder="lastName"
                    icon={<User className="w-4 h-4" />}
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    autoComplete="family-name"
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Email"
                    type="email"
                    id="signupEmail"
                    placeholder="you@gmail.com"
                    icon={<Mail className="w-4 h-4" />}
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    autoComplete="email"
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Password"
                    type="password"
                    id="signupPassword"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Confirm Password"
                    type="password"
                    id="confirmPassword"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                </motion.div>
              </>
            ) : (
              <>
                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Email"
                    type="email"
                    id="loginEmail"
                    placeholder="you@gmail.com"
                    icon={<Mail className="w-4 h-4" />}
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    autoComplete="email"
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Password"
                    type="password"
                    id="loginPassword"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    autoComplete="current-password"
                  />
                </motion.div>

                <motion.div variants={formItemVariants} className="flex justify-end mt-1">
                  <button
                    type="button"
                    onClick={handleForgotPassword}
                    disabled={loading}
                    className="text-[13px] font-sans font-medium text-[#D4AF37] hover:underline hover:brightness-110 cursor-pointer transition-all duration-200 ease-out outline-none disabled:opacity-50"
                  >
                    Forgot Password?
                  </button>
                </motion.div>
              </>
            )}

            {/* Submit button */}
            <motion.div variants={formItemVariants} className="mt-4">
              <motion.button
                type="submit"
                onClick={activeTab === 'signup' ? handleSignUp : handleLogIn}
                disabled={loading}
                whileHover={loading ? {} : { scale: 1.025, y: -2, boxShadow: '0 4px 20px rgba(212, 175, 55, 0.45)' }}
                whileTap={loading ? {} : { scale: 0.98 }}
                className="w-full py-3.5 bg-gold border border-gold hover:bg-gold-light hover:border-gold-light text-cinematic-950 font-serif text-xs font-bold tracking-[0.2em] uppercase rounded-xl transition-all duration-300 outline-none shadow-gold-glow disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading
                  ? 'Please wait…'
                  : activeTab === 'signup' ? 'Create Account' : 'Log In'}
              </motion.button>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </form>

      {/* 5. Divider */}
      <div className="flex items-center gap-3 w-full select-none opacity-50">
        <div className="h-[0.5px] flex-grow bg-gradient-to-r from-transparent to-white/20" />
        <span className="text-[9px] font-sans tracking-[0.25em] text-gray-500 uppercase">Or</span>
        <div className="h-[0.5px] flex-grow bg-gradient-to-l from-transparent to-white/20" />
      </div>

      {/* 6. Google Sign In */}
      <motion.button
        type="button"
        onClick={handleGoogle}
        disabled={loading}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        whileHover={loading ? {} : { scale: 1.01, y: -2, borderColor: '#D4AF37', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)' }}
        whileTap={loading ? {} : { scale: 0.98 }}
        className="w-full h-[60px] rounded-[16px] bg-[#FFFFFF] border border-[#D1D5DB] hover:border-gold px-6 flex items-center justify-center gap-3.5 transition-all duration-300 ease-out outline-none disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05" />
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335" />
        </svg>
        <span className="text-[#1F1F1F] text-sm font-semibold tracking-wide">
          Continue with Google
        </span>
      </motion.button>
    </div>
  );
};
