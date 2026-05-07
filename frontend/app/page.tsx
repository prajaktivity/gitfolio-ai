"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Github, Zap, Share2, FileDown, Target, Star, GitFork, Users } from "lucide-react";
import { authApi, paymentsApi } from "@/lib/api";
import { Plan } from "@/types";

const DEMO_STATS = [
  { label: "Profiles Analyzed", value: "2,841" },
  { label: "Skills Detected", value: "18,000+" },
  { label: "PDFs Downloaded", value: "940" },
  { label: "Job Matches Made", value: "1,200+" },
];

const FEATURES = [
  {
    icon: Zap,
    title: "AI-Written Developer Summary",
    desc: "Claude reads every repo, commit, and README to write a sharp 4-sentence summary that tells recruiters exactly who you are.",
  },
  {
    icon: Share2,
    title: "Shareable Public Profile",
    desc: "Get a clean gitfolio.app/@you link. Share it on LinkedIn, job applications, or your email signature.",
  },
  {
    icon: Star,
    title: "Skill & Score Breakdown",
    desc: "Activity, quality, diversity, and impact scores — each explained so you know exactly what to improve.",
  },
  {
    icon: FileDown,
    title: "PDF Export",
    desc: "Download a recruiter-ready PDF version of your profile. One-time purchase, yours forever.",
  },
  {
    icon: Target,
    title: "Job Description Matcher",
    desc: "Paste any job description and get an instant match score with specific skill gaps identified.",
  },
  {
    icon: Users,
    title: "Built for Junior Devs",
    desc: "No inflated metrics or fake rankings. Honest analysis that helps you grow and get hired faster.",
  },
];

export default function LandingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const loginUrl = authApi.getLoginUrl();

  useEffect(() => {
    paymentsApi.getPlans().then((r) => setPlans(r.data.plans)).catch(() => {});
  }, []);

  return (
    <main className="mesh-bg min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-[#0a0a14]/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Github className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">GitFolio</span>
          </div>
          <a
            href={loginUrl}
            className="flex items-center gap-2 bg-white text-gray-900 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
          >
            <Github className="w-4 h-4" />
            Sign in with GitHub
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-40 pb-24 px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 text-indigo-300 text-sm mb-8">
            <Zap className="w-3.5 h-3.5" />
            AI-powered in 30 seconds
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-tight">
            Your GitHub,{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              analyzed by AI
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Connect GitHub. Get an AI-written developer summary, skill score, and a shareable
            profile link — ready for recruiters in under a minute.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href={loginUrl}
              className="flex items-center gap-3 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl text-base font-semibold transition-all hover:scale-105 shadow-lg shadow-indigo-500/20"
            >
              <Github className="w-5 h-5" />
              Analyze My GitHub — Free
            </a>
            <Link
              href="/profile/demo-developer"
              className="text-gray-400 hover:text-white text-sm underline underline-offset-4 transition-colors"
            >
              View a sample profile →
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto"
        >
          {DEMO_STATS.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-white">{s.value}</div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* How it works */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-center text-3xl font-bold text-white mb-4">How it works</h2>
          <p className="text-center text-gray-400 mb-16">Three steps. Under a minute.</p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Connect GitHub", desc: "One-click OAuth. We read your public repos, commits, and languages." },
              { step: "02", title: "AI Analyzes", desc: "Claude reads your repos and writes a sharp, honest developer assessment." },
              { step: "03", title: "Share & Apply", desc: "Get your gitfolio.app/@you link. Share on LinkedIn or paste in job apps." },
            ].map((s) => (
              <div key={s.step} className="relative">
                <div className="text-5xl font-bold text-white/5 mb-4">{s.step}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{s.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-center text-3xl font-bold text-white mb-4">Everything you need</h2>
          <p className="text-center text-gray-400 mb-16">Built specifically for junior devs and CS students</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <motion.div
                key={f.title}
                whileHover={{ y: -4 }}
                className="bg-white/3 border border-white/8 rounded-2xl p-6 hover:border-indigo-500/30 transition-colors"
              >
                <div className="w-10 h-10 bg-indigo-500/15 rounded-xl flex items-center justify-center mb-4">
                  <f.icon className="w-5 h-5 text-indigo-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      {plans.length > 0 && (
        <section id="pricing" className="py-20 px-6 border-t border-white/5">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-center text-3xl font-bold text-white mb-4">Simple pricing</h2>
            <p className="text-center text-gray-400 mb-16">Start free. Pay once when you're ready to stand out.</p>
            <div className="grid md:grid-cols-3 gap-6">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className={`relative rounded-2xl p-6 border transition-all ${
                    plan.highlighted
                      ? "bg-gradient-to-b from-indigo-600/20 to-purple-600/10 border-indigo-500/40 ring-1 ring-indigo-500/30"
                      : "bg-white/3 border-white/8"
                  }`}
                >
                  {plan.highlighted && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-xs font-medium px-3 py-1 rounded-full">
                      Most Popular
                    </div>
                  )}
                  <div className="mb-6">
                    <div className="text-sm text-gray-400 mb-1">{plan.name}</div>
                    <div className="flex items-end gap-1">
                      <span className="text-3xl font-bold text-white">
                        {plan.price === 0 ? "Free" : `$${plan.price}`}
                      </span>
                      {plan.price > 0 && (
                        <span className="text-gray-400 text-sm mb-1">/{plan.billing}</span>
                      )}
                    </div>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                        <span className="text-indigo-400 mt-0.5">✓</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                  <a
                    href={loginUrl}
                    className={`block text-center py-3 rounded-xl text-sm font-medium transition-all ${
                      plan.highlighted
                        ? "bg-indigo-600 hover:bg-indigo-500 text-white"
                        : "bg-white/8 hover:bg-white/12 text-white"
                    }`}
                  >
                    {plan.cta}
                  </a>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="py-24 px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Ready to get hired faster?
        </h2>
        <p className="text-gray-400 mb-8 max-w-md mx-auto">
          Join thousands of developers who've turned their GitHub into a professional profile.
        </p>
        <a
          href={loginUrl}
          className="inline-flex items-center gap-3 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-semibold transition-all hover:scale-105"
        >
          <Github className="w-5 h-5" />
          Get My Free Profile
        </a>
      </section>

      <footer className="border-t border-white/5 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Github className="w-4 h-4" />
            <span>GitFolio — Built for developers, by a developer</span>
          </div>
          <div className="text-gray-600 text-xs">© 2025 GitFolio. All rights reserved.</div>
        </div>
      </footer>
    </main>
  );
}
