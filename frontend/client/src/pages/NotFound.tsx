import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

/**
 * NotFound page - minimal dark 404
 */
export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#080808] flex items-center justify-center">
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-8xl font-bold text-white/10 mb-4"
          style={{ fontFamily: "'Space Grotesk', sans-serif" }}
        >
          404
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-500 text-lg mb-8"
        >
          Page not found
        </motion.p>
        <Button
          variant="outline"
          className="border-white/10 text-white hover:bg-white/5"
          onClick={() => window.location.href = "/"}
        >
          Go Home
        </Button>
      </div>
    </div>
  );
}
