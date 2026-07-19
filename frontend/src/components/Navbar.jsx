import React, { useState, useEffect } from 'react';

// ── Logo: drop any image named logo.png / logo.svg / logo.webp into
// frontend/public/ and it will replace the 'Y' letter automatically.
const LOGO_SRC = '/logo.png';

export default function Navbar({ currentPage, setCurrentPage, onLogout }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [logoError, setLogoError] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out px-6 md:px-16 ${isScrolled
        ? 'py-4 glass-nav backdrop-blur-md shadow-2xl'
        : 'py-6 bg-transparent border-b border-transparent'
        }`}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left Side: YATRA Logo Placeholder */}
        <div className="flex items-center gap-3">
          {/* Logo container with float and shimmer */}
          <div className="relative group cursor-pointer flex items-center gap-2">
            <div className="w-9 h-9 border border-antiqueGold/40 rounded-sm flex items-center justify-center relative overflow-hidden group-hover:border-antiqueGold/80 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-tr from-antiqueGold/10 to-transparent group-hover:opacity-100 transition-opacity"></div>

              {/* Logo image — falls back to 'Y' letter if file is not found */}
              {!logoError ? (
                <img
                  src={LOGO_SRC}
                  alt="Yatra logo"
                  onError={() => setLogoError(true)}
                  className="absolute inset-0 w-full h-full object-cover z-10"
                />
              ) : (
                <span className="font-heading text-lg font-bold text-gold-shimmer select-none relative z-10">Y</span>
              )}

              {/* Decorative corners */}
              <span className="absolute top-0 left-0 w-1.5 h-1.5 border-t border-l border-antiqueGold/60"></span>
              <span className="absolute bottom-0 right-0 w-1.5 h-1.5 border-b border-r border-antiqueGold/60"></span>
            </div>

            {/* Logo text with Cormorant Garamond */}
            <span className="font-heading text-2xl font-bold tracking-[0.25em] text-white group-hover:text-antiqueGold transition-colors duration-300 ml-1 pr-2">
              YATRA
            </span>

            {/* Logo image placeholder comment */}
            {/* <!-- YATRA Logo Placeholder: Add logo illustration / image here --> */}
          </div>
        </div>

        {/* Center: Navigation Links */}
        <div className="flex items-center space-x-6 md:space-x-12">
          <button
            onClick={() => setCurrentPage('home')}
            className={`font-body text-xs md:text-sm tracking-[0.2em] uppercase transition-all duration-300 relative py-1 focus:outline-none ${currentPage === 'home'
              ? 'text-antiqueGold font-medium'
              : 'text-lightGray hover:text-white'
              }`}
          >
            Home
            <span
              className={`absolute bottom-0 left-0 right-0 h-[1px] bg-antiqueGold transition-all duration-300 origin-left ${currentPage === 'home' ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'
                }`}
            ></span>
          </button>

          <button
            onClick={() => setCurrentPage('history')}
            className={`font-body text-xs md:text-sm tracking-[0.2em] uppercase transition-all duration-300 relative py-1 focus:outline-none ${currentPage === 'history'
              ? 'text-antiqueGold font-medium'
              : 'text-lightGray hover:text-white'
              }`}
          >
            History
            <span
              className={`absolute bottom-0 left-0 right-0 h-[1px] bg-antiqueGold transition-all duration-300 origin-left ${currentPage === 'history' ? 'scale-x-100' : 'scale-x-0'
                }`}
            ></span>
          </button>
        </div>

        {/* Right side: Logout button (if provided) */}
        <div className="w-20 md:w-24 hidden md:flex justify-end">
          {onLogout && (
            <button
              onClick={onLogout}
              className="font-body text-xs md:text-sm tracking-[0.2em] text-lightGray hover:text-antiqueGold uppercase transition-colors duration-300 focus:outline-none"
            >
              Log Out
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
