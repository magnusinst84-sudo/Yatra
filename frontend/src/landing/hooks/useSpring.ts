import { useEffect, useRef } from 'react';

interface SpringConfig {
  stiffness?: number;
  damping?: number;
}

export function useSpring<T extends Record<string, number>>(
  initialValues: T,
  config: SpringConfig = { stiffness: 150, damping: 18 }
) {
  const currentRef = useRef<T>({ ...initialValues });
  const targetRef = useRef<T>({ ...initialValues });
  
  // Initialize velocity tracker
  const velocityRef = useRef<Record<keyof T, number>>(
    Object.keys(initialValues).reduce((acc, key) => {
      acc[key as keyof T] = 0;
      return acc;
    }, {} as Record<keyof T, number>)
  );
  
  const elementRef = useRef<HTMLElement | null>(null);
  const animationFrameId = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  const setTarget = (newTargets: Partial<T>) => {
    targetRef.current = { ...targetRef.current, ...newTargets };
    // Start animation loop if not already running
    if (animationFrameId.current === null) {
      lastTimeRef.current = performance.now();
      animate();
    }
  };

  const animate = () => {
    const now = performance.now();
    let dt = (now - lastTimeRef.current) / 1000;
    lastTimeRef.current = now;

    // Cap dt to prevent massive jumps when tab is inactive or performance lags
    if (dt > 0.03) dt = 0.03;

    let isMoving = false;
    const current = currentRef.current;
    const target = targetRef.current;
    const velocity = velocityRef.current;
    const stiffness = config.stiffness ?? 150;
    const damping = config.damping ?? 18;

    for (const key in target) {
      const curVal = current[key];
      const tarVal = target[key];
      const vel = velocity[key];

      const diff = curVal - tarVal;
      const force = -stiffness * diff - damping * vel;
      const nextVel = vel + force * dt;
      const nextVal = curVal + nextVel * dt;

      // Check if value is still moving significantly
      if (Math.abs(nextVel) > 0.0001 || Math.abs(diff) > 0.0001) {
        current[key] = nextVal as any;
        velocity[key] = nextVel;
        isMoving = true;
      } else {
        current[key] = tarVal;
        velocity[key] = 0;
      }
    }

    // Apply animated values as CSS variables directly to the DOM element
    if (elementRef.current) {
      for (const key in current) {
        elementRef.current.style.setProperty(`--spring-${key}`, current[key].toFixed(4));
      }
    }

    if (isMoving) {
      animationFrameId.current = requestAnimationFrame(animate);
    } else {
      animationFrameId.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (animationFrameId.current !== null) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, []);

  // Initialize CSS variables on mount or when element changes
  const bindRef = (node: HTMLElement | null) => {
    elementRef.current = node;
    if (node) {
      for (const key in currentRef.current) {
        node.style.setProperty(`--spring-${key}`, currentRef.current[key].toString());
      }
    }
  };

  return {
    ref: bindRef,
    setTarget,
    currentRef,
    targetRef,
  };
}
