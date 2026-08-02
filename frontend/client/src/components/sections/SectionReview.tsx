import { motion } from "framer-motion";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";

/**
 * Section 8 — AI REVIEW
 * Premium review dashboard
 * Grand Hotel display + Lato body fonts
 */

interface SectionReviewProps {
  isActive: boolean;
  walletUpdate: number;
}

const radarData = [
  { category: "Taste", score: 9.5, fullMark: 10 },
  { category: "Presentation", score: 9.0, fullMark: 10 },
  { category: "Texture", score: 9.8, fullMark: 10 },
  { category: "Timing", score: 9.2, fullMark: 10 },
  { category: "Creativity", score: 9.5, fullMark: 10 },
];

const categoryCards = [
  { name: "Taste", score: 9.5, comment: "Perfect balance of spices", positive: true },
  { name: "Presentation", score: 9.0, comment: "Beautiful plating", positive: true },
  { name: "Texture", score: 9.8, comment: "Ideal firmness", positive: true },
  { name: "Timing", score: 9.2, comment: "Slightly over", positive: false },
  { name: "Creativity", score: 9.5, comment: "Innovative spice blend", positive: true },
];

export default function SectionReview({ isActive, walletUpdate }: SectionReviewProps) {
  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-emerald-950/8 to-[#0a0a0a]" />

      {/* Content */}
      <div className="relative z-10 w-full max-w-3xl mx-auto">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-emerald-400 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          Judge AI Assessment
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-8"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 6vw, 3.5rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">Judge's </span>
          <span className="text-emerald-400">Review</span>
        </motion.h2>

        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Score & Radar */}
          <div className="flex-1 w-full">
            {/* Large Score */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, type: "spring", bounce: 0.3 }}
              className="text-center mb-6"
            >
              <p className="text-6xl md:text-7xl font-bold text-gradient-lime font-body" style={{ fontFamily: "'Lato', sans-serif", fontWeight: 900 }}>
                9.8
              </p>
              <p className="text-gray-500 text-sm font-body">/ 10</p>
            </motion.div>

            {/* Radar Chart */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="w-full h-52"
            >
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="70%">
                  <PolarGrid stroke="rgba(255,255,255,0.06)" />
                  <PolarAngleAxis dataKey="category" tick={{ fill: "#6B7280", fontSize: 11, fontFamily: "'Lato', sans-serif" }} />
                  <PolarRadiusAxis tick={false} axisLine={false} />
                  <Radar
                    name="Score"
                    dataKey="score"
                    stroke="#A3E635"
                    fill="#A3E635"
                    fillOpacity={0.15}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          {/* Category Cards */}
          <div className="flex-1 w-full space-y-2">
            {categoryCards.map((card, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 + idx * 0.08, duration: 0.35 }}
                className="glass px-4 py-3"
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-white text-sm font-body">{card.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-gray-300">{card.score}</span>
                    <span className={`text-[10px] ${card.positive ? "text-emerald-400" : "text-amber-400"}`}>
                      {card.positive ? "✓" : "→"}
                    </span>
                  </div>
                </div>
                <p className={`text-[11px] ${card.positive ? "text-emerald-400/60" : "text-amber-400/60"} font-body`}>
                  {card.comment}
                </p>
              </motion.div>
            ))}

            {/* Reward */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.7 }}
              className="glass px-4 py-3 glow-lime"
            >
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm font-body">Reward</span>
                <motion.span
                  initial={{ scale: 1.2 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.8, type: "spring" }}
                  className="text-lime-400 font-bold font-mono text-base"
                >
                  +₹{walletUpdate}
                </motion.span>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
