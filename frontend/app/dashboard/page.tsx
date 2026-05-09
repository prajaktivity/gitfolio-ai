"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import {
  RefreshCw, Share2, Download, Target, Github, ExternalLink,
  Star, GitFork, Users, Code, Zap, TrendingUp, ChevronRight,
} from "lucide-react";
import Image from "next/image";
import { useAuthStore } from "@/lib/store";
import { profileApi, paymentsApi } from "@/lib/api";
import { ProfileAnalysis, GitHubProfile } from "@/types";
import ScoreRing from "@/components/dashboard/ScoreRing";
import LanguageBar from "@/components/dashboard/LanguageBar";
import JobMatcher from "@/components/dashboard/JobMatcher";

export default function DashboardPage() {
  const router = useRouter();
  const { user, fetchUser, token, logout } = useAuthStore();
  const [analysis, setAnalysis] = useState<ProfileAnalysis | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [showJobMatcher, setShowJobMatcher] = useState(false);

  useEffect(() => {
    if (!token) { router.push("/"); return; }
    fetchUser().then(() => {
      loadAnalysis();
    });
  }, []);

  const loadAnalysis = async () => {
    try {
      const { data } = await profileApi.getMyAnalysis();
      setAnalysis(data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // First time — auto sync
        handleSync();
      }
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const { data } = await profileApi.sync();
      setAnalysis(data);
      await fetchUser();
      toast.success("Profile synced and analyzed!");
    } catch {
      toast.error("Failed to sync. Please try again.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleShare = () => {
    if (!analysis) return;
    const url = `${window.location.origin}/profile/${analysis.slug}`;
    navigator.clipboard.writeText(url);
    toast.success("Profile link copied!");
  };

  const handleExportPdf = async () => {
    if (user?.plan === "free") {
      const { data } = await paymentsApi.createCheckout("one_time");
      window.location.href = data.checkout_url;
      return;
    }
    try {
      toast.loading("Generating PDF…");
      const response = await profileApi.exportPdf();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `gitfolio-${user?.github_username}.pdf`;
      a.click();
      toast.dismiss();
      toast.success("PDF downloaded!");
    } catch {
      toast.dismiss();
      toast.error("Failed to generate PDF.");
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen mesh-bg flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a14]">
      {/* Top Nav */}
      <nav className="border-b border-white/5 bg-[#0d0d1a]/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Github className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">GitFolio</span>
          </div>
          <div className="flex items-center gap-3">
            {user.plan === "free" && (
              <button
                onClick={async () => {
                  const { data } = await paymentsApi.createCheckout("one_time");
                  window.location.href = data.checkout_url;
                }}
                className="text-xs bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 px-3 py-1.5 rounded-lg hover:bg-indigo-500/25 transition-colors"
              >
                Upgrade →
              </button>
            )}
            {user.plan !== "free" && (
              <span className="text-xs bg-purple-500/15 text-purple-300 border border-purple-500/30 px-3 py-1.5 rounded-lg">
                {user.plan === "pro" ? "Job Hunter" : "Full Profile"}
              </span>
            )}
            <div className="flex items-center gap-2">
              {user.avatar_url && (
                <Image
                  src={user.avatar_url}
                  alt={user.github_username}
                  width={32}
                  height={32}
                  className="rounded-full border border-white/10"
                />
              )}
              <button onClick={logout} className="text-xs text-gray-500 hover:text-gray-300">
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-10">
          <div className="flex items-center gap-4">
            {user.avatar_url && (
              <Image
                src={user.avatar_url}
                alt={user.github_username}
                width={64}
                height={64}
                className="rounded-2xl border border-white/10"
              />
            )}
            <div>
              <h1 className="text-2xl font-bold text-white">{user.name || user.github_username}</h1>
              <div className="flex items-center gap-2 mt-1">
                <a
                  href={`https://github.com/${user.github_username}`}
                  target="_blank"
                  className="text-gray-400 text-sm hover:text-white flex items-center gap-1"
                >
                  @{user.github_username}
                  <ExternalLink className="w-3 h-3" />
                </a>
                {analysis?.career_level && (
                  <span className="bg-indigo-500/15 text-indigo-300 text-xs px-2 py-0.5 rounded-full border border-indigo-500/20">
                    {analysis.career_level}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className="flex items-center gap-2 bg-white/5 hover:bg-white/8 border border-white/10 text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} />
              {isSyncing ? "Analyzing…" : "Re-sync"}
            </button>
            <button
              onClick={handleShare}
              className="flex items-center gap-2 bg-white/5 hover:bg-white/8 border border-white/10 text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-all"
            >
              <Share2 className="w-4 h-4" />
              Share Profile
            </button>
            <button
              onClick={handleExportPdf}
              className="flex items-center gap-2 bg-indigo-600/80 hover:bg-indigo-600 border border-indigo-500/50 text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-all"
            >
              <Download className="w-4 h-4" />
              {user.plan === "free" ? "Export PDF ($9)" : "Export PDF"}
            </button>
            {user.plan === "pro" && (
              <button
                onClick={() => setShowJobMatcher(!showJobMatcher)}
                className="flex items-center gap-2 bg-purple-600/80 hover:bg-purple-600 border border-purple-500/50 text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-all"
              >
                <Target className="w-4 h-4" />
                Job Match
              </button>
            )}
          </div>
        </div>

        {isSyncing && !analysis && (
          <div className="text-center py-24">
            <div className="w-12 h-12 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Analyzing your GitHub profile…</p>
            <p className="text-gray-600 text-sm mt-2">Reading repos, commits, and languages. This takes ~30 seconds.</p>
          </div>
        )}

        {analysis && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid lg:grid-cols-3 gap-6"
          >
            {/* Left column */}
            <div className="lg:col-span-2 space-y-6">
              {/* AI Summary Card */}
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-4 h-4 text-indigo-400" />
                  <h2 className="font-semibold text-white text-sm">AI Summary</h2>
                </div>
                {analysis.headline && (
                  <h3 className="text-lg font-medium text-white mb-3">{analysis.headline}</h3>
                )}
                <p className="text-gray-300 leading-relaxed text-sm">{analysis.summary}</p>
              </div>

              {/* Scores */}
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-6">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  <h2 className="font-semibold text-white text-sm">Profile Scores</h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries({
                    Activity: analysis.scores.activity,
                    Quality: analysis.scores.quality,
                    Diversity: analysis.scores.diversity,
                    Impact: analysis.scores.impact,
                  }).map(([label, score]) => (
                    <ScoreRing key={label} label={label} score={score} />
                  ))}
                </div>
              </div>

              {/* Strengths & Improvements */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                  <h2 className="font-semibold text-white text-sm mb-4">✦ Strengths</h2>
                  <ul className="space-y-2.5">
                    {analysis.strengths.map((s) => (
                      <li key={s} className="flex items-start gap-2 text-sm text-gray-300">
                        <span className="text-emerald-400 mt-0.5">●</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                  <h2 className="font-semibold text-white text-sm mb-4">↑ Improve</h2>
                  <ul className="space-y-2.5">
                    {analysis.improvement_areas.map((s) => (
                      <li key={s} className="flex items-start gap-2 text-sm text-gray-300">
                        <span className="text-amber-400 mt-0.5">●</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Job Matcher */}
              {showJobMatcher && analysis && (
                <JobMatcher analysisId={analysis.id} onClose={() => setShowJobMatcher(false)} />
              )}

              {/* Upgrade Banner */}
              {user.plan === "free" && (
                <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-6 flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-white mb-1">Get the Full Profile</div>
                    <div className="text-sm text-gray-400">PDF export, watermark removal, and job matching for $9 one-time.</div>
                  </div>
                  <button
                    onClick={async () => {
                      const { data } = await paymentsApi.createCheckout("one_time");
                      window.location.href = data.checkout_url;
                    }}
                    className="flex items-center gap-1 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap ml-4"
                  >
                    Upgrade $9 <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Right column */}
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6 text-center">
                <div className="text-5xl font-bold text-white mb-1">{Math.round(analysis.scores.overall)}</div>
                <div className="text-gray-400 text-sm">Overall Score</div>
                <div className="mt-3">
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${analysis.scores.overall}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                    />
                  </div>
                </div>
              </div>

              {/* Recommended Roles */}
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-4">Recommended Roles</h2>
                <div className="flex flex-wrap gap-2">
                  {analysis.recommended_roles.map((role) => (
                    <span
                      key={role}
                      className="bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-3 py-1.5 rounded-lg text-xs"
                    >
                      {role}
                    </span>
                  ))}
                </div>
              </div>

              {/* Share Link */}
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-3">Your Public Profile</h2>
                <div className="bg-white/5 rounded-lg px-3 py-2.5 text-xs text-gray-400 font-mono break-all mb-3">
                  gitfolio.app/profile/{analysis.slug}
                </div>
                <button
                  onClick={handleShare}
                  className="w-full bg-indigo-600/50 hover:bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Share2 className="w-4 h-4" />
                  Copy Link
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
