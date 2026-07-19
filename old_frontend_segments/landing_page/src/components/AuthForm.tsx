import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Mail, Lock } from 'lucide-react';
import { InputField } from './InputField';

export const AuthForm = () => {
  const [activeTab, setActiveTab] = useState<'signup' | 'login'>('signup');

  // Animation variants for form container & stagger
  const formContainerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.06,
        delayChildren: 0.05,
      },
    },
  };

  const formItemVariants = {
    hidden: { opacity: 0, y: 18 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 120,
        damping: 16,
      },
    },
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className="w-full max-w-[480px] p-8 sm:p-10 rounded-[30px] bg-cinematic-800/40 backdrop-blur-xl border border-white/5 shadow-2xl flex flex-col gap-8 text-center select-none">

      {/* 1. Pill Switch Tab Toggle */}
      <div className="flex p-1 bg-cinematic-950/70 rounded-full border border-white/5">
        <button
          onClick={() => setActiveTab('signup')}
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
          onClick={() => setActiveTab('login')}
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

      {/* 3. Form fields with staggered Framer Motion reveal */}
      <form onSubmit={handleFormSubmit} className="flex flex-col gap-5">
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
                {/* Two-column Row for First/Last name */}
                <motion.div variants={formItemVariants} className="grid grid-cols-2 gap-3.5">
                  <InputField
                    label="First Name"
                    type="text"
                    id="firstName"
                    placeholder="Saksham"
                    icon={<User className="w-4 h-4" />}
                  />
                  <InputField
                    label="Last Name"
                    type="text"
                    id="lastName"
                    placeholder="Mittal"
                    icon={<User className="w-4 h-4" />}
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Email"
                    type="email"
                    id="email"
                    placeholder="sakshammittal0029@gmail.com"
                    icon={<Mail className="w-4 h-4" />}
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Password"
                    type="password"
                    id="password"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Confirm Password"
                    type="password"
                    id="confirmPassword"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
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
                    placeholder="sakshammittal0029@gmail.com"
                    icon={<Mail className="w-4 h-4" />}
                  />
                </motion.div>

                <motion.div variants={formItemVariants}>
                  <InputField
                    label="Password"
                    type="password"
                    id="loginPassword"
                    placeholder="••••••••"
                    icon={<Lock className="w-4 h-4" />}
                  />
                </motion.div>

                <motion.div variants={formItemVariants} className="flex justify-end mt-3">
                  <button
                    type="button"
                    onClick={() => console.log('Forgot password clicked')}
                    className="text-[14px] font-sans font-medium text-[#D4AF37] hover:underline hover:brightness-110 cursor-pointer transition-all duration-200 ease-out outline-none"
                  >
                    Forgot Password?
                  </button>
                </motion.div>
              </>
            )}

            {/* 4. Primary Button */}
            <motion.div variants={formItemVariants} className="mt-4">
              <motion.button
                type="submit"
                whileHover={{
                  scale: 1.025,
                  y: -2,
                  boxShadow: '0 4px 20px rgba(212, 175, 55, 0.45)'
                }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3.5 bg-gold border border-gold hover:bg-gold-light hover:border-gold-light text-cinematic-950 font-serif text-xs font-bold tracking-[0.2em] uppercase rounded-xl transition-all duration-300 outline-none shadow-gold-glow"
              >
                {activeTab === 'signup' ? 'Create Account' : 'Log In'}
              </motion.button>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </form>

      {/* 5. Horizontal divider */}
      <div className="flex items-center gap-3 w-full select-none opacity-50">
        <div className="h-[0.5px] flex-grow bg-gradient-to-r from-transparent to-white/20" />
        <span className="text-[9px] font-sans tracking-[0.25em] text-gray-500 uppercase">Or</span>
        <div className="h-[0.5px] flex-grow bg-gradient-to-l from-transparent to-white/20" />
      </div>

      {/* 6. Google Sign In Button */}
      <motion.button
        type="button"
        onClick={() => console.log('Google login clicked')}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        whileHover={{
          scale: 1.01,
          y: -2,
          borderColor: '#D4AF37',
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)',
        }}
        whileTap={{ scale: 0.98 }}
        className="w-full h-[60px] rounded-[16px] bg-[#FFFFFF] border border-[#D1D5DB] hover:border-gold px-6 flex items-center justify-center gap-3.5 transition-all duration-300 ease-out outline-none"
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
