"use client";

import { motion } from "framer-motion";

interface SectionOrderProps {
  isActive: boolean;
  dish?: string;
  orderId?: string | number;
  estimatedCost?: number | null;
  ingredientCount?: number | null;
  agentName?: string;
}

export default function SectionOrder({
  isActive,
  dish = "",
  orderId,
  estimatedCost = 0,
  ingredientCount = 0,
  agentName = "Planner AI (Groq - Llama 3.3 70B)",
}: SectionOrderProps) {
  const hasDish = Boolean(dish?.trim());
  const costValue = typeof estimatedCost === "number" && estimatedCost > 0 ? `₹${estimatedCost}` : "₹—";
  const ingredientValue = typeof ingredientCount === "number" && ingredientCount > 0 ? `${ingredientCount} items` : "— items";

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-amber-950/10 to-[#0a0a0a]" />

      {/* Content */}
      <div className="relative z-10 text-center max-w-lg mx-auto w-full">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-amber-400 text-xs font-medium tracking-[0.4em] uppercase mb-4 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          {hasDish ? "Order Received" : "Awaiting Order"}
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
          className="mb-10"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2.5rem, 7vw, 5rem)", lineHeight: 1.1 }}
        >
          {hasDish ? (
            <>
              <span className="text-white/90">Order </span>
              <span className="text-gradient-orange">Accepted</span>
            </>
          ) : (
            <span className="text-gray-500">Order Standby</span>
          )}
        </motion.h2>

        {/* Order Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4, duration: 0.7 }}
          className="glass-strong px-7 py-6 text-left mb-8 rounded-2xl border border-white/10 shadow-2xl"
        >
          <div className="border-b border-white/10 pb-4 mb-4 flex items-center justify-between">
            <h3 className="text-xl font-bold text-white font-body">
              {hasDish ? dish : "No Dish Selected Yet"}
            </h3>
            {hasDish && orderId && (
              <span className="text-xs font-mono text-amber-400/90 bg-amber-400/10 px-2.5 py-1 rounded-md border border-amber-400/20">
                Order #{orderId}
              </span>
            )}
          </div>
          
          <div className="space-y-3">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="flex justify-between items-center"
            >
              <span className="text-gray-400 text-sm font-body">Estimated Cost</span>
              <span className="text-white font-mono text-sm font-bold">
                {hasDish ? costValue : "₹—"}
              </span>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="flex justify-between items-center"
            >
              <span className="text-gray-400 text-sm font-body">Ingredients Required</span>
              <span className="text-white font-mono text-sm font-body">
                {hasDish ? ingredientValue : "— items"}
              </span>
            </motion.div>
          </div>

          <div className="border-t border-white/10 pt-4 mt-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm font-body">Assigned Agent</span>
              <span className="text-emerald-400 text-sm font-medium font-body">
                {hasDish ? agentName : "Agent Standby"}
              </span>
            </div>
          </div>
        </motion.div>

        {/* CONFIRMED Stamp */}
        {hasDish && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.0, type: "spring", bounce: 0.4 }}
          >
            <div className="inline-block border-2 border-emerald-400 rounded-full px-6 py-2 shadow-[0_0_20px_rgba(52,211,153,0.4)]">
              <span className="text-emerald-400 font-bold text-sm tracking-[0.15em] uppercase font-body" style={{ fontFamily: "'Lato', sans-serif" }}>
                Confirmed
              </span>
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
}
