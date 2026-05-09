import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "GitFolio — AI-Powered GitHub Portfolio Analyzer",
  description:
    "Turn your GitHub into a recruiter-ready portfolio in 30 seconds. AI-generated developer summary, skill analysis, and shareable profile link.",
  keywords: "github portfolio, developer portfolio, github profile analyzer, AI resume",
  openGraph: {
    title: "GitFolio — AI GitHub Portfolio",
    description: "Your GitHub, analyzed by AI. Get a shareable developer profile in 30 seconds.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-[#0a0a14] text-white antialiased">
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#1a1a2e",
              color: "#fff",
              border: "1px solid rgba(99,102,241,0.3)",
            },
          }}
        />
      </body>
    </html>
  );
}
