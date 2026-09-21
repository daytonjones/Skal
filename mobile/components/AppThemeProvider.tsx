import type { ReactNode } from "react";
import { PaperProvider } from "react-native-paper";
import { ThemeProvider } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useAuthState } from "../lib/authContext";
import { useMe } from "../hooks/useMe";
import { themeForMode, type ThemeMode } from "../lib/theme";

export default function AppThemeProvider({ children }: { children: ReactNode }) {
  const { status } = useAuthState();
  const { data: me } = useMe({ enabled: status === "authenticated" });
  const mode: ThemeMode = me?.theme ?? "dark";
  const { paper, navigation } = themeForMode(mode);

  return (
    <PaperProvider theme={paper}>
      <ThemeProvider value={navigation}>
        <StatusBar style="light" />
        {children}
      </ThemeProvider>
    </PaperProvider>
  );
}
