"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store";

export default function AuthCallback() {
  const router = useRouter();
  const params = useSearchParams();
  const { setToken, fetchUser } = useAuthStore();

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      router.push("/?error=auth_failed");
      return;
    }
    setToken(token);
    fetchUser().then(() => {
      router.push("/dashboard");
    });
  }, []);

  return (
    <div className="min-h-screen mesh-bg flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Connecting your GitHub…</p>
      </div>
    </div>
  );
}
