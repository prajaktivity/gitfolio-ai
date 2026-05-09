"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Target, X, Loader } from "lucide-react";
import { profileApi } from "@/lib/api";

interface Props {
  analysisId: number;
  onClose: () => void;
}

interface MatchResult {
  match_score: number;
  feedback: string;
  matching_skills: string[];
  missing_skills: string[];
  recommendation: string;
}

const RECOMMENDATION_COLOR: Record<string, string> = {
  "Strong Match": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  "Good Potential": "text-blue-400 bg-blue-500/10 border-blue-500/20",
  "Skill Gap": "text-amber-400 bg-amber-500/10 border-amber-500/20",
  "Not Recommended": "text-red-400 bg-red-500/10 border-red-500/20",
};

export default function JobMatcher({ analysisId, onClose }: Props) {
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<MatchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleMatch = async () => {
    if (!jobDescription.trim() || jobDescription.length < 50) {
      toast.error("Please paste a full job description (at least 50 characters).");
      return;
    }
    setIsLoading(true);
    try {
      const { data } = await profileApi.matchJob(analysisId, jobDescription);
      setResult(data);
    } catch {
      toast.error("Job match failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const colorClass = result
    ? RECOMMENDATION_COLOR[result.recommendation] || "text-gray-400 bg-white/5 border-white/10"
    : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/3 border border-purple-500/30 rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-purple-400" />
          <h2 className="font-semibold text-white text-sm">Job Description Matcher</h2>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      <textarea
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        placeholder="Paste a job description here… (e.g. from LinkedIn, Naukri, etc.)"
        rows={6}
        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-purple-500/50 mb-4"
      />

      <button
        onClick={handleMatch}
        disabled={isLoading}
        className="w-full bg-purple-600/80 hover:bg-purple-600 text-white py-3 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {isLoading ? (
          <><Loader className="w-4 h-4 animate-spin" /> Analyzing match…</>
        ) : (
          <><Target className="w-4 h-4" /> Check My Match Score</>
        )}
      </button>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="text-4xl font-bold text-white">{result.match_score}%</div>
            <span className={`text-xs font-medium px-3 py-1.5 rounded-full border ${colorClass}`}>
              {result.recommendation}
            </span>
          </div>

          <p className="text-sm text-gray-300 leading-relaxed">{result.feedback}</p>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="text-xs font-medium text-emerald-400 mb-2">Matching Skills</div>
              <div className="flex flex-wrap gap-1.5">
                {result.matching_skills.map((s) => (
                  <span key={s} className="text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-1 rounded-md">
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-red-400 mb-2">Missing Skills</div>
              <div className="flex flex-wrap gap-1.5">
                {result.missing_skills.map((s) => (
                  <span key={s} className="text-xs bg-red-500/10 text-red-300 border border-red-500/20 px-2 py-1 rounded-md">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
