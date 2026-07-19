import { useState } from 'react';
import { motion } from 'framer-motion';
import { destinations } from '../data/destinations';
import { CardCarousel } from './CardCarousel';
import { ScrollIndicator } from './ScrollIndicator';
import { AuthSection } from './AuthSection';

export const LandingPage = () => {
  const [activeIndex, setActiveIndex] = useState(2); // Start with Varanasi (center card) as active

  return (
    /* Root scroll-snapping container */
    <div className="relative h-screen w-full overflow-y-scroll snap-y snap-mandatory scroll-smooth bg-cinematic-950 font-sans text-gray-200">
      
      {/* SECTION 1: Carousel Showcase (Home) */}
      <section className="relative w-full h-screen flex flex-col justify-center items-center overflow-hidden snap-start">
        
        {/* Brand Name Header */}
        <motion.div
          initial={{ opacity: 0, y: -25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.0, ease: 'easeOut' }}
          className="absolute top-10 left-0 right-0 flex flex-col items-center justify-center text-center z-20 pointer-events-none select-none px-6"
        >
          {/* Logo Title (Responsive text size, custom gold gradient & text-glow) */}
          <h1 
            className="font-serif font-bold uppercase tracking-[12px] pl-[12px] leading-none text-[36px] sm:text-[48px] lg:text-[60px]"
            style={{
              backgroundImage: 'linear-gradient(90deg, #F8E7A1, #D4AF37)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
              textShadow: '0 0 12px rgba(212, 175, 55, 0.18)',
            }}
          >
            YATRA
          </h1>
          {/* Tagline */}
          <p className="text-white/75 text-xs sm:text-base font-sans font-medium uppercase tracking-[6px] pl-[6px] mt-3">
            Journey Through Time
          </p>
        </motion.div>

        {/* Cinematic Background Fader Layers */}
        {destinations.map((dest, idx) => (
          <div
            key={`bg-${dest.id}`}
            className="absolute inset-0 transition-opacity duration-1000 ease-in-out pointer-events-none"
            style={{
              background: dest.gradient,
              opacity: idx === activeIndex ? 1 : 0,
              zIndex: 0,
            }}
          >
            {dest.image && (
              <img
                src={dest.image}
                alt={dest.name}
                className="w-full h-full object-cover opacity-35 mix-blend-luminosity animate-pulse-slow"
              />
            )}
          </div>
        ))}

        {/* Dark Vignette overlay for depth */}
        <div 
          className="absolute inset-0 pointer-events-none z-[1]"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(7, 7, 10, 0.1) 0%, rgba(7, 7, 10, 0.75) 70%, rgba(7, 7, 10, 0.95) 100%)'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-cinematic-950/40 via-transparent to-cinematic-950/90 pointer-events-none z-[1]" />

        {/* Carousel Showcase */}
        <div className="relative w-full z-10 flex items-center justify-center overflow-visible p-6 sm:p-12 lg:p-16">
          <div className="w-full max-w-[1400px] flex items-center justify-center overflow-visible">
            <CardCarousel
              destinations={destinations}
              activeIndex={activeIndex}
              setActiveIndex={setActiveIndex}
            />
          </div>
        </div>

        {/* Floating Scroll Indicator */}
        <ScrollIndicator />
      </section>

      {/* SECTION 2: Fullscreen Authentication Page */}
      <AuthSection />
    </div>
  );
};
