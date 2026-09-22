import { Image, StyleSheet } from "react-native";
import { useThemeMode } from "../lib/theme";

// Mirrors the web app's body::before honey-pour background (templates/base.html +
// static/css/styles.css): a fixed, full-bleed, low-opacity decorative image behind
// all content, at a slightly lower opacity in dark mode.
const OPACITY: Record<"light" | "dark", number> = { light: 0.3, dark: 0.2 };

export default function AppBackground() {
  const mode = useThemeMode();

  return (
    <Image
      source={require("../assets/images/mead_background.jpg")}
      style={[styles.background, { opacity: OPACITY[mode] }]}
      resizeMode="cover"
    />
  );
}

const styles = StyleSheet.create({
  background: {
    ...StyleSheet.absoluteFill,
    zIndex: -1,
    pointerEvents: "none",
  },
});
