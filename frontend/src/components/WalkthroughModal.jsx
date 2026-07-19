import React, { useContext, useState } from 'react';
import { AuthContext } from '../App';
import { saveWalkthrough, shareWalkthrough } from '../services/api';

/**
 * WalkthroughModal
 * ----------------
 * Full-screen overlay that renders an AI-generated historical walkthrough.
 *
 * Props:
 *   walkthrough  — the full world_state object from the backend
 *   onClose      — callback to dismiss the modal
 */
export default function WalkthroughModal({ walkthrough, onClose }) {
  const { idToken } = useContext(AuthContext);
  const [saved, setSaved]           = useState(false);
  const [shareSlug, setShareSlug]   = useState(walkthrough?.share_slug || null);
  const [saving, setSaving]         = useState(false);
  const [sharing, setSharing]       = useState(false);
  const [activeStop, setActiveStop] = useState(0);
  const [copied, setCopied]         = useState(false);

  if (!walkthrough) return null;

  const { place, era, stops = [], walkthrough_id } = walkthrough;

  // ── Save to history ──────────────────────────────────────────────────────
  const handleSave = async () => {
    if (!idToken) return;
    setSaving(true);
    try {
      await saveWalkthrough(walkthrough_id, idToken);
      setSaved(true);
    } catch (err) {
      console.error('Save failed:', err);
    } finally {
      setSaving(false);
    }
  };

  // ── Share ─────────────────────────────────────────────────────────────────
  const handleShare = async () => {
    if (!idToken) return;
    setSharing(true);
    try {
      const { share_slug } = await shareWalkthrough(walkthrough_id, idToken);
      setShareSlug(share_slug);
      const url = `${window.location.origin}/shared/${share_slug}`;
      await navigator.clipboard.writeText(url).catch(() => {});
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch (err) {
      console.error('Share failed:', err);
    } finally {
      setSharing(false);
    }
  };

  const stop = stops[activeStop];

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/80 backdrop-blur-sm animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Panel — slides up from bottom */}
      <div className="w-full max-w-5xl max-h-[92vh] overflow-hidden rounded-t-2xl border border-white/10 bg-[#0D0D0D] flex flex-col animate-slide-up shadow-2xl">

        {/* ── Header ── */}
        <div className="flex items-start justify-between px-6 pt-6 pb-4 border-b border-white/10 shrink-0">
          <div>
            <p className="font-body text-[10px] tracking-[0.3em] text-antiqueGold uppercase mb-1">{era}</p>
            <h2 className="font-heading text-2xl md:text-3xl font-bold text-white tracking-widest uppercase">{place}</h2>
          </div>
          <div className="flex items-center gap-3">
            {/* Save button */}
            {idToken && (
              <button
                onClick={handleSave}
                disabled={saved || saving}
                className={`px-4 py-2 rounded text-xs font-body tracking-[0.15em] uppercase font-semibold transition-all duration-300 ${
                  saved
                    ? 'bg-green-900/40 text-green-400 border border-green-700/50 cursor-default'
                    : 'border border-antiqueGold/50 text-antiqueGold hover:bg-antiqueGold/10'
                }`}
              >
                {saving ? 'Saving…' : saved ? '✓ Saved' : 'Save'}
              </button>
            )}
            {/* Share button */}
            {idToken && (
              <button
                onClick={handleShare}
                disabled={sharing}
                className="px-4 py-2 rounded text-xs font-body tracking-[0.15em] uppercase font-semibold border border-white/20 text-lightGray hover:border-white/40 hover:text-white transition-all duration-300"
              >
                {sharing ? 'Sharing…' : copied ? '✓ Copied!' : shareSlug ? 'Copy Link' : 'Share'}
              </button>
            )}
            {/* Close */}
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full border border-white/20 flex items-center justify-center text-lightGray hover:text-white hover:border-white/50 transition-all duration-200"
            >
              ✕
            </button>
          </div>
        </div>

        {/* ── Stop Tabs ── */}
        {stops.length > 1 && (
          <div className="flex gap-2 px-6 py-3 border-b border-white/10 overflow-x-auto shrink-0">
            {stops.map((s, i) => (
              <button
                key={i}
                onClick={() => setActiveStop(i)}
                className={`shrink-0 px-4 py-1.5 rounded text-[11px] font-body tracking-[0.15em] uppercase transition-all duration-200 ${
                  i === activeStop
                    ? 'bg-antiqueGold/20 text-antiqueGold border border-antiqueGold/40'
                    : 'text-lightGray border border-white/10 hover:border-white/30 hover:text-white'
                }`}
              >
                Stop {i + 1}
              </button>
            ))}
          </div>
        )}

        {/* ── Stop Content ── */}
        <div className="flex-1 overflow-y-auto">
          {stop && (
            <div key={activeStop} className="animate-fade-in grid grid-cols-1 md:grid-cols-2 gap-0">

              {/* Left: Image */}
              <div className="relative bg-black min-h-[260px] md:min-h-full">
                {stop.image_url ? (
                  <img
                    src={stop.image_url}
                    alt={stop.stop_name}
                    className="absolute inset-0 w-full h-full object-cover opacity-90"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-4xl mb-3 opacity-30">🏛</div>
                      <p className="font-body text-xs text-lightGray/50 tracking-widest uppercase">Image generating…</p>
                    </div>
                  </div>
                )}
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[#0D0D0D] hidden md:block" />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0D0D0D] to-transparent md:hidden" />
              </div>

              {/* Right: Narration */}
              <div className="p-6 md:p-8 flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-4">
                  <span className="h-[1px] w-8 bg-antiqueGold/60" />
                  <span className="font-body text-[10px] tracking-[0.25em] text-antiqueGold uppercase">
                    Stop {activeStop + 1} of {stops.length}
                  </span>
                </div>
                <h3 className="font-heading text-xl md:text-2xl font-bold text-white tracking-wider mb-4">
                  {stop.stop_name}
                </h3>
                <p className="font-body text-sm md:text-base text-lightGray leading-relaxed font-light mb-6">
                  {stop.narration_script}
                </p>

                {/* Daily Facts */}
                {stop.daily_life_facts && stop.daily_life_facts.length > 0 && (
                  <div className="p-4 rounded-lg bg-white/5 border border-white/10 mt-auto">
                    <h4 className="font-body text-[10px] tracking-[0.2em] text-antiqueGold uppercase mb-2">
                      Did You Know?
                    </h4>
                    <ul className="list-none space-y-2">
                      {stop.daily_life_facts.map((fact, idx) => (
                        <li key={idx} className="font-body text-xs md:text-sm text-lightGray/90 flex gap-2 items-start">
                          <span className="text-antiqueGold opacity-70 mt-0.5">•</span>
                          <span>{fact}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Navigate stops */}
                {stops.length > 1 && (
                  <div className="flex items-center gap-4 mt-8">
                    <button
                      onClick={() => setActiveStop((p) => Math.max(0, p - 1))}
                      disabled={activeStop === 0}
                      className="w-10 h-10 rounded-full border border-white/15 hover:border-antiqueGold flex items-center justify-center text-lightGray hover:text-antiqueGold transition-all duration-200 disabled:opacity-30 disabled:cursor-default"
                    >←</button>
                    <span className="font-body text-[10px] text-lightGray/60 tracking-widest">
                      {activeStop + 1} / {stops.length}
                    </span>
                    <button
                      onClick={() => setActiveStop((p) => Math.min(stops.length - 1, p + 1))}
                      disabled={activeStop === stops.length - 1}
                      className="w-10 h-10 rounded-full border border-white/15 hover:border-antiqueGold flex items-center justify-center text-lightGray hover:text-antiqueGold transition-all duration-200 disabled:opacity-30 disabled:cursor-default"
                    >→</button>
                  </div>
                )}
              </div>

            </div>
          )}
        </div>

      </div>
    </div>
  );
}
