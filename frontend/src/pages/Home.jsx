import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { startWalkthrough } from '../services/api';
import WalkthroughModal from '../components/WalkthroughModal';

// Predefined destination data to feed the state
const INITIAL_DESTINATIONS = [
  {
    id: 1,
    name: 'AYODHYA',
    subtitle: 'The Divine City',
    era: 'Ancient',
    description: 'Discover the sacred city of Ayodhya, where magnificent temple architecture, peaceful courtyards, and centuries of devotion celebrate the birthplace of Lord Rama. Experience one of India’s holiest cities, where faith, history, and timeless heritage come together.',
    background: '/images/backgrounds/ayodhya_bg.png',
    cardImage: '/images/cards/ayodhya_div_bg.png'
  },
  {
    id: 2,
    name: 'JAIPUR',
    subtitle: 'The Pink City',
    era: 'Medieval',
    description: 'Discover the majestic Pink City of Jaipur, where grand forts and ornate palaces tell tales of Rajput valor and architectural brilliance. From the iconic Hawa Mahal to the imposing Amber Fort, every corner echoes royal grandeur.',
    background: '/images/backgrounds/jaipur_bg.png',
    cardImage: '/images/cards/jaipur_div_bg.png'
  },
  {
    id: 3,
    name: 'PUNE',
    subtitle: 'The Maratha Stronghold',
    era: 'Medieval',
    description: 'Walk through the magnificent courtyards of Shaniwar Wada, where carved wooden balconies, majestic pillars, and royal halls stand as enduring symbols of the Peshwa dynasty. Experience the architectural brilliance and rich legacy of the Maratha Empire at the heart of historic Pune',
    background: '/images/backgrounds/pune_bg.png',
    cardImage: '/images/cards/pune_div_bg.png'
  },
  {
    id: 4,
    name: 'VARANASI',
    subtitle: 'The Eternal City',
    era: 'Ancient',
    description: 'Experience the oldest living city in the world Varanasi. Witness the mesmerizing Ganga Aarti on the ghats, navigate the narrow ancient lanes, and feel the profound spiritual energy that has drawn seekers for millennia.',
    background: '/images/backgrounds/varanasi_bg.png',
    cardImage: '/images/cards/varanasi_div_bg.png'
  },
  {
    id: 5,
    name: 'VIJAYANAGAR',
    subtitle: 'The City of Victory',
    era: 'Ancient',
    description: 'Journey to the ruins of the magnificent Vijayanagar Empire at Hampi. Marvel at the stunning stone temples, royal enclosures, and the iconic stone chariot remnants of one of the richest and most powerful empires in Indian history.',
    background: '/images/backgrounds/vijayanagar_bg.png',
    cardImage: '/images/cards/vijayanagar_div_bg.png'
  }
];

const getTitleFontSize = (name) => {
  const len = name.length;
  if (len <= 4) {
    return 'text-6xl md:text-8xl lg:text-9xl';
  } else if (len <= 8) {
    return 'text-5xl md:text-7xl lg:text-8xl';
  } else {
    return 'text-4xl md:text-6xl lg:text-6xl';
  }
};

export default function Home() {
  const { idToken } = useContext(AuthContext);
  const [destinations, setDestinations] = useState(INITIAL_DESTINATIONS);
  const [activeIndex, setActiveIndex] = useState(0);
  const [searchPlace, setSearchPlace] = useState('');

  // Walkthrough state
  const [walkthrough, setWalkthrough] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const loadingTexts = [
    "Gathering context...",
    "Generating the first scene...",
    "Consulting historical archives...",
    "Assembling the timeline..."
  ];
  const [loadingTextIndex, setLoadingTextIndex] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setLoadingTextIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setLoadingTextIndex((prev) => (prev + 1) % loadingTexts.length);
    }, 2500);
    return () => clearInterval(interval);
  }, [isLoading]);

  // Local display states synced with fade transition
  const [displayEra, setDisplayEra] = useState(INITIAL_DESTINATIONS[0].era);
  const [displayName, setDisplayName] = useState(INITIAL_DESTINATIONS[0].name);
  const [displayDesc, setDisplayDesc] = useState(INITIAL_DESTINATIONS[0].description);
  const [isFading, setIsFading] = useState(false);
  const [selectedEra, setSelectedEra] = useState('Ancient');

  // Autoplay timer that changes featured place every 3s
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % destinations.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [activeIndex, destinations.length]);

  // Sync display states when active destination changes with a smooth fade transition (600ms)
  useEffect(() => {
    setIsFading(true);
    const timer = setTimeout(() => {
      setDisplayEra(destinations[activeIndex].era);
      setDisplayName(destinations[activeIndex].name);
      setDisplayDesc(destinations[activeIndex].description);
      setIsFading(false);
    }, 300); // 300ms fade out, then updates content and fades back in
    return () => clearTimeout(timer);
  }, [activeIndex, destinations]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchPlace.trim()) return;
    setSearchError(null);
    setIsLoading(true);
    try {
      const result = await startWalkthrough(searchPlace.trim(), selectedEra, idToken);
      setWalkthrough(result);
    } catch (err) {
      setSearchError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCardClick = async (dest, idx) => {
    setActiveIndex(idx);
    setSearchError(null);
    setIsLoading(true);
    try {
      const result = await startWalkthrough(dest.name, dest.era, idToken);
      setWalkthrough(result);
    } catch (err) {
      setSearchError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="relative min-h-screen w-full flex flex-col justify-between overflow-hidden cinema-grid select-text">

        {/* ========================================== */}
        {/* HERO BACKGROUND & GRADIENT OVERLAYS        */}
        {/* ========================================== */}

        {/* Hero Background Placeholder */}
        {/* I will manually add historical background images */}
        <div
          className={`absolute inset-0 bg-cover bg-center transition-opacity duration-[600ms] -z-30 bg-darkBg ${isFading ? 'opacity-0' : 'opacity-100'
            }`}
          style={{
            backgroundImage: `url('${destinations[activeIndex].background}')`,
          }}
        >
          {/* Subtle cinematic radial grid flare */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(212,175,55,0.02)_0%,transparent_70%)]"></div>
        </div>

        {/* Cinematic Dark & Gradient Overlays */}
        <div className="absolute inset-0 -z-20 pointer-events-none">
          {/* Left deep overlay for text readability */}
          <div className="absolute inset-y-0 left-0 w-full md:w-3/5 bg-gradient-to-r from-black via-black/80 to-transparent"></div>
          {/* Bottom vertical gradient to black out footer and hide image seam */}
          <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-[#0D0D0D] via-[#0D0D0D]/60 to-transparent"></div>
          {/* Top vertical gradient for navbar readability */}
          <div className="absolute inset-x-0 top-0 h-1/4 bg-gradient-to-b from-black/80 to-transparent"></div>
        </div>


        {/* ========================================== */}
        {/* MAIN HERO CONTENT - LEFT                   */}
        {/* ========================================== */}

        <div className="max-w-7xl mx-auto w-full px-6 md:px-16 pt-32 pb-16 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center flex-grow">

          {/* LEFT COLUMN: Texts & Form inputs */}
          <div className="lg:col-span-7 flex flex-col justify-center h-full z-10 animate-slide-up">

            {/* Era, Name and Description with smooth fade transition */}
            <div className={`transition-opacity duration-[600ms] ${isFading ? 'opacity-0' : 'opacity-100'}`}>
              {/* Timeline details like a museum site */}
              <div className="flex items-center gap-4 mb-4 select-none">
                <span className="h-[1px] w-12 bg-antiqueGold/60"></span>
                <span className="font-body text-xs tracking-[0.3em] text-antiqueGold font-medium uppercase">
                  {displayEra}
                </span>
              </div>

              {/* Place Name */}
              <div className="mb-4 max-w-full lg:max-w-[58vw]">
                <h1 className={`font-heading ${getTitleFontSize(displayName)} font-bold tracking-widest text-white leading-none uppercase select-text break-words`}>
                  {displayName}
                </h1>
              </div>

              {/* Description */}
              <div className="mb-10 max-w-xl">
                <p className="font-body text-sm md:text-base text-lightGray leading-relaxed font-light select-text">
                  {displayDesc}
                </p>
              </div>
            </div>

            {/* SEARCH FORM PANEL WITH GLASSMORPHISM */}
            <form onSubmit={handleSearch} className="glass-panel p-6 rounded-lg max-w-lg border border-white/10 shadow-2xl relative overflow-hidden group">
              {/* Ambient gold glow on hover */}
              <div className="absolute -right-24 -bottom-24 w-48 h-48 bg-antiqueGold/5 rounded-full blur-3xl group-hover:bg-antiqueGold/10 transition-all duration-700 pointer-events-none"></div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* Search Place Input */}
                <div className="flex flex-col gap-1.5">
                  <label className="font-body text-[10px] tracking-[0.2em] text-lightGray uppercase ml-1">
                    Search Place
                  </label>
                  <input
                    type="text"
                    value={searchPlace}
                    onChange={(e) => setSearchPlace(e.target.value)}
                    placeholder="e.g. Pune,Varanasi,Ayodhya..."
                    className="glass-input px-4 py-3 rounded text-sm text-white placeholder-white/35 focus:ring-1 focus:ring-antiqueGold"
                    required
                  />
                </div>

                {/* Select Era Input */}
                <div className="flex flex-col gap-1.5">
                  <label className="font-body text-[10px] tracking-[0.2em] text-lightGray uppercase ml-1">
                    Select Era
                  </label>
                  <select
                    value={selectedEra}
                    onChange={(e) => setSelectedEra(e.target.value)}
                    className="glass-input px-4 py-3 rounded text-sm text-white focus:ring-1 focus:ring-antiqueGold cursor-pointer appearance-none bg-darkBg"
                    style={{
                      backgroundImage: `url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%23D4AF37' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E")`,
                      backgroundPosition: 'right 0.75rem center',
                      backgroundSize: '1.25rem',
                      backgroundRepeat: 'no-repeat',
                      paddingRight: '2.5rem'
                    }}
                  >
                    <option value="Ancient" className="bg-[#121212]">Ancient</option>
                    <option value="Medieval" className="bg-[#121212]">Medieval</option>
                    <option value="Modern" className="bg-[#121212]">Modern</option>
                  </select>
                </div>
              </div>

              {/* Large Rounded Search Button */}
              <button
                type="submit"
                className="w-full py-3.5 rounded bg-gradient-to-r from-antiqueGold via-antiqueGold-light to-antiqueGold-dark hover:from-white hover:to-white text-black font-body text-xs font-semibold tracking-[0.25em] uppercase transition-all duration-500 shadow-[0_4px_20px_rgba(212,175,55,0.25)] hover:shadow-[0_4px_25px_rgba(255,255,255,0.4)] active:scale-[0.98] focus:outline-none"
              >
                Search Timeline
              </button>
            </form>

          </div>

          {/* ========================================== */}
          {/* DESTINATION CARDS - RIGHT                  */}
          {/* ========================================== */}

          {/* RIGHT COLUMN: Vertical stack of exactly 5 cards */}
          <div className="lg:col-span-5 flex flex-col gap-4 justify-center z-10 animate-fade-in lg:pl-8">

            <div className="flex items-center justify-between mb-2 select-none">
              <span className="font-heading text-xs tracking-[0.25em] text-antiqueGold uppercase font-semibold">Recommended Yatras</span>
              <span className="font-body text-[10px] text-lightGray">0{activeIndex + 1} &nbsp;/&nbsp; 05</span>
            </div>

            <div className="flex flex-col gap-3.5 max-h-[480px] overflow-y-auto pr-1">
              {destinations.map((dest, idx) => {
                const isActive = idx === activeIndex;
                return (
                  <div
                    key={dest.id}
                    onClick={() => handleCardClick(dest, idx)}
                    className={`group relative rounded-lg cursor-pointer p-4 transition-all duration-500 flex items-center justify-between overflow-hidden border ${isActive
                      ? 'glass-card border-antiqueGold shadow-[0_0_20px_rgba(212,175,55,0.15)] translate-x-1'
                      : 'bg-white/[0.02] border-white/5 hover:border-white/20 hover:bg-white/[0.04]'
                      }`}
                  >
                    {/* Subtle active state golden glow side bar */}
                    <div
                      className={`absolute left-0 top-0 bottom-0 w-[3px] bg-antiqueGold transition-transform duration-500 ${isActive ? 'scale-y-100' : 'scale-y-0 group-hover:scale-y-100 origin-center'
                        }`}
                    ></div>

                    {/* Left part of card: Text info */}
                    <div className="flex flex-col gap-1 z-10 pl-2">
                      <span className="font-body text-[8px] tracking-[0.2em] text-antiqueGold/70 uppercase font-medium">
                        {dest.era}
                      </span>
                      <h3 className="font-heading text-lg md:text-xl tracking-wider text-white font-bold group-hover:text-antiqueGold transition-colors duration-300">
                        {dest.name}
                      </h3>
                      <p className="font-body text-[10px] text-lightGray font-light">
                        {dest.subtitle}
                      </p>
                    </div>

                    {/* Right part of card: Image Container */}
                    <div className="relative w-20 h-14 md:w-24 md:h-16 rounded overflow-hidden border border-white/10 bg-black/40 flex items-center justify-center shrink-0">

                      {/* Destination Card Image */}
                      <img
                        src={dest.cardImage}
                        alt={dest.name}
                        className="absolute inset-0 w-full h-full object-cover"
                      />

                      <div className="absolute inset-0 bg-gradient-to-tr from-black/80 to-transparent z-10"></div>

                      {/* Golden accent stripe */}
                      <div className={`absolute bottom-0 right-0 w-1.5 h-1.5 bg-antiqueGold/40 transition-transform z-20 ${isActive ? 'scale-100' : 'scale-0 group-hover:scale-100'
                        }`}></div>
                    </div>

                  </div>
                );
              })}
            </div>

          </div>

        </div>

        {/* ========================================== */}
        {/* NAVIGATION ARROWS & DECORATIVE BOTTOM      */}
        {/* ========================================== */}

        <div className="max-w-7xl mx-auto w-full px-6 md:px-16 pb-10 flex items-center justify-between z-10 select-none">

          {/* Left Side: Page counter / coordinates detail */}
          <div className="hidden md:flex items-center gap-6 font-body text-[10px] tracking-[0.25em] text-lightGray/80">
            <span>YATRA SYSTEM v1.0.4</span>
            <span className="w-1.5 h-1.5 bg-antiqueGold/60 rounded-full animate-pulse-subtle"></span>
          </div>

          {/* Right Side: Large Navigation Arrows (Animation only) */}
          <div className="flex items-center gap-6 ml-auto md:ml-0">
            <button
              type="button"
              onClick={() => setActiveIndex((prev) => (prev === 0 ? destinations.length - 1 : prev - 1))}
              className="w-12 h-12 rounded-full border border-white/15 hover:border-antiqueGold flex items-center justify-center group transition-all duration-300 hover:bg-white/[0.02]"
              title="Previous Yatra"
            >
              <span className="text-lightGray group-hover:text-antiqueGold text-lg font-body transition-all duration-300 group-hover:-translate-x-1">
                ←
              </span>
            </button>

            <span className="h-[1px] w-8 bg-white/10"></span>

            <button
              type="button"
              onClick={() => setActiveIndex((prev) => (prev === destinations.length - 1 ? 0 : prev + 1))}
              className="w-12 h-12 rounded-full border border-white/15 hover:border-antiqueGold flex items-center justify-center group transition-all duration-300 hover:bg-white/[0.02]"
              title="Next Yatra"
            >
              <span className="text-lightGray group-hover:text-antiqueGold text-lg font-body transition-all duration-300 group-hover:translate-x-1">
                →
              </span>
            </button>
          </div>

        </div>

      </div>

      {/* ── Loading Overlay ── */}
      {isLoading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="glass-panel rounded-xl px-10 py-8 flex flex-col items-center gap-5 border border-antiqueGold/20 shadow-2xl">
            <div className="w-12 h-12 border-2 border-antiqueGold border-t-transparent rounded-full animate-spin" />
            <p className="font-body text-sm tracking-[0.2em] text-antiqueGold uppercase animate-pulse">
              {loadingTexts[loadingTextIndex]}
            </p>
          </div>
        </div>
      )}

      {/* ── Error Toast ── */}
      {searchError && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-fade-in">
          <div className="glass-panel rounded-lg px-6 py-3 border border-red-500/30 flex items-center gap-4 shadow-xl">
            <span className="text-red-400 text-sm font-body">{searchError}</span>
            <button onClick={() => setSearchError(null)} className="text-lightGray hover:text-white text-xs">✕</button>
          </div>
        </div>
      )}

      {/* ── Walkthrough Modal ── */}
      {walkthrough && (
        <WalkthroughModal
          walkthrough={walkthrough}
          onClose={() => setWalkthrough(null)}
        />
      )}
    </>
  );
}
