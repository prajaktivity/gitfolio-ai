import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("gitfolio_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("gitfolio_token");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  getMe: () => api.get("/api/auth/me"),
  logout: () => api.post("/api/auth/logout"),
  getLoginUrl: () => `${API_URL}/api/auth/github/login`,
};

// ── Profile ───────────────────────────────────────────────────────────────────
export const profileApi = {
  sync: () => api.post("/api/profile/sync"),
  getMyAnalysis: () => api.get("/api/profile/me"),
  getPublicProfile: (slug: string) => api.get(`/api/profile/public/${slug}`),
  matchJob: (analysisId: number, jobDescription: string) =>
    api.post("/api/profile/job-match", {
      analysis_id: analysisId,
      job_description: jobDescription,
    }),
  exportPdf: () =>
    api.get("/api/profile/export-pdf", { responseType: "blob" }),
};

// ── Payments ──────────────────────────────────────────────────────────────────
export const paymentsApi = {
  getPlans: () => api.get("/api/payments/plans"),
  createCheckout: (planType: string) =>
    api.post("/api/payments/create-checkout", { plan_type: planType }),
};
