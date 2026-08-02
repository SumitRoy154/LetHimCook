import { motion } from "framer-motion";
import { useState, useEffect } from "react";

/**
 * Section 5 — COOKING
 * Cinematic cooking steps timeline
 * Grand Hotel display + Lato body fonts
 */

interface SectionCookingProps {
  isActive: boolean;
  steps: {
    emoji: string;
    text: string;
  }[];
}

function createSeededRandom(seed: number) {
  let value = seed;

  return () => {
    value = (value * 1664525 + 1013904223) % 4294967296;
    return value / 4294967296;
  };
}

export default function SectionCooking({ isActive, steps }: SectionCookingProps) {
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const steamParticles = Array.from({ length: 15 }, (_, index) => {
    const random = createSeededRandom(5200 + index);

    return {
      width: 2 + random() * 2,
      height: 2 + random() * 2,
      left: 30 + random() * 40,
      bottom: 10 + random() * 20,
      rise: 120 + random() * 180,
      duration: 4 + random() * 3,
      delay: random() * 4,
    };
  });

  useEffect(() => {
    if (!isActive) return;
    
    setCompletedSteps([]);
    setCurrentStep(0);
    setProgress(0);

    const timers: NodeJS.Timeout[] = [];
    steps.forEach((_, idx) => {
      timers.push(setTimeout(() => {
        setCurrentStep(idx);
        setProgress(Math.round(((idx) / steps.length) * 100));
      }, idx * 1200 + 300));
      
      timers.push(setTimeout(() => {
        setCompletedSteps((prev) => {
          if (!prev.includes(idx)) return [...prev, idx];
          return prev;
        });
      }, idx * 1200 + 1000));
    });

    timers.push(setTimeout(() => setProgress(100), steps.length * 1200 + 500));

    return () => timers.forEach(clearTimeout);
  }, [isActive]);

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0">
        <img
          src="/manus-storage/cooking-steps_103b66e6.png"
          alt=""
          className="w-full h-full object-cover opacity-12"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-orange-950/10 to-[#0a0a0a]" />
      </div>

      {/* Orange glow */}
      <motion.div
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 5, repeat: Infinity }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-orange-500/[0.04] blur-[200px]"
      />

      {/* Steam particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {steamParticles.map((particle, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: `${particle.width}px`,
              height: `${particle.height}px`,
              left: `${particle.left}%`,
              bottom: `${particle.bottom}%`,
              background: "rgba(255,255,255,0.04)",
            }}
            animate={{
              y: [0, -particle.rise],
              opacity: [0, 0.2, 0],
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
      <div className="relative z-10 w-full max-w-3xl mx-auto">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-orange-400 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          AI Chef at Work
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-8"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 6vw, 4rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">The </span>
          <span className="text-gradient-warm">Cooking</span>
        </motion.h2>

        {/* Progress & Stats */}
        <div className="flex items-center gap-5 mb-8">
          <div className="relative w-16 h-16">
            <svg className="w-16 h-16 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
              <motion.circle
                cx="40" cy="40" r="34" fill="none"
                stroke="url(#orangeGrad)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={213.6}
                initial={{ strokeDashoffset: 213.6 }}
                animate={{ strokeDashoffset: 213.6 * (1 - progress / 100) }}
                transition={{ duration: 0.8 }}
              />
              <defs>
                <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#F97316" />
                  <stop offset="100%" stopColor="#FBBF24" />
                </linearGradient>
              </defs>
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-white font-bold text-sm font-body">{progress}%</span>
          </div>
          <div>
            <p className="text-white text-sm font-bold font-body">Cooking In Progress</p>
            <p className="text-gray-500 text-xs font-mono">{completedSteps.length}/{steps.length} steps complete</p>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-2">
          {steps.map((step, idx) => {
            const isCompleted = completedSteps.includes(idx);
            const isCurrent = idx === currentStep && !isCompleted;
            
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0.3 }}
                animate={{ 
                  opacity: isCompleted || isCurrent ? 1 : 0.3,
                }}
                transition={{ duration: 0.4 }}
                className={`glass px-4 py-3 flex items-center gap-4 ${
                  isCurrent ? "border-orange-400/20 glow-orange" : ""
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  isCompleted 
                    ? "bg-emerald-400/20" 
                    : isCurrent 
                      ? "bg-orange-400/20 animate-pulse" 
                      : "bg-white/5"
                }`}>
                  {isCompleted ? (
                    <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-sm">{step.emoji}</span>
                  )}
                </div>
                <span className={`text-sm font-body ${
                  isCompleted ? "text-emerald-400" : isCurrent ? "text-white" : "text-gray-600"
                }`}>
                  {step.text}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
