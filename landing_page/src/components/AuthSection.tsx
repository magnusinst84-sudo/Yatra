import { motion } from 'framer-motion';
import { AuthImagePanel } from './AuthImagePanel';
import { AuthForm } from './AuthForm';

export const AuthSection = () => {
  return (
    <motion.section
      id="auth-section"
      initial={{ opacity: 0, y: 60 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.18 }}
      transition={{ type: 'spring' as const, stiffness: 50, damping: 15, duration: 1.1 }}
      className="relative min-h-screen w-full flex items-center justify-center bg-[#090909] snap-start z-10 overflow-y-auto py-12 lg:py-16"
    >
      {/* Decorative Gold Radial Light Source in Background */}
      <div 
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none opacity-[0.03] rounded-full blur-[120px]"
        style={{ background: 'radial-gradient(circle, #D4AF37 0%, transparent 70%)' }}
      />

      {/* Main Responsive Layout Wrapper */}
      <div className="w-full max-w-[1400px] mx-auto px-6 sm:px-12 lg:px-16 flex flex-col lg:grid lg:grid-cols-[45fr_55fr] gap-10 lg:gap-[50px] items-center justify-center">
        
        {/* Left Side: Dynamic Image Panel Placeholder */}
        <div className="w-full flex items-center justify-center lg:h-[580px]">
          <AuthImagePanel />
        </div>

        {/* Right Side: Glassmorphism Authentication Form */}
        <div className="w-full flex items-center justify-center">
          <AuthForm />
        </div>
      </div>
    </motion.section>
  );
};
