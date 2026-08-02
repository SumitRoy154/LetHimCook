import { motion } from "framer-motion";

/**
 * Progress Indicator — Left side vertical dot navigation
 * Shows current stage in the cooking workflow
 * Lato body font
 */

interface ProgressIndicatorProps {
  currentStage: string;
  stages: string[];
}

const stageLabels: Record<string, string> = {
  "intro": "Start",
  "shopping": "Shop",
  "inventory": "Stock",
  "order": "Order",
  "cooking": "Cook",
  "judge-ai": "Ready",
  "final-dish": "Serve",
  "how-it-works": "About",
  "next-order": "Next",
  "footer": "",
};

export default function ProgressIndicator({ currentStage, stages }: ProgressIndicatorProps) {
  const currentIndex = stages.indexOf(currentStage);

  return (
    <div className="fixed left-4 top-1/2 -translate-y-1/2 z-50 hidden md:flex flex-col items-center gap-2.5">
      {stages.filter(s => s !== "footer").map((stage, idx) => {
        const isActive = stage === currentStage;
        const isPast = idx < currentIndex;

        return (
          <div key={stage} className="flex flex-col items-center">
            <motion.div
              animate={{
                scale: isActive ? 1.4 : 1,
                backgroundColor: isActive ? "#A3E635" : isPast ? "rgba(163, 230, 53, 0.4)" : "rgba(255,255,255,0.15)",
              }}
              transition={{ duration: 0.3 }}
              className="w-2 h-2 rounded-full"
            />
            {idx < stages.length - 1 && (
              <div
                className="w-px h-2.5"
                style={{
                  backgroundColor: isPast ? "rgba(163, 230, 53, 0.3)" : "rgba(255,255,255,0.06)",
                }}
              />
            )}
          </div>
        );
      })}

      {/* Current stage label */}
      {currentIndex > 0 && (
        <motion.p
          key={currentStage}
          initial={{ opacity: 0, x: -6 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-[8px] text-lime-400/50 font-body tracking-wider uppercase mt-1.5"
          style={{ fontFamily: "'Lato', sans-serif" }}
        >
          {stageLabels[currentStage] || ""}
        </motion.p>
      )}
    </div>
  );
}
