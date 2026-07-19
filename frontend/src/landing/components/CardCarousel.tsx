import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import type { Destination } from '../data/destinations';
import { DestinationCard } from './DestinationCard';
import type { DestinationCardRef } from './DestinationCard';

interface CardCarouselProps {
  destinations: Destination[];
  activeIndex: number;
  setActiveIndex: React.Dispatch<React.SetStateAction<number>>;
}

export const CardCarousel: React.FC<CardCarouselProps> = ({
  destinations,
  activeIndex,
  setActiveIndex,
}) => {
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1200);
  const cardRefs = useRef<(DestinationCardRef | null)[]>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);
  
  // Interaction/Animation states stored in refs to avoid React re-renders
  const mouseRef = useRef({ x: 0, y: 0 });
  const isInsideRef = useRef(false);
  const rAFId = useRef<number | null>(null);
  const cardCentersRef = useRef<{ x: number; y: number }[]>([]);
  
  // Timer references
  const autoplayTimerRef = useRef<number | null>(null);
  const resumeTimeoutRef = useRef<number | null>(null);
  const isHoveredRef = useRef(false);

  // 1. Memoized Window Resize Handler
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 2. Cache Card Center coordinates mathematically to prevent getBoundingClientRect layout thrashing
  const updateCardCenters = useCallback(() => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    const isMobile = windowWidth < 640;
    const isTablet = windowWidth >= 640 && windowWidth < 1024;
    const S = isMobile ? 120 : isTablet ? 190 : 270;

    cardCentersRef.current = destinations.map((_, index) => {
      let rel = index - activeIndex;
      const N = destinations.length;
      rel = ((rel % N) + N) % N;
      if (rel > N / 2) rel -= N;
      return {
        x: cx + rel * S,
        y: cy,
      };
    });
  }, [activeIndex, windowWidth, destinations.length]);

  useEffect(() => {
    updateCardCenters();
  }, [updateCardCenters]);

  // 3. 60 FPS RequestAnimationFrame tracking loop (Throttles calculations without updating state)
  const tick = useCallback(() => {
    const mx = mouseRef.current.x;
    const my = mouseRef.current.y;
    const isInside = isInsideRef.current;
    const centers = cardCentersRef.current;
    const sensitivityRadius = Math.max(windowWidth / 2, 700);

    cardRefs.current.forEach((cardRef, idx) => {
      if (!cardRef) return;

      if (isInside && centers[idx]) {
        const dx = mx - centers[idx].x;
        const dy = my - centers[idx].y;

        const percentX = Math.max(-1, Math.min(1, dx / sensitivityRadius));
        const percentY = Math.max(-1, Math.min(1, dy / sensitivityRadius));

        // Calculate tilts (rotateX ±8°, rotateY ±12°)
        const tiltX = -percentY * 8;
        const tiltY = percentX * 12;

        cardRef.setTilt(tiltX, tiltY);
      } else {
        cardRef.setTilt(0, 0); // Settle smoothly
      }
    });

    rAFId.current = requestAnimationFrame(tick);
  }, [windowWidth]);

  // Handle global mousemove event coordinates
  const handleMouseMove = useCallback((e: MouseEvent) => {
    mouseRef.current.x = e.clientX;
    mouseRef.current.y = e.clientY;
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]);

  // 4. Autoplay Rotation Logic (looping 1 -> 2 -> 3 -> 4 -> 5 -> 1)
  const startAutoplay = useCallback(() => {
    if (autoplayTimerRef.current) {
      clearInterval(autoplayTimerRef.current);
    }
    
    autoplayTimerRef.current = window.setInterval(() => {
      if (!isHoveredRef.current) {
        setActiveIndex((prev) => (prev + 1) % destinations.length);
      }
    }, 2500);
  }, [destinations.length, setActiveIndex]);

  const stopAutoplay = useCallback(() => {
    if (autoplayTimerRef.current) {
      clearInterval(autoplayTimerRef.current);
      autoplayTimerRef.current = null;
    }
  }, []);

  const handleMouseEnter = useCallback(() => {
    isHoveredRef.current = true;
    isInsideRef.current = true;
    
    // Clear autoplay immediately on hover
    stopAutoplay();
    if (resumeTimeoutRef.current) {
      clearTimeout(resumeTimeoutRef.current);
      resumeTimeoutRef.current = null;
    }
  }, [stopAutoplay]);

  const handleMouseLeave = useCallback(() => {
    isHoveredRef.current = false;
    isInsideRef.current = false;
    mouseRef.current = { x: 0, y: 0 }; // Settle coordinates

    if (resumeTimeoutRef.current) {
      clearTimeout(resumeTimeoutRef.current);
    }

    // Resume autoplay after 2 seconds
    resumeTimeoutRef.current = window.setTimeout(() => {
      startAutoplay();
    }, 2000);
  }, [startAutoplay]);

  // Coordinates autoplay lifecycle
  useEffect(() => {
    startAutoplay();
    rAFId.current = requestAnimationFrame(tick);

    return () => {
      stopAutoplay();
      if (resumeTimeoutRef.current) clearTimeout(resumeTimeoutRef.current);
      if (rAFId.current) cancelAnimationFrame(rAFId.current);
    };
  }, [startAutoplay, tick, stopAutoplay]);

  // 5. Memoized click-to-focus handler
  const handleCardClick = useCallback((index: number) => {
    if (index !== activeIndex) {
      setActiveIndex(index);
      
      // Reset autoplay timer immediately on click
      stopAutoplay();
      startAutoplay();
    }
  }, [activeIndex, setActiveIndex, stopAutoplay, startAutoplay]);

  // 6. Memoized layout calculation (pre-computes values to avoid heavy computation during rendering)
  const cardStyles = useMemo(() => {
    return destinations.map((_, index) => {
      let rel = index - activeIndex;
      const N = destinations.length;
      
      // Circular mapping
      rel = ((rel % N) + N) % N;
      if (rel > N / 2) rel -= N;

      const isMobile = windowWidth < 640;
      const isTablet = windowWidth >= 640 && windowWidth < 1024;

      const S = isMobile ? 120 : isTablet ? 190 : 270;
      const tx = rel * S;
      const ty = 0;

      const tz = Math.abs(rel) * (isMobile ? -80 : -130);

      let ry = 0;
      if (rel !== 0) {
        const baseRot = isMobile ? 18 : 22;
        ry = -rel * baseRot;
      }

      let s = 1.0;
      if (isMobile) {
        s = rel === 0 ? 0.72 : Math.abs(rel) === 1 ? 0.56 : 0.42;
      } else if (isTablet) {
        s = rel === 0 ? 0.88 : Math.abs(rel) === 1 ? 0.74 : 0.58;
      } else {
        s = rel === 0 ? 1.0 : Math.abs(rel) === 1 ? 0.8 : 0.64;
      }

      const zIndex = 30 - Math.abs(rel) * 10;
      const opacity = rel === 0 ? 1.0 : Math.abs(rel) === 1 ? 0.85 : 0.55;

      return {
        tx,
        ty,
        tz,
        ry,
        s,
        zIndex,
        opacity,
      };
    });
  }, [activeIndex, windowWidth, destinations.length]);

  return (
    <div
      ref={containerRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="relative w-full h-[520px] sm:h-[600px] lg:h-[680px] flex items-center justify-center perspective-2000 overflow-visible select-none"
    >
      {destinations.map((dest, idx) => {
        const styles = cardStyles[idx];
        const isCenter = idx === activeIndex;

        return (
          <motion.div
            key={dest.id}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transformStyle: 'preserve-3d',
              zIndex: styles.zIndex,
              pointerEvents: isCenter ? 'auto' : 'auto', // Keep clickable
              willChange: 'transform, opacity',
            }}
            animate={{
              // Center coordinates translated by half of card width/height
              x: styles.tx - 210,
              y: styles.ty - 310,
              z: styles.tz,
              rotateY: styles.ry,
              scale: styles.s,
              opacity: styles.opacity,
            }}
            // GPU-accelerated spring animations matching user guidelines
            transition={{
              type: 'spring',
              stiffness: 120,
              damping: 18,
              mass: 0.8,
            }}
            className="preserve-3d backface-hidden"
          >
            <DestinationCard
              ref={(el) => {
                cardRefs.current[idx] = el;
              }}
              destination={dest}
              isActive={isCenter}
              onClick={() => handleCardClick(idx)}
            />
          </motion.div>
        );
      })}
    </div>
  );
};
