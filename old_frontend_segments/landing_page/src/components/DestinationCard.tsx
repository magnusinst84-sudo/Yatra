import { forwardRef, useImperativeHandle, useRef, memo } from 'react';
import { MapPin, Compass } from 'lucide-react';
import type { Destination } from '../data/destinations';
import { useSpring } from '../hooks/useSpring';

interface DestinationCardProps {
  destination: Destination;
  isActive: boolean;
  onClick: () => void;
}

export interface DestinationCardRef {
  setTilt: (x: number, y: number) => void;
  setScale: (s: number) => void;
  getElement: () => HTMLDivElement | null;
}

export const DestinationCard = memo(
  forwardRef<DestinationCardRef, DestinationCardProps>(
    ({ destination, isActive, onClick }, ref) => {
      // Spring physics configuration for luxury feel (stiff but smooth damping)
      const { ref: springBind, setTarget } = useSpring({
        tiltX: 0,
        tiltY: 0,
        scale: 1.0,
      }, { stiffness: 120, damping: 16 });

      const cardRef = useRef<HTMLDivElement | null>(null);

      // Define safe callback ref to bundle elements
      const bindRefs = (node: HTMLDivElement | null) => {
        cardRef.current = node;
        springBind(node);
      };

      // Expose methods to parent carousel for coordinated tilt animations
      useImperativeHandle(ref, () => ({
        setTilt: (x: number, y: number) => {
          setTarget({ tiltX: x, tiltY: y });
        },
        setScale: (s: number) => {
          setTarget({ scale: s });
        },
        getElement: () => cardRef.current,
      }));

      // Mouse enter: increase scale target slightly
      const handleMouseEnter = () => {
        setTarget({ scale: 1.06 });
      };

      // Mouse leave: reset scale target
      const handleMouseLeave = () => {
        setTarget({ scale: 1.0 });
      };

      return (
        <div
          ref={bindRefs}
          onClick={onClick}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          className={`relative w-[420px] h-[620px] rounded-[28px] overflow-hidden cursor-pointer select-none preserve-3d transition-all duration-500
            ${isActive 
              ? 'glass-card-active shadow-gold-glow border-gold/40' 
              : 'glass-card shadow-2xl border-white/5 hover:border-gold/25 hover:shadow-gold-glow'
            }`}
          style={{
            transform: 'rotateX(calc(var(--spring-tiltX, 0) * 1deg)) rotateY(calc(var(--spring-tiltY, 0) * 1deg)) scale(var(--spring-scale, 1))',
            transformStyle: 'preserve-3d',
            backfaceVisibility: 'hidden',
            willChange: 'transform',
          }}
        >
          {/* Background - image or fallbacks */}
          <div className="absolute inset-0 w-full h-full preserve-3d" style={{ transform: 'translateZ(-10px)' }}>
            {destination.image ? (
              <img
                src={destination.image}
                alt={destination.name}
                className="w-full h-full object-cover transition-transform duration-700 hover:scale-110"
              />
            ) : (
              <div 
                className="w-full h-full transition-transform duration-700 hover:scale-105"
                style={{ background: destination.cardGradient }}
              />
            )}

            {/* Luxury gold pattern overlay */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-black/60 pointer-events-none" />
            
            {/* Elegant geometric historical lines in background */}
            <div className="absolute inset-0 border border-gold/10 m-4 rounded-[22px] pointer-events-none flex items-center justify-center opacity-40">
              {!destination.image && (
                <Compass className="w-24 h-24 text-gold/10 animate-pulse-slow" />
              )}
            </div>
          </div>

          {/* Shadow overlays for dramatic look */}
          <div className="absolute inset-0 bg-gradient-to-t from-cinematic-950 via-cinematic-950/40 to-transparent pointer-events-none" />

          {/* Content Container */}
          <div 
            className="absolute bottom-0 left-0 right-0 p-8 flex flex-col gap-3 preserve-3d"
            style={{ transform: 'translateZ(30px)' }}
          >
            {/* Era Badge */}
            <div className="flex items-center gap-2">
              <span className="px-3.5 py-1 text-[10px] tracking-[0.2em] font-medium uppercase rounded-full bg-gold/10 border border-gold/30 text-gold shadow-sm backdrop-blur-md">
                {destination.era.split(' • ')[0]}
              </span>
            </div>

            {/* Title */}
            <h3 className="font-serif text-3xl font-bold text-white tracking-wide drop-shadow-md">
              {destination.name}
            </h3>

            {/* Location */}
            <div className="flex items-center gap-1.5 text-gray-400 text-xs tracking-wider">
              <MapPin className="w-3.5 h-3.5 text-gold/80" />
              <span>{destination.location}</span>
            </div>
          </div>

          {/* Interactive Gold Border Effect */}
          <div className="absolute inset-0 border-[0.5px] border-white/5 hover:border-gold/30 rounded-[28px] pointer-events-none transition-colors duration-300" />
        </div>
      );
    }
  )
);

DestinationCard.displayName = "DestinationCard";
