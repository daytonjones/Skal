import { lightTheme, darkTheme, lightNavTheme, darkNavTheme, themeForMode } from "../lib/theme";

function lum(hex: string): number {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) =>
    v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4),
  );
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function contrast(a: string, b: string): number {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

describe.each([
  ["light", lightTheme, lightNavTheme],
  ["dark", darkTheme, darkNavTheme],
] as const)("%s theme", (_name, paper, nav) => {
  const c = paper.colors;
  it("keeps paper's background opaque but leaves the nav background transparent so AppBackground shows through screen content", () => {
    // React Navigation/expo-router paint `colors.background` opaquely behind every
    // screen (react-native-screens' ScreenStack container + the native-stack/bottom-tabs
    // Background view), independent of anything in app/_layout.tsx. Paper's own
    // `background` stays a real color for Paper components (Surface, etc.).
    expect(nav.colors.background).toBe("transparent");
    expect(c.background).not.toBe("transparent");
    expect(c.onBackground).not.toBe(c.background);
  });
  it("has readable text pairs", () => {
    expect(contrast(c.onBackground, c.background)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(c.onSurface, c.surface)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(c.onPrimary, c.primary)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(c.onSurface, c.elevation.level1)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(nav.colors.text, nav.colors.card)).toBeGreaterThanOrEqual(4.5);
  });
});

it("themeForMode selects by mode", () => {
  expect(themeForMode("light").paper).toBe(lightTheme);
  expect(themeForMode("dark").navigation).toBe(darkNavTheme);
});
