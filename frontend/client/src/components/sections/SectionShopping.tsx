"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface SectionShoppingProps {
  isActive: boolean;
  ingredients: {
    name: string;
    qty: string;
    price: string;
    icon?: string;
  }[];
  total: number;
}

export default function SectionShopping({ isActive, ingredients, total }: SectionShoppingProps) {
  const [checkedItems, setCheckedItems] = useState<number[]>([]);
  const [showReceipt, setShowReceipt] = useState(false);

  useEffect(() => {
    if (!isActive || ingredients.length === 0) {
      setCheckedItems([]);
      setShowReceipt(false);
      return;
    }
    
    ingredients.forEach((_, idx) => {
      const timer = setTimeout(() => {
        setCheckedItems((prev) => {
          if (prev.includes(idx)) return prev;
          return [...prev, idx];
        });
      }, (idx + 1) * 700);
      return () => clearTimeout(timer);
    });
    
    const receiptTimer = setTimeout(() => setShowReceipt(true), ingredients.length * 700 + 400);
    return () => clearTimeout(receiptTimer);
  }, [isActive, ingredients]);

  const hasShoppingNeeded = ingredients.length > 0 && total > 0;

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0">
        <img
          src="/manus-storage/grocery-market_f5c7e677.png"
          alt=""
          className="w-full h-full object-cover opacity-12"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-amber-950/10 to-[#0a0a0a]" />
      </div>

      {/* Warm glow */}
      <motion.div
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 6, repeat: Infinity }}
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-amber-500/[0.04] blur-[200px]"
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-3xl mx-auto">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-amber-400 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          AI Shopping Agent
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-10"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2rem, 6vw, 4rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">Grocery </span>
          <span className="text-gradient-orange">Shopping</span>
        </motion.h2>

        {!hasShoppingNeeded ? (
          /* Empty / Standby Shopping Cart State */
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-strong p-10 rounded-2xl border border-white/10 text-center max-w-md mx-auto shadow-2xl"
          >
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="w-16 h-16 rounded-full bg-amber-400/10 text-amber-400 flex items-center justify-center mx-auto mb-4 text-3xl border border-amber-400/20 shadow-[0_0_25px_rgba(251,191,36,0.2)]"
            >
              🛒
            </motion.div>
            <h3 className="text-xl font-bold text-white mb-2 font-body" style={{ fontFamily: "'Lato', sans-serif" }}>
              {ingredients.length > 0 && total === 0 ? "All Ingredients Available" : "Awaiting Shopping List..."}
            </h3>
            <p className="text-gray-400 text-xs font-body leading-relaxed">
              {ingredients.length > 0 && total === 0
                ? "Checked user inventory & pantry staples. Everything needed for this dish is already in stock!"
                : "Select a dish above to generate a smart market list for missing ingredients."}
            </p>
          </motion.div>
        ) : (
          <div className="grid md:grid-cols-5 gap-8 items-start">
            {/* Ingredient Checklist without item emojis */}
            <div className="md:col-span-3 space-y-2">
              {ingredients.map((item, idx) => {
                const isChecked = checkedItems.includes(idx);
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -15 }}
                    animate={{
                      opacity: isChecked ? 1 : 0.3,
                      x: 0,
                    }}
                    transition={{ duration: 0.5, delay: idx * 0.2 }}
                    className="glass px-4 py-3.5 flex items-center gap-3 rounded-xl border border-white/10"
                  >
                    <span className="text-white text-sm font-semibold flex-1 font-body">{item.name}</span>
                    <span className="text-gray-400 text-xs font-mono">{item.qty}</span>
                    <span className="text-amber-400/90 text-xs font-mono font-bold">{item.price}</span>
                    {isChecked && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-5 h-5 rounded-full bg-emerald-400/20 flex items-center justify-center flex-shrink-0"
                      >
                        <svg className="w-3 h-3 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </motion.span>
                    )}
                  </motion.div>
                );
              })}
            </div>

            {/* Receipt Panel */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="md:col-span-2 glass-strong px-5 py-5 rounded-2xl border border-white/10"
            >
              <div className="flex items-center justify-between mb-4">
                <p className="text-[10px] text-gray-500 uppercase tracking-[0.2em] font-body">Receipt</p>
                <span className="text-[10px] text-amber-400 font-mono font-bold">
                  {showReceipt ? "Complete" : "Calculating..."}
                </span>
              </div>
              <div className="border-b border-white/10 pb-3 mb-3">
                <p className="text-white text-sm font-bold font-body">Shopping List</p>
              </div>
              <div className="space-y-2 text-xs">
                {ingredients.slice(0, checkedItems.length).map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-between text-gray-300 font-body"
                  >
                    <span>{item.name}</span>
                    <span className="text-amber-400/90 font-mono">{item.price}</span>
                  </motion.div>
                ))}
              </div>
              <div className="border-t border-white/10 pt-3 mt-3 flex justify-between">
                <span className="text-white text-sm font-bold font-body">Total</span>
                <span className="text-amber-400 text-sm font-bold font-mono">₹{total}</span>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </section>
  );
}
