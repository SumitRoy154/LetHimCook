import { motion } from "framer-motion";
import { Github, Linkedin } from "lucide-react";

/**
 * Footer Section
 * Minimal dark footer with brand and credits
 * Grand Hotel display + Lato body fonts
 */

export default function SectionFooter() {
  return (
    <footer className="relative w-full py-16 px-6 border-t border-white/5">
      <div className="max-w-3xl mx-auto text-center">
        {/* Brand */}
        <motion.h3
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-4xl md:text-5xl mb-4 font-bold"
          style={{ fontFamily: "'Grand Hotel', cursive" }}
        >
          <span className="text-white/90">Let Him </span>
          <span className="text-gradient-lime">Cook !!</span>
        </motion.h3>

        <p className="text-gray-400 text-base md:text-lg font-body mb-6" style={{ fontFamily: "'Lato', sans-serif" }}>
          An AI-powered autonomous kitchen experience.
        </p>

        {/* Divider */}
        <div className="w-24 h-px bg-white/10 mx-auto mb-6" />

        {/* Credits */}
        <p className="text-gray-500 text-sm font-body mb-4" style={{ fontFamily: "'Lato', sans-serif" }}>
          Copyright © 2026 Let Him Cook !! All rights reserved.
        </p>

        {/* Social Icons */}
        <div className="flex items-center justify-center gap-3">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="w-8 h-8 rounded-full border border-white/5 flex items-center justify-center hover:border-lime-400/30 transition-colors"
          >
            <Github className="w-3.5 h-3.5 text-gray-500 hover:text-lime-400 transition-colors" />
          </a>
          <a
            href="https://linkedin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="w-8 h-8 rounded-full border border-white/5 flex items-center justify-center hover:border-lime-400/30 transition-colors"
          >
            <Linkedin className="w-3.5 h-3.5 text-gray-500 hover:text-lime-400 transition-colors" />
          </a>
        </div>
      </div>
    </footer>
  );
}
