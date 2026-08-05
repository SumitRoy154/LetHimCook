import { motion } from "framer-motion";

interface ProgressIndicatorProps {
  currentStage: string;
  stages: string[];
  onSelectStage?: (stage: string) => void;
}

const stageLabels: Record<string, string> = {
  "intro": "Start",
  "order": "Order",
  "shopping": "Shop",
  "inventory": "Stock",
  "cooking": "Cook",
  "judge-ai": "Judge AI",
  "final-dish": "Serve",
  "next-order": "Next",
  "how-it-works": "How it Works",
};

export default function ProgressIndicator({ currentStage, stages, onSelectStage }: ProgressIndicatorProps) {
  const visibleStages = stages.filter(s => s !== "footer");
  const currentIndex = stages.indexOf(currentStage);

  return (
    <nav
      aria-label="Workflow progress navigation"
      className="fixed left-4 md:left-6 top-1/2 -translate-y-1/2 z-50 flex flex-col gap-2 pointer-events-auto"
    >
      <div className="bg-black/60 backdrop-blur-md border border-white/10 p-2.5 rounded-2xl shadow-2xl flex flex-col gap-1.5 min-w-[130px]">
        {visibleStages.map((stage, idx) => {
          const isActive = stage === currentStage;
          const isPast = idx < currentIndex;
          const label = stageLabels[stage] || stage;

          return (
            <button
              key={stage}
              type="button"
              onClick={() => onSelectStage?.(stage)}
              className="flex items-center gap-2.5 px-2 py-1 rounded-lg transition-all cursor-pointer group text-left w-full hover:bg-white/5"
            >
              {/* Animated Dot Indicator */}
              <div className="relative flex items-center justify-center w-3 h-3">
                <motion.div
                  animate={{
                    scale: isActive ? 1.25 : 1,
                    backgroundColor: isActive ? "#A3E635" : isPast ? "rgba(163, 230, 53, 0.6)" : "rgba(255,255,255,0.25)",
                    boxShadow: isActive ? "0 0 10px rgba(163,230,53,0.8)" : "0 0 0px rgba(0,0,0,0)",
                  }}
                  transition={{ duration: 0.2 }}
                  className="w-2.5 h-2.5 rounded-full"
                />
                {isActive && (
                  <motion.div
                    layoutId="activeDotRing"
                    className="absolute inset-0 rounded-full border border-lime-400"
                    transition={{ type: "spring", stiffness: 300, damping: 25 }}
                  />
                )}
              </div>

              {/* Permanent Text Label beside dot */}
              <span
                className={`text-xs font-medium font-body transition-colors ${
                  isActive
                    ? "text-lime-400 font-bold"
                    : isPast
                    ? "text-gray-300 group-hover:text-white"
                    : "text-gray-500 group-hover:text-gray-300"
                }`}
                style={{ fontFamily: "'Lato', sans-serif" }}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
