import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { router } from "expo-router";
import { getServerUrl, getTokens, clearTokens } from "./secureStorage";
import { setSessionExpiredHandler } from "./apiFetch";

type AuthStatus = "loading" | "no-server" | "unauthenticated" | "authenticated";

interface AuthContextValue {
  status: AuthStatus;
  signOut: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");

  const refreshStatus = useCallback(async () => {
    const serverUrl = await getServerUrl();
    if (!serverUrl) {
      setStatus("no-server");
      return;
    }
    const tokens = await getTokens();
    setStatus(tokens ? "authenticated" : "unauthenticated");
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  useEffect(() => {
    setSessionExpiredHandler(() => {
      setStatus("unauthenticated");
      router.replace("/login");
    });
  }, []);

  const signOut = useCallback(async () => {
    await clearTokens();
    setStatus("unauthenticated");
  }, []);

  return (
    <AuthContext.Provider value={{ status, signOut, refreshStatus }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthState(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthState must be used within AuthProvider");
  return ctx;
}
