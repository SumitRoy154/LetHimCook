"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

interface SectionIntroProps {
  isActive: boolean;
  coins: number;
  onStart: (dishName: string) => void;
  currentDish?: string;
  isLoading?: boolean;
}

const subtitles = ["Planning...", "Thinking...", "Preparing..."];

const dishSuggestions = [
  "Paneer Butter Masala",
  "Masala Dosa",
  "Chicken Biryani",
  "Butter Chicken",
  "Pasta Carbonara",
  "Veg Fried Rice",
];

function createSeededRandom(seed: number) {
  let value = seed;
  return () => {
    value = (value * 1664525 + 1013904223) % 4294967296;
    return value / 4294967296;
  };
}

export default function SectionIntro({
  isActive,
  coins,
  onStart,
  currentDish = "",
  isLoading = false,
}: SectionIntroProps) {
  const [dishInput, setDishInput] = useState("");
  const [subtitleIndex, setSubtitleIndex] = useState(0);
  const [started, setStarted] = useState(false);

  const particles = Array.from({ length: 20 }, (_, index) => {
    const random = createSeededRandom(1440 + index);
    return {
      width: 1 + random() * 1.5,
      height: 1 + random() * 1.5,
      left: random() * 100,
      top: random() * 100,
      alpha: 0.1 + random() * 0.15,
      rise: 80 + random() * 120,
      delay: random() * 5,
      duration: 5 + random() * 6,
    };
  });

  useEffect(() => {
    if (started) return;
    const interval = setInterval(() => {
      setSubtitleIndex((prev) => (prev + 1) % subtitles.length);
    }, 1800);
    return () => clearInterval(interval);
  }, [started]);

  const handleStart = (e?: React.FormEvent) => {
    e?.preventDefault();
    const targetDish = dishInput.trim();
    if (!targetDish || isLoading) return;
    setStarted(true);
    onStart(targetDish);
  };

  const handleSuggestionClick = (dish: string) => {
    setDishInput(dish);
  };

  const isValidInput = dishInput.trim().length >= 2;
  const isTyping = dishInput.trim().length > 0;

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0">
        <img
          src="/manus-storage/hero-kitchen_ab27f3bf.png"
          alt=""
          className="w-full h-full object-cover opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a]/50 via-[#0a0a0a]/80 to-[#0a0a0a]" />
      </div>

      {/* Ambient glow */}
      <motion.div
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 6, repeat: Infinity }}
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-amber-500/[0.04] blur-[200px]"
      />

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {particles.map((particle, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: `${particle.width}px`,
              height: `${particle.height}px`,
              left: `${particle.left}%`,
              top: `${particle.top}%`,
              background: `rgba(163, 230, 53, ${particle.alpha})`,
            }}
            animate={{
              y: [0, -particle.rise],
              opacity: [0, 0.4, 0],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 text-center max-w-2xl mx-auto">
        {/* Main Title */}
        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.23, 1, 0.32, 1] }}
          className="mb-3"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2.8rem, 8vw, 6rem)", lineHeight: 1 }}
        >
          <span className="text-white/90">Let Him</span>
          <br />
          <span className="text-gradient-lime">Cook.</span>
        </motion.h1>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-gray-400 text-sm md:text-base max-w-xl mx-auto mb-4 leading-relaxed font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          An AI-powered autonomous kitchen where intelligent agents plan, shop, cook, judge, and reward every meal.
        </motion.p>

        {/* Animated Subtitle */}
        <div className="h-5 mb-6 flex items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={subtitleIndex}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.35 }}
              className="text-xs font-medium tracking-[0.4em] uppercase text-lime-400/70 font-mono"
              style={{ fontFamily: "'Lato', sans-serif" }}
            >
              {subtitles[subtitleIndex]}
            </motion.p>
          </AnimatePresence>
        </div>

        {/* Interactive Order Input Card */}
        <motion.form
          onSubmit={handleStart}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="glass-strong max-w-md mx-auto mb-6 px-6 py-5 rounded-2xl border border-white/10 text-left shadow-2xl"
        >
          <div className="flex items-center justify-between mb-3">
            <p className="text-[10px] text-gray-400 uppercase tracking-[0.2em] font-body font-semibold">What are we cooking today?</p>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] text-emerald-400 font-mono font-bold">Kitchen Ready</span>
            </div>
          </div>

          <div className="relative mb-4">
            <input
              type="text"
              value={dishInput}
              onChange={(e) => setDishInput(e.target.value)}
              placeholder="e.g. Paneer Butter Masala, Egg Roll, Masala Dosa..."
              className="w-full bg-black/50 border border-white/15 focus:border-lime-400 rounded-xl px-4 py-3 text-base font-body text-white placeholder:text-gray-600 outline-none transition-all shadow-inner"
              style={{ fontFamily: "'Lato', sans-serif" }}
            />
          </div>

          {/* Quick Suggestions */}
          <div className="mb-4">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2 font-body">Quick Suggestions:</p>
            <div className="flex flex-wrap gap-1.5">
              {dishSuggestions.map((dish) => (
                <button
                  key={dish}
                  type="button"
                  onClick={() => handleSuggestionClick(dish)}
                  className={`text-xs px-2.5 py-1 rounded-lg border transition-all font-body ${
                    dishInput === dish
                      ? "bg-lime-400/20 border-lime-400 text-lime-300 font-semibold"
                      : "bg-white/5 border-white/10 text-gray-400 hover:text-white hover:border-white/30"
                  }`}
                  style={{ fontFamily: "'Lato', sans-serif" }}
                >
                  {dish}
                </button>
              ))}
            </div>
          </div>

          {/* Start Cooking Button */}
          <button
            type="submit"
            disabled={!isValidInput || isLoading}
            className={`w-full py-3.5 rounded-xl text-black font-bold text-base tracking-wide font-body transition-all flex items-center justify-center gap-2 ${
              !isValidInput || isLoading
                ? "bg-gray-600 opacity-40 cursor-not-allowed"
                : isValidInput
                  ? "bg-gradient-to-r from-lime-400 to-emerald-400 shadow-[0_0_30px_rgba(163,230,53,0.6)] animate-pulse hover:scale-[1.02] active:scale-[0.98]"
                  : isTyping
                    ? "bg-gradient-to-r from-lime-400 to-emerald-400 opacity-80 shadow-[0_0_15px_rgba(163,230,53,0.3)]"
                    : "bg-lime-400"
            }`}
            style={{ fontFamily: "'Lato', sans-serif" }}
          >
            {isLoading ? (
              <>
                <svg className="w-5 h-5 animate-spin text-black" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span>Dispatching AI Agents...</span>
              </>
            ) : (
              <span>Start Cooking</span>
            )}
          </button>
        </motion.form>
      </div>
    </section>
  );
}
