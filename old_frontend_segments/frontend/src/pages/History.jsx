import React, { useState } from 'react';

const INITIAL_HISTORY = [
  {
    id: 'h1',
    placeName: 'Giza Plateau',
    era: 'Old Kingdom Egypt',
    date: 'July 15, 2026',
    description: 'Explored the subterranean burial chambers of Khufu and decyphered the worker markings on the limestone block layers.',
    coordinates: '29.9792° N, 31.1342° E'
  },
  {
    id: 'h2',
    placeName: 'Colosseum of Rome',
    era: 'Roman Empire',
    date: 'July 12, 2026',
    description: 'Observed the opening games under Emperor Titus, mapping the hypogeum tunnel systems and animal elevators.',
    coordinates: '41.8902° N, 12.4922° E'
  },
  {
    id: 'h3',
    placeName: 'Kinkaku-ji (Golden Pavilion)',
    era: 'Muromachi Period Japan',
    date: 'July 10, 2026',
    description: 'Studied the Zen architectural styles, blending Shinden, Bukke, and Zen sect typologies in feudal Japan.',
    coordinates: '35.0394° N, 135.7292° E'
  },
  {
    id: 'h4',
    placeName: 'The Acropolis of Athens',
    era: 'Classical Greece',
    date: 'July 08, 2026',
    description: 'Attended a public assembly at the Pnyx, followed by a walk through the Propylaea during the Panathenaic games.',
    coordinates: '37.9715° N, 23.7257° E'
  },
  {
    id: 'h5',
    placeName: 'Al-Khazneh (Petra)',
    era: 'Nabataean Kingdom',
    date: 'July 05, 2026',
    description: 'Investigated the intricate canyon water reservoirs, tomb architecture, and Nabataean trade-route logistics.',
    coordinates: '30.3285° N, 35.4444° E'
  },
  {
    id: 'h6',
    placeName: 'Babylon Gates',
    era: 'Neo-Babylonian Empire',
    date: 'July 01, 2026',
    description: 'Analyzed the glazed blue brick structures of the Ishtar Gate and met the scribes under King Nebuchadnezzar II.',
    coordinates: '32.5355° N, 44.4244° E'
  }
];

export default function History() {
  const [historyList, setHistoryList] = useState(INITIAL_HISTORY);

  // Handle Share simulation
  const handleShare = (place) => {
    if (navigator.share) {
      navigator.share({
        title: `Yatra Walkthrough: ${place}`,
        text: `Check out my historical walkthrough of ${place} using Yatra!`,
        url: window.location.href,
      }).catch(console.error);
    } else {
      // Fallback
      alert(`Copied link to share: Walkthrough of ${place}`);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col justify-between overflow-hidden cinema-grid select-text pt-28 pb-16 px-6 md:px-16">
      
      {/* Background gradients for dark premium styling */}
      <div className="absolute inset-0 -z-20 pointer-events-none bg-darkBg">
        {/* Subtle decorative radial golden light flare */}
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-antiqueGold/3 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-black rounded-full"></div>
      </div>

      {/* ========================================== */}
      {/* DECORATIVE FLOATING ELEMENT ILLUSTRATIONS   */}
      {/* Fixed position, low z-index, pointer-events-none */}
      {/* 30-40% overflow offset for premium feel. */}
      {/* ========================================== */}

      {/* Top Left → Antique Compass */}
      <div className="fixed -top-16 -left-16 sm:-top-20 sm:-left-20 md:-top-28 md:-left-28 lg:-top-36 lg:-left-36 w-48 h-48 sm:w-64 sm:h-64 md:w-80 md:h-80 lg:w-[400px] lg:h-[400px] z-[1] pointer-events-none rotate-[15deg] select-none opacity-[0.08]">
        <img
          src="/images/floating/compass.png"
          alt="Antique Compass"
          className="w-full h-full object-contain animate-float-compass"
        />
      </div>

      {/* Top Right → Antique Globe */}
      <div className="fixed -top-16 -right-16 sm:-top-20 sm:-right-20 md:-top-28 md:-right-28 lg:-top-36 lg:-right-36 w-48 h-48 sm:w-64 sm:h-64 md:w-80 md:h-80 lg:w-[400px] lg:h-[400px] z-[1] pointer-events-none rotate-[-8deg] select-none opacity-[0.08]">
        <img
          src="/images/floating/globe.png"
          alt="Antique Globe"
          className="w-full h-full object-contain animate-float-globe"
        />
      </div>

      {/* Bottom Left → Ancient Scroll */}
      <div className="fixed -bottom-16 -left-16 sm:-bottom-20 sm:-left-20 md:-bottom-28 md:-left-28 lg:-bottom-36 lg:-left-36 w-48 h-48 sm:w-64 sm:h-64 md:w-80 md:h-80 lg:w-[400px] lg:h-[400px] z-[1] pointer-events-none rotate-[5deg] select-none opacity-[0.08]">
        <img
          src="/images/floating/scroll.png"
          alt="Ancient Scroll"
          className="w-full h-full object-contain animate-float-scroll"
        />
      </div>

      {/* Bottom Right → Antique Hourglass */}
      <div className="fixed -bottom-16 -right-16 sm:-bottom-20 sm:-right-20 md:-bottom-28 md:-right-28 lg:-bottom-36 lg:-right-36 w-48 h-48 sm:w-64 sm:h-64 md:w-80 md:h-80 lg:w-[400px] lg:h-[400px] z-[1] pointer-events-none rotate-[-6deg] select-none opacity-[0.08]">
        <img
          src="/images/floating/hourglass.png"
          alt="Antique Hourglass"
          className="w-full h-full object-contain animate-float-hourglass"
        />
      </div>

      <div className="max-w-7xl mx-auto w-full flex-grow flex flex-col z-10 animate-slide-up">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="h-[1px] w-8 bg-antiqueGold/60"></span>
              <span className="font-body text-xs tracking-[0.25em] text-antiqueGold font-medium uppercase">
                Temporal Log
              </span>
            </div>
            <h1 className="font-heading text-4xl md:text-6xl font-bold tracking-widest text-white uppercase">
              History
            </h1>
          </div>
        </div>

        {/* Grid of History Cards */}
        {historyList.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {historyList.map((item) => (
              <div
                key={item.id}
                className="glass-card rounded-lg border border-white/5 p-6 flex flex-col justify-between group hover:border-antiqueGold/40 hover:shadow-[0_4px_30px_rgba(212,175,55,0.08)] transition-all duration-500 hover:-translate-y-1"
              >
                <div>
                  {/* Thumbnail Placeholder container */}
                  {/* <!-- Thumbnail Placeholder --> */}
                  <div className="relative w-full h-44 rounded overflow-hidden border border-white/10 bg-black/50 mb-5 flex items-center justify-center">
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent z-10"></div>
                    
                    {/* Wireframe geometric details */}
                    <div className="w-16 h-16 border border-dashed border-antiqueGold/15 rounded flex items-center justify-center z-10 group-hover:border-antiqueGold/35 transition-colors duration-500">
                      <span className="text-[8px] tracking-widest text-white/30 uppercase select-none">THUMBNAIL</span>
                    </div>

                    {/* Coordinates overlay at the top left */}
                    <span className="absolute top-3 left-3 z-10 font-body text-[8px] tracking-wider text-lightGray bg-black/60 px-2 py-0.5 rounded border border-white/5">
                      {item.coordinates}
                    </span>
                  </div>

                  {/* Date and Era header */}
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-body text-[9px] tracking-wider text-antiqueGold font-medium uppercase">
                      {item.era}
                    </span>
                    <span className="font-body text-[9px] tracking-wider text-lightGray/70 uppercase">
                      {item.date}
                    </span>
                  </div>

                  {/* Place Name */}
                  <h3 className="font-heading text-xl md:text-2xl font-bold tracking-wide text-white mb-3 group-hover:text-antiqueGold transition-colors duration-300">
                    {item.placeName}
                  </h3>

                  {/* Description */}
                  <p className="font-body text-xs text-lightGray leading-relaxed font-light mb-6">
                    {item.description}
                  </p>
                </div>

                {/* Footer Buttons */}
                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/5">
                  
                  {/* Open Button */}
                  <button
                    onClick={() => alert(`Launching immersive walkthrough for ${item.placeName}...`)}
                    className="py-2.5 rounded bg-antiqueGold hover:bg-white text-black font-body text-[10px] font-semibold tracking-[0.2em] uppercase transition-all duration-300 active:scale-[0.98]"
                  >
                    Open Yatra
                  </button>

                  {/* Share Button */}
                  <button
                    onClick={() => handleShare(item.placeName)}
                    className="py-2.5 rounded border border-white/10 hover:border-antiqueGold text-white hover:text-antiqueGold font-body text-[10px] font-medium tracking-[0.2em] uppercase transition-all duration-300 active:scale-[0.98] bg-white/[0.02]"
                  >
                    Share
                  </button>

                </div>

              </div>
            ))}
          </div>
        ) : (
          <div className="flex-grow flex flex-col items-center justify-center py-20 text-center">
            <span className="text-4xl mb-4 select-none">🕳️</span>
            <h3 className="font-heading text-xl text-white tracking-widest uppercase mb-1">No Archives Found</h3>
            <p className="font-body text-xs text-lightGray max-w-xs font-light">
              Your historical footsteps have not yet crossed this combination. Try searching a different period.
            </p>
          </div>
        )}

      </div>

      {/* Decorative footer metrics */}
      <div className="max-w-7xl mx-auto w-full px-6 md:px-16 mt-16 flex items-center justify-between text-[8px] md:text-[10px] tracking-[0.25em] text-lightGray/40 select-none border-t border-white/5 pt-8 z-10">
        <span>YATRA TEMPORAL CHRONOLOGY CHANNELS ACTIVE</span>
        <span>STABLE CONTEXT BLOCK: #384920</span>
      </div>

    </div>
  );
}
