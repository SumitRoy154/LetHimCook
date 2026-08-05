import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { DishOption } from "@/services/recipe";

interface DishSuggestionModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  suggestions: DishOption[];
  onSelectDish: (dishName: string) => void;
  onTryAgain: () => void;
  isLoading?: boolean;
}

export default function DishSuggestionModal({
  open,
  onOpenChange,
  suggestions,
  onSelectDish,
  onTryAgain,
  isLoading,
}: DishSuggestionModalProps) {
  if (!open) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative w-full max-w-lg glass-strong p-6 md:p-8 rounded-3xl border border-white/10 shadow-2xl overflow-hidden font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          {/* Ambient Header Glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-lime-400 to-transparent" />

          <div className="flex items-center justify-between mb-6">
            <div>
              <span className="text-[10px] text-lime-400 font-mono uppercase tracking-widest font-bold">AI Culinary Recommendations</span>
              <h2 className="text-xl md:text-2xl font-bold text-white mt-1">Suggested Dishes</h2>
            </div>
            <button
              type="button"
              onClick={() => onOpenChange(false)}
              className="w-8 h-8 rounded-full glass flex items-center justify-center text-gray-400 hover:text-white transition-colors text-sm font-bold"
            >
              ✕
            </button>
          </div>

          <p className="text-gray-300 text-xs mb-6">
            Based on your craving, Groq AI analyzed our kitchen database and prepared these dish suggestions for you:
          </p>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-lime-400 border-t-transparent animate-spin" />
              <p className="text-xs text-lime-400 font-mono">Analyzing craving & matching recipes...</p>
            </div>
          ) : (
            <div className="flex flex-col gap-3 mb-6">
              {suggestions.map((option, idx) => (
                <motion.button
                  key={option.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  type="button"
                  onClick={() => {
                    onSelectDish(option.name);
                    onOpenChange(false);
                  }}
                  className="w-full text-left glass hover:bg-lime-400/10 hover:border-lime-400/50 border border-white/10 p-4 rounded-2xl transition-all flex items-start gap-3.5 group cursor-pointer"
                >
                  <span className="text-2xl p-2 rounded-xl bg-white/5 group-hover:scale-110 transition-transform">
                    {option.emoji || "🍲"}
                  </span>
                  <div className="flex-1">
                    <h3 className="text-sm font-bold text-white group-hover:text-lime-400 transition-colors">
                      {option.name}
                    </h3>
                    <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">
                      {option.description}
                    </p>
                  </div>
                </motion.button>
              ))}
            </div>
          )}

          {/* Action Footer */}
          <div className="pt-4 border-t border-white/10 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => {
                onTryAgain();
                onOpenChange(false);
              }}
              className="flex-1 py-3 rounded-xl glass hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white font-bold text-xs transition-colors"
            >
              🔄 None of the above (Try Again)
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
