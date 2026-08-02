"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface SectionFinalDishProps {
  isActive: boolean;
  coinsEarned: number;
  dishName: string;
}

function createSeededRandom(seed: number) {
  let value = seed;
  return () => {
    value = (value * 1664525 + 1013904223) % 4294967296;
    return value / 4294967296;
  };
}

export default function SectionFinalDish({
  isActive,
  coinsEarned,
  dishName,
}: SectionFinalDishProps) {
  const [showDetails, setShowDetails] = useState(false);

  const steamParticles = Array.from({ length: 6 }, (_, index) => {
    const random = createSeededRandom(7100 + index);
    return {
      width: 20 + random() * 30,
      height: 20 + random() * 30,
      left: (index - 3) * 18,
      rise: 60 + random() * 40,
      duration: 3 + random() * 2,
      delay: random() * 2,
    };
  });

  const confettiPieces = Array.from({ length: 30 }, (_, index) => {
    const random = createSeededRandom(8200 + index);
    return {
      left: random() * 100,
      x: (random() - 0.5) * 200,
      duration: 2.5 + random() * 2,
      delay: random(),
      color: ["#FCD34D", "#F97316", "#A3E635", "#34D399", "#60A5FA", "#F472B6"][index % 6],
    };
  });

  useEffect(() => {
    if (isActive) {
      setShowDetails(false);
      const timer = setTimeout(() => setShowDetails(true), 1500);
      return () => clearTimeout(timer);
    }
  }, [isActive]);

  const hasDish = Boolean(dishName?.trim());

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-amber-950/8 to-[#0a0a0a]" />

      {/* Steam */}
      <div className="absolute top-[35%] left-1/2 -translate-x-1/2 pointer-events-none">
        {steamParticles.map((particle, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white/[0.03]"
            style={{
              width: `${particle.width}px`,
              height: `${particle.height}px`,
              left: `${particle.left}px`,
            }}
            animate={{
              y: [0, -particle.rise],
              opacity: [0, 0.1, 0],
              scale: [1, 1.3],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
          />
        ))}
      </div>

      {/* Confetti */}
      {showDetails && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {confettiPieces.map((piece, i) => (
            <motion.div
              key={i}
              className="absolute w-1.5 h-1.5 rounded-sm"
              style={{
                left: `${piece.left}%`,
                top: "-5px",
                background: piece.color,
              }}
              animate={{
                y: ["0vh", "100vh"],
                x: [piece.x],
                rotate: [0, 720],
                opacity: [1, 0],
              }}
              transition={{
                duration: piece.duration,
                delay: piece.delay,
              }}
            />
          ))}
        </div>
      )}

      {/* Content */}
      <div className="relative z-10 text-center max-w-lg mx-auto">
        {/* Title */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mb-3"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 5vw, 3.5rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">{hasDish ? `We cooked ${dishName} !` : "We are Cooking"}</span>
          <br />
          <span className="text-gradient-warm font-bold">{hasDish ? "Prepared Successfully" : "Waiting for the next dish"}</span>
        </motion.h2>

        {/* Reward Pill Only */}
        {showDetails && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center justify-center mt-4"
          >
            <div className="glass-strong px-8 py-4 rounded-full border border-lime-400/30 shadow-[0_0_20px_rgba(163,230,53,0.3)]">
              <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-0.5 font-body">Reward Credited</p>
              <p className="text-lime-400 font-bold text-2xl font-mono tabular-nums">+{coinsEarned} Coins Earned</p>
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
}
