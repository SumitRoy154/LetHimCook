"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface SectionJudgeAIProps {
  isActive: boolean;
  dish: string;
  reviewText?: string;
  agentName?: string;
}

export default function SectionJudgeAI({
  isActive,
  dish,
  reviewText = "",
  agentName = "Gemini Pro AI Judge Agent",
}: SectionJudgeAIProps) {
  const [judgePhase, setJudgePhase] = useState<"tasting" | "thinking" | "judging" | "ready">("tasting");
  const [typedText, setTypedText] = useState("");

  const targetText = reviewText.trim() || "Evaluating flavor harmony, culinary execution, and presentation...";

  useEffect(() => {
    if (!isActive) {
      setJudgePhase("tasting");
      setTypedText("");
      return;
    }

    // 2-second evaluation phase sequence
    setJudgePhase("tasting");
    const t1 = setTimeout(() => setJudgePhase("thinking"), 700);
    const t2 = setTimeout(() => setJudgePhase("judging"), 1400);
    const t3 = setTimeout(() => setJudgePhase("ready"), 2100);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [isActive, reviewText]);

  // Typewriter animation when phase is ready
  useEffect(() => {
    if (judgePhase !== "ready") {
      setTypedText("");
      return;
    }

    let current = 0;
    const interval = setInterval(() => {
      if (current < targetText.length) {
        current++;
        setTypedText(targetText.slice(0, current));
      } else {
        clearInterval(interval);
      }
    }, 25);

    return () => clearInterval(interval);
  }, [judgePhase, targetText]);

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-emerald-950/6 to-[#0a0a0a]" />

      {/* Emerald glow */}
      <motion.div
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 6, repeat: Infinity }}
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-emerald-500/[0.04] blur-[200px]"
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-2xl mx-auto text-center">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-emerald-400 text-xs font-medium tracking-[0.4em] uppercase mb-4 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          Culinary Evaluation
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-8"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2.2rem, 6vw, 4rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">AI Culinary </span>
          <span className="text-gradient-lime">Assessment</span>
        </motion.h2>

        {/* Gemini AI Assessment Glass Review Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="glass-strong p-8 rounded-2xl border border-white/10 text-left shadow-2xl relative overflow-hidden min-h-[220px]"
        >
          <div className="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-lime-400 to-emerald-500 flex items-center justify-center text-black font-bold text-lg shadow-lg">
              🤖
            </div>
            <div>
              <h3 className="text-white text-base font-bold font-body">{agentName}</h3>
              <p className="text-emerald-400 text-[11px] font-mono uppercase tracking-wider">
                Evaluation for {dish || "Order"}
              </p>
            </div>
          </div>

          {judgePhase !== "ready" ? (
            /* 2-Second Tasting / Thinking / Judging Pause State */
            <div className="py-8 flex flex-col items-center justify-center gap-3">
              <motion.div
                animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-3xl"
              >
                🧠
              </motion.div>
              <p className="text-amber-400 font-mono text-sm uppercase tracking-widest font-bold capitalize animate-pulse">
                {judgePhase}...
              </p>
            </div>
          ) : (
            /* Typing Animation Review Output */
            <blockquote className="text-gray-200 text-base md:text-lg font-body leading-relaxed italic relative z-10">
              "{typedText}"
              <span className="inline-block w-2 h-5 ml-1 bg-lime-400 animate-pulse align-middle" />
            </blockquote>
          )}
        </motion.div>

        {/* Status indicator */}
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="mt-6 flex items-center justify-center gap-2"
        >
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span className="text-emerald-400 text-[10px] font-mono tracking-wider uppercase font-bold">
            {judgePhase === "ready" ? "Assessment Complete" : `${judgePhase.toUpperCase()} DISH IN PROGRESS`}
          </span>
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </motion.div>
      </div>
    </section>
  );
}
