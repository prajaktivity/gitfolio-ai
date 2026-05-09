"use client";

import { motion } from "framer-motion";
import { Language } from "@/types";

interface Props {
  languages: Language[];
}

export default function LanguageBar({ languages }: Props) {
  return (
    <div className="space-y-3">
      {languages.slice(0, 6).map((lang, i) => (
        <div key={lang.name}>
          <div className="flex justify-between text-xs text-gray-400 mb-1.5">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ background: lang.color }}
              />
              {lang.name}
            </div>
            <span>{lang.percentage}%</span>
          </div>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${lang.percentage}%` }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: "easeOut" }}
              className="h-full rounded-full"
              style={{ background: lang.color }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
