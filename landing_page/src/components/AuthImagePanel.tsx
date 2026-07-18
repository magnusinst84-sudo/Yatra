import mainImg from '../data/images_re/main.jpeg';

export const AuthImagePanel = () => {
  return (
    <div className="relative w-full h-[320px] sm:h-[420px] lg:h-full min-h-[400px] lg:min-h-[580px] rounded-[30px] overflow-hidden border border-white/5 shadow-2xl">
      {/* 1. Large Premium Rounded Image Container */}
      <div className="absolute inset-0 w-full h-full rounded-[30px] overflow-hidden bg-[#101015]">
        <img
          src={mainImg}
          alt="Explore History"
          className="w-full h-full object-cover transition-transform duration-[2000ms] hover:scale-105"
        />
        {/* Decorative Luxury Lines */}
        <div className="absolute inset-0 border border-gold/10 m-5 rounded-[22px] pointer-events-none z-10" />
      </div>

      {/* 2. Bottom Overlay Gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent pointer-events-none z-[1]" />

      {/* 3. Text Overlay Content */}
      <div className="absolute bottom-0 left-0 right-0 p-8 sm:p-10 flex flex-col gap-4 text-left z-10 select-none">
        <div className="flex flex-col gap-1.5">
          {/* Main Title */}
          <h2 className="font-serif text-3xl sm:text-4xl font-extrabold text-white tracking-wide leading-tight">
            Explore History
          </h2>
          {/* Subtitle */}
          <p className="font-sans text-sm font-light text-gray-300 tracking-wide max-w-sm">
            Begin your journey through India's timeless heritage and explore the sacred chronicles of Yatra.
          </p>
        </div>

        {/* Slider Dots */}
        <div className="flex items-center gap-2 mt-2">
          <span className="w-6 h-1 rounded-full bg-gold transition-all duration-300" />
          <span className="w-1.5 h-1.5 rounded-full bg-white/20 transition-all duration-300 hover:bg-white/40" />
          <span className="w-1.5 h-1.5 rounded-full bg-white/20 transition-all duration-300 hover:bg-white/40" />
        </div>
      </div>
    </div>
  );
};
