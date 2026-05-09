import { create } from "zustand";
import { User } from "@/types";
import { authApi } from "@/lib/api";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setToken: (token: string) => void;
  fetchUser: () => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== "undefined" ? localStorage.getItem("gitfolio_token") : null,
  isLoading: false,

  setToken: (token) => {
    localStorage.setItem("gitfolio_token", token);
    set({ token });
  },

  fetchUser: async () => {
    set({ isLoading: true });
    try {
      const { data } = await authApi.getMe();
      set({ user: data, isLoading: false });
    } catch {
      set({ user: null, isLoading: false });
      localStorage.removeItem("gitfolio_token");
    }
  },

  logout: () => {
    localStorage.removeItem("gitfolio_token");
    set({ user: null, token: null });
    window.location.href = "/";
  },
}));
