"use client";

import { motion } from "framer-motion";

interface SectionInventoryProps {
  isActive: boolean;
  items: {
    name: string;
    emoji?: string;
    status: string;
  }[];
}

export default function SectionInventory({ isActive, items }: SectionInventoryProps) {
  const purchasedCount = items.filter((i) => i.status === "Purchased").length;
  const availableCount = items.filter((i) => i.status !== "Purchased").length;

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0">
        <img
          src="/manus-storage/pantry-shelves_8b3c1f6d.png"
          alt=""
          className="w-full h-full object-cover opacity-12"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-emerald-950/10 to-[#0a0a0a]" />
      </div>

      {/* Emerald glow */}
      <motion.div
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 6, repeat: Infinity }}
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-emerald-500/[0.04] blur-[200px]"
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-3xl mx-auto text-center">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-emerald-400 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          Inventory Management
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-10 text-center"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2.5rem, 6vw, 4.5rem)", lineHeight: 1.1 }}
        >
          <span className="text-gradient-emerald">Inventory</span>
        </motion.h2>

        {items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-strong p-8 rounded-2xl border border-white/10 text-center max-w-md mx-auto"
          >
            <p className="text-gray-400 text-sm font-body">Awaiting order ingredients...</p>
          </motion.div>
        ) : (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-3"
            >
              {items.map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 25, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ delay: idx * 0.25 + 0.3, duration: 0.4 }}
                  className="glass px-4 py-4 text-center rounded-xl border border-emerald-400/20 shadow-lg"
                >
                  <p className="text-white text-sm font-bold font-body">{item.name}</p>
                  <p className="text-emerald-400 text-[11px] font-mono mt-1 font-semibold">{item.status}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* We Are Ready !! Summary */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: items.length * 0.25 + 0.5 }}
              className="mt-8 inline-block glass-strong px-8 py-3 rounded-full border border-emerald-400/40 shadow-[0_0_20px_rgba(52,211,153,0.3)]"
            >
              <p className="text-emerald-400 font-bold text-base font-body tracking-wide">
                We are ready !!
              </p>
              <p className="text-gray-400 text-xs font-mono mt-0.5">
                {purchasedCount} Purchased • {availableCount} Available in Pantry
              </p>
            </motion.div>
          </>
        )}
      </div>
    </section>
  );
}
