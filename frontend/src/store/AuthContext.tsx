import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { AuthUser } from "../services/api";
import { getCurrentUser, login as apiLogin, logout as apiLogout, register as apiRegister, updateProfile as apiUpdateProfile } from "../services/api";

type AuthContextValue = { user: AuthUser | null; loading: boolean; login: (email: string, password: string) => Promise<AuthUser>; register: (name: string, email: string, password: string) => Promise<AuthUser>; updateProfile: (payload: { name: string; avatar_url?: string | null }) => Promise<AuthUser>; logout: () => Promise<void> };
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null); const [loading, setLoading] = useState(true);
  useEffect(() => { getCurrentUser().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false)); }, []);
  const value = useMemo<AuthContextValue>(() => ({ user, loading,
    async login(email, password) { const next = await apiLogin(email, password); setUser(next); return next; },
    async register(name, email, password) { const next = await apiRegister(name, email, password); setUser(next); return next; },
    async updateProfile(payload) { const next = await apiUpdateProfile(payload); setUser(next); return next; },
    async logout() { await apiLogout(); setUser(null); },
  }), [loading, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error("useAuth must be used inside AuthProvider"); return context; }
