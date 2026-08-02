import { motion } from "framer-motion";

/**
 * Section 6 — LIVE AI THINKING
 * Dark AI neural network background
 * Grand Hotel display + Lato body fonts
 */

interface SectionAIThinkingProps {
  isActive: boolean;
}

const thinkingBubbles = [
  "Optimizing spice ratios...",
  "Balancing temperature...",
  "Adjusting cooking time...",
  "Enhancing flavor profile...",
];

const codeSnippets = [
  "optimize_recipe()",
  "balance_taste(0.85)",
  "temp.adjust(180°C)",
  "timing.optimize()",
];

export default function SectionAIThinking({ isActive }: SectionAIThinkingProps) {
  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-blue-950/10 to-[#0a0a0a]" />
      
      {/* AI neural background */}
      <img
        src="/manus-storage/ai-neural_dbd1dc0a.png"
        alt=""
        className="absolute inset-0 w-full h-full object-cover opacity-20"
      />

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: Math.random() > 0.5 ? "#3B82F6" : "#8B5CF6",
            }}
            animate={{
              opacity: [0, 0.5, 0],
              scale: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 3,
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
          className="text-blue-400 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          Neural Processing Active
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
          className="mb-10"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 6vw, 4rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">AI Is </span>
          <span className="text-gradient-blue">Thinking</span>
        </motion.h2>

        <div className="grid md:grid-cols-2 gap-4">
          {/* Thinking bubbles */}
          <div className="space-y-2">
            {thinkingBubbles.map((bubble, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -15 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1, duration: 0.4 }}
                className="glass px-4 py-3 flex items-center gap-3"
              >
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse flex-shrink-0" />
                <span className="text-gray-300 text-xs font-body">{bubble}</span>
              </motion.div>
            ))}
          </div>

          {/* Code snippets */}
          <div className="space-y-2">
            {codeSnippets.map((snippet, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: 15 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 + idx * 0.1, duration: 0.4 }}
                className="glass px-4 py-3 flex items-center gap-3 border-l-2 border-l-purple-400/30"
              >
                <span className="text-purple-400 text-xs font-mono">{'>'}</span>
                <span className="text-purple-300 text-xs font-mono">{snippet}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Pulsing indicator */}
        <motion.div
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="mt-8 flex items-center justify-center gap-2"
        >
          <div className="w-2 h-2 rounded-full bg-blue-400" />
          <span className="text-blue-400/50 text-xs font-mono tracking-wider">PROCESSING...</span>
          <div className="w-2 h-2 rounded-full bg-purple-400" />
        </motion.div>
      </div>
    </section>
  );
}
