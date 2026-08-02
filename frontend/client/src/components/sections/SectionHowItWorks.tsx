"use client";

import { motion } from "framer-motion";

const architectureSteps = [
  {
    num: "01",
    name: "User Request & JWT Auth",
    tech: "Next.js 15 • React 19 • Axios • Zustand",
    desc: "User submits dish request authenticated with JWT bearer token and validated via React Hook Form & Zod.",
    color: "text-amber-400",
  },
  {
    num: "02",
    name: "FastAPI REST Gateway",
    tech: "FastAPI • Pydantic v2 • SQLAlchemy • Alembic",
    desc: "FastAPI receives request, validates schemas, verifies DB session, and initializes order record.",
    color: "text-orange-400",
  },
  {
    num: "03",
    name: "Planner Node (OpenAI GPT-4o)",
    tech: "LangGraph StateGraph • OpenAI API",
    desc: "Planner Agent generates structured recipe JSON, ingredient list, and estimated costs or pulls from Recipe Cache.",
    color: "text-lime-400",
  },
  {
    num: "04",
    name: "Inventory Engine & Market",
    tech: "MySQL Database • Transaction Service",
    desc: "Checks pantry staples (salt, water, spices, oil). Purchases missing items, debits wallet balance, and updates inventory.",
    color: "text-emerald-400",
  },
  {
    num: "05",
    name: "Cooking Agent (Claude 3.5)",
    tech: "Anthropic Claude SDK • Multi-Step Execution",
    desc: "Simulates step-by-step culinary execution, heat control, and state progress monitoring.",
    color: "text-teal-400",
  },
  {
    num: "06",
    name: "Judge Agent & Reward Engine (Gemini Pro)",
    tech: "Google Gemini GenAI SDK • Wallet Engine",
    desc: "Evaluates dish quality, writes qualitative critique, and credits bonus coin reward to user's wallet.",
    color: "text-cyan-400",
  },
  {
    num: "07",
    name: "Persistence Node & Live Updates",
    tech: "TanStack React Query • MySQL Workflow Logging",
    desc: "Saves complete state snapshot and execution logs to workflow_executions; invalidates React Query cache for live frontend sync.",
    color: "text-blue-400",
  },
];

export default function SectionHowItWorks() {
  return (
    <section className="relative w-full min-h-screen flex items-center justify-center py-20 px-6">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-[#0a0a0a] to-[#0a0a0a]" />

      {/* Content */}
      <div className="relative z-10 w-full max-w-3xl mx-auto">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-gray-500 text-xs font-medium tracking-[0.3em] uppercase mb-3 font-body text-center"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          System Architecture
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mb-8 text-center"
          style={{ fontFamily: "'Grand Hotel', cursive", fontSize: "clamp(2.2rem, 6vw, 4rem)", lineHeight: 1.1 }}
        >
          <span className="text-white/90">How It </span>
          <span className="text-gradient-lime">Works</span>
        </motion.h2>

        {/* Architecture Flow List */}
        <div className="space-y-3.5">
          {architectureSteps.map((step, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.08, duration: 0.4 }}
              className="glass p-5 rounded-xl border border-white/10 flex items-start gap-4 hover:border-white/20 transition-colors"
            >
              <span className={`${step.color} text-lg font-mono font-bold flex-shrink-0 pt-0.5`}>{step.num}</span>
              <div className="flex-1">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                  <h4 className="text-white text-base font-bold font-body">{step.name}</h4>
                  <span className="text-[10px] font-mono text-lime-400/80 bg-lime-400/10 px-2.5 py-0.5 rounded border border-lime-400/20">
                    {step.tech}
                  </span>
                </div>
                <p className="text-gray-400 text-xs font-body leading-relaxed">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
