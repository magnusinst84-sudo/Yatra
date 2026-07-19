import { motion } from 'framer-motion';
import { ArrowDown } from 'lucide-react';

export const ScrollIndicator = () => {
  const handleScroll = () => {
    const authElement = document.getElementById('auth-section');
    if (authElement) {
      authElement.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-2.5 z-20 cursor-pointer select-none">
      {/* Small Text Indicator */}
      <span className="text-[10px] font-sans font-medium tracking-[0.25em] text-gold/80 uppercase">
        Scroll to Continue
      </span>

      {/* Animated Circular Button */}
      <motion.button
        onClick={handleScroll}
        whileHover={{ scale: 1.12, boxShadow: '0 0 25px rgba(212, 175, 55, 0.55)' }}
        whileTap={{ scale: 0.95 }}
        animate={{
          y: [0, 8, 0],
        }}
        transition={{
          y: {
            duration: 2.2,
            repeat: Infinity,
            ease: "easeInOut"
          }
        }}
        className="w-11 h-11 rounded-full flex items-center justify-center border border-gold/50 bg-gold/15 text-gold shadow-gold-glow hover:border-gold hover:text-white transition-colors duration-300 backdrop-blur-md"
      >
        <ArrowDown className="w-5 h-5" />
      </motion.button>
    </div>
  );
};
