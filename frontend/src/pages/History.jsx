import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { getMyWalkthroughs, getWalkthroughById, shareWalkthrough } from '../services/api';
import WalkthroughModal from '../components/WalkthroughModal';

export default function History() {
  const { idToken } = useContext(AuthContext);
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [activeWalkthrough, setActiveWalkthrough] = useState(null);
  const [copiedId, setCopiedId]       = useState(null);

  useEffect(() => {
    if (!idToken) { setLoading(false); return; }
    getMyWalkthroughs(idToken)
      .then(setHistoryList)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [idToken]);

  const handleOpen = async (walkthroughId) => {
    try {
      const wt = await getWalkthroughById(walkthroughId);
      setActiveWalkthrough(wt);
    } catch (err) {
      console.error('Failed to load walkthrough:', err);
    }
  };

  const handleShare = async (item) => {
    if (!idToken) return;
    try {
      const { share_slug } = await shareWalkthrough(item.walkthrough_id, idToken);
      const url = `${window.location.origin}/shared/${share_slug}`;
      await navigator.clipboard.writeText(url).catch(() => {});
      setCopiedId(item.walkthrough_id);
      setTimeout(() => setCopiedId(null), 3000);
    } catch (err) {
      console.error('Share failed:', err);
    }
  };

  // Format ISO date string to a readable label
  const formatDate = (iso) => {
    if (!iso) return '';
    try { return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }); }
    catch { return iso; }
  };

  return (
    <>
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
        {loading ? (
          /* Skeleton loading state */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1,2,3].map((n) => (
              <div key={n} className="glass-card rounded-lg border border-white/5 p-6 animate-pulse">
                <div className="w-full h-44 rounded bg-white/5 mb-5" />
                <div className="h-3 w-16 bg-white/10 rounded mb-2" />
                <div className="h-6 w-3/4 bg-white/10 rounded mb-3" />
                <div className="h-3 w-full bg-white/5 rounded mb-1" />
                <div className="h-3 w-5/6 bg-white/5 rounded" />
              </div>
            ))}
          </div>
        ) : historyList.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {historyList.map((item) => (
              <div
                key={item.walkthrough_id}
                className="glass-card rounded-lg border border-white/5 p-6 flex flex-col justify-between group hover:border-antiqueGold/40 hover:shadow-[0_4px_30px_rgba(212,175,55,0.08)] transition-all duration-500 hover:-translate-y-1"
              >
                <div>
                  {/* Thumbnail */}
                  <div className="relative w-full h-44 rounded overflow-hidden border border-white/10 bg-black/50 mb-5">
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent z-10" />
                    {item.thumbnail_url ? (
                      <img
                        src={item.thumbnail_url}
                        alt={item.place}
                        className="absolute inset-0 w-full h-full object-cover"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-16 h-16 border border-dashed border-antiqueGold/15 rounded flex items-center justify-center z-10 group-hover:border-antiqueGold/35 transition-colors duration-500">
                          <span className="text-[8px] tracking-widest text-white/30 uppercase select-none">THUMBNAIL</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Era & date */}
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-body text-[9px] tracking-wider text-antiqueGold font-medium uppercase">{item.era}</span>
                    <span className="font-body text-[9px] tracking-wider text-lightGray/70 uppercase">{formatDate(item.created_at)}</span>
                  </div>

                  {/* Place Name */}
                  <h3 className="font-heading text-xl md:text-2xl font-bold tracking-wide text-white mb-3 group-hover:text-antiqueGold transition-colors duration-300">
                    {item.place}
                  </h3>
                </div>

                {/* Footer Buttons */}
                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/5">
                  <button
                    onClick={() => handleOpen(item.walkthrough_id)}
                    className="py-2.5 rounded bg-antiqueGold hover:bg-white text-black font-body text-[10px] font-semibold tracking-[0.2em] uppercase transition-all duration-300 active:scale-[0.98]"
                  >
                    Open Yatra
                  </button>
                  <button
                    onClick={() => handleShare(item)}
                    className="py-2.5 rounded border border-white/10 hover:border-antiqueGold text-white hover:text-antiqueGold font-body text-[10px] font-medium tracking-[0.2em] uppercase transition-all duration-300 active:scale-[0.98] bg-white/[0.02]"
                  >
                    {copiedId === item.walkthrough_id ? '✓ Copied!' : 'Share'}
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

    {/* Walkthrough Modal */}
    {activeWalkthrough && (
      <WalkthroughModal
        walkthrough={activeWalkthrough}
        onClose={() => setActiveWalkthrough(null)}
      />
    )}
  </>
  );
}
