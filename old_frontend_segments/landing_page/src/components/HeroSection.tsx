import { useState, useEffect } from 'react';
import { Compass, BookOpen, ChevronRight } from 'lucide-react';
import type { Destination } from '../data/destinations';

interface HeroSectionProps {
  destination: Destination;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ destination }) => {
  const [animate, setAnimate] = useState(true);

  // Trigger text transition when destination changes
  useEffect(() => {
    setAnimate(false);
    const timer = setTimeout(() => {
      setAnimate(true);
    }, 150); // Small offset to sync with the background/card shift
    return () => clearTimeout(timer);
  }, [destination]);

  return (
    <div 
      className={`w-full max-w-xl flex flex-col justify-center gap-6 text-left transition-all duration-800 transform
        ${animate ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`}
    >
      {/* Small Category Label */}
      <div className="flex items-center gap-2">
        <Compass className="w-4.5 h-4.5 text-gold animate-spin-slow" />
        <span className="text-[11px] font-semibold tracking-[0.3em] text-gold uppercase">
          Chronicle of Bharat
        </span>
        <div className="h-[0.5px] w-12 bg-gold/30" />
      </div>

      {/* Title */}
      <div className="relative">
        <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl font-black text-white tracking-wide leading-none select-none">
          {destination.name}
        </h1>
        {/* Subtle accent border under title */}
        <div className="absolute -bottom-2 left-0 w-24 h-[1px] bg-gradient-to-r from-gold via-gold/50 to-transparent" />
      </div>

      {/* Era & Location Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 mt-2 text-xs tracking-widest text-gold-light/90 font-medium">
        <div className="flex items-center gap-2">
          <span className="uppercase">{destination.era}</span>
        </div>
        <span className="hidden sm:inline text-gold/30">|</span>
        <div className="uppercase">
          <span>{destination.location}</span>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-300 font-sans text-sm sm:text-base leading-relaxed tracking-wide font-light max-w-lg mt-2 drop-shadow-sm">
        {destination.description}
      </p>

      {/* Interactive Call to Action */}
      <div className="flex items-center gap-4 mt-4">
        <button className="group relative flex items-center gap-2.5 px-6 py-3 rounded-full bg-gold/10 hover:bg-gold/20 border border-gold/40 hover:border-gold text-white font-serif text-sm tracking-widest uppercase transition-all duration-300 shadow-gold-glow hover:shadow-gold-glow-strong">
          <BookOpen className="w-4 h-4 text-gold group-hover:scale-110 transition-transform" />
          <span>Explore Archives</span>
          <ChevronRight className="w-4 h-4 text-gold transform group-hover:translate-x-1 transition-transform" />
        </button>
        
        <button className="px-5 py-3 rounded-full border border-white/10 hover:border-white/20 text-gray-400 hover:text-white text-xs tracking-widest uppercase transition-all duration-300 bg-white/5 hover:bg-white/10 backdrop-blur-md">
          View Map
        </button>
      </div>
    </div>
  );
};
