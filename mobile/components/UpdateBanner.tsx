import { useState } from "react";
import { Banner } from "react-native-paper";
import Constants from "expo-constants";
import { useServerVersion } from "../hooks/useServerVersion";
import { isNewerVersion } from "../lib/version";

export default function UpdateBanner() {
  const { data } = useServerVersion();
  const [dismissed, setDismissed] = useState(false);
  const currentVersion = Constants.expoConfig?.version ?? "0.0.0";
  const serverVersion = data?.version;

  const showBanner = !dismissed && !!serverVersion && isNewerVersion(currentVersion, serverVersion);

  if (!showBanner) return null;

  return (
    <Banner
      visible
      actions={[{ label: "Dismiss", onPress: () => setDismissed(true) }]}
    >
      {`A newer version of Skål is available (v${serverVersion}). You're on v${currentVersion}.`}
    </Banner>
  );
}
