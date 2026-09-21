import { Slot } from "expo-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { queryClient } from "../lib/queryClient";
import { AuthProvider } from "../lib/authContext";
import AppThemeProvider from "../components/AppThemeProvider";
import UpdateBanner from "../components/UpdateBanner";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AppThemeProvider>
            <UpdateBanner />
            <Slot />
          </AppThemeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
