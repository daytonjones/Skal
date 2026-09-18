import { Slot } from "expo-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { PaperProvider, MD3DarkTheme } from "react-native-paper";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { queryClient } from "../lib/queryClient";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <PaperProvider theme={MD3DarkTheme}>
          <StatusBar style="light" />
          <Slot />
        </PaperProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
