import { createContext, useContext } from "react";
import { MD3DarkTheme, MD3LightTheme, type MD3Theme } from "react-native-paper";
import { DarkTheme, DefaultTheme } from "expo-router";

export type ThemeMode = "light" | "dark";

// Exposes the resolved light/dark mode (computed once in AppThemeProvider from the
// logged-in user's saved preference) to any component that needs it, without having
// to re-derive it from useAuthState()/useMe() or drill it through props.
export const ThemeModeContext = createContext<ThemeMode>("dark");

export function useThemeMode(): ThemeMode {
  return useContext(ThemeModeContext);
}

export const stageColors = {
  planned: "#94a3b8",
  active: "#d97706",
  secondary: "#7c3aed",
  bottled: "#16a34a",
} as const;

export const lightTheme: MD3Theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    // Web uses #d97706 with white text (3.2:1); brown-500 keeps white text >= 4.5:1.
    primary: "#b45309",
    onPrimary: "#ffffff",
    primaryContainer: "#fef3c7",
    onPrimaryContainer: "#451a03",
    secondary: "#92400e",
    onSecondary: "#ffffff",
    background: "#fef9ef",
    onBackground: "#451a03",
    surface: "#ffffff",
    onSurface: "#451a03",
    surfaceVariant: "#fef3c7",
    onSurfaceVariant: "#92400e",
    outline: "#e9d5a1",
    elevation: {
      level0: "transparent",
      level1: "#f8d860",
      level2: "#f5d054",
      level3: "#f2c948",
      level4: "#efc23e",
      level5: "#ecbb34",
    },
  },
};

export const darkTheme: MD3Theme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: "#f59e0b",
    onPrimary: "#1c0a00",
    primaryContainer: "#451a03",
    onPrimaryContainer: "#fde68a",
    secondary: "#fcd97a",
    onSecondary: "#1c0a00",
    background: "#1a0f00",
    onBackground: "#fde68a",
    surface: "#1f1000",
    onSurface: "#fde68a",
    surfaceVariant: "#2a1500",
    onSurfaceVariant: "#fcd97a",
    outline: "#5a3a1a",
    elevation: {
      level0: "transparent",
      level1: "#2a1500",
      level2: "#301a05",
      level3: "#361f0a",
      level4: "#3b230d",
      level5: "#402810",
    },
  },
};

// The nav theme's `background` is what React Navigation/expo-router paints, opaquely,
// behind every screen's content (react-native-screens' ScreenStack container, plus the
// per-screen Background view used by both the native-stack and bottom-tabs navigators).
// That paint happens *underneath* every routed screen regardless of anything set in
// app/_layout.tsx, so to let AppBackground's mead photo show through screen content
// (rendered as a sibling behind the navigator, see app/_layout.tsx + AppBackground.tsx)
// this must be transparent rather than an opaque color. Paper's own `background` (used
// for Paper components like Surface) is intentionally left opaque and unchanged, and
// `card`/`text`/`border` (header + tab bar chrome) stay solid so nav chrome is unaffected.
export const lightNavTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: "#f59e0b",
    background: "transparent",
    card: "#1c0a00",
    text: "#fef3c7",
    border: "#451a03",
    notification: "#d97706",
  },
};

export const darkNavTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: "#f59e0b",
    background: "transparent",
    card: "#1c0a00",
    text: "#fef3c7",
    border: "#5a3a1a",
    notification: "#d97706",
  },
};

export function themeForMode(mode: ThemeMode) {
  return mode === "light"
    ? { paper: lightTheme, navigation: lightNavTheme }
    : { paper: darkTheme, navigation: darkNavTheme };
}
