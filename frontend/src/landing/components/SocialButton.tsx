import React from 'react';
import { motion } from 'framer-motion';

interface SocialButtonProps {
  provider: 'google' | 'facebook' | 'apple';
  onClick?: () => void;
}

export const SocialButton: React.FC<SocialButtonProps> = ({ provider, onClick }) => {
  // Luxury inline SVG paths matching theme aesthetics
  const getProviderIcon = () => {
    switch (provider) {
      case 'google':
        return (
          <svg className="w-5 h-5 text-gold-light" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.24 10.285V13.4h6.887c-.275 1.565-1.88 4.604-6.887 4.604-4.33 0-7.859-3.578-7.859-8s3.53-8 7.859-8c2.46 0 4.105 1.025 5.047 1.926l2.427-2.334C18.155 1.802 15.428 1 12.24 1 6.01 1 1 6.01 1 12.24s5.01 11.24 11.24 11.24c6.51 0 10.823-4.572 10.823-11.023 0-.742-.08-1.302-.177-1.86H12.24z"/>
          </svg>
        );
      case 'facebook':
        return (
          <svg className="w-5 h-5 text-gold-light" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c4.56-.93 8-4.96 8-9.75z"/>
          </svg>
        );
      case 'apple':
        return (
          <svg className="w-5 h-5 text-gold-light" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C4.79 17.2 3.65 11.66 6.3 7.02c1.31-2.28 3.59-3.5 5.86-3.32 1.8.15 3.1 1.08 4.08 1.08s2.51-1.05 4.7-.8c2.28.26 3.99 1.25 4.9 2.87-4.48 2.62-3.3 8.39.92 10.12-1.04 2.5-2.43 4.99-4.8 7.37l.09-.09zM12.03 3.52c-.1-.01-.2-.02-.3-.02 0-2.22 1.83-4.01 4.09-4 0 .1.01.2.01.3-.12 2.14-1.92 3.73-3.8 3.72z"/>
          </svg>
        );
    }
  };

  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{ 
        scale: 1.08, 
        backgroundColor: 'rgba(212, 175, 55, 0.08)',
        borderColor: 'rgba(212, 175, 55, 0.45)',
        boxShadow: '0 0 15px rgba(212, 175, 55, 0.15)'
      }}
      whileTap={{ scale: 0.96 }}
      className="flex-1 py-3.5 px-4 bg-cinematic-900/40 backdrop-blur-md border border-white/5 rounded-xl flex items-center justify-center transition-all duration-300 outline-none"
    >
      {getProviderIcon()}
    </motion.button>
  );
};
