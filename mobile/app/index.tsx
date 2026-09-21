import { useEffect } from "react";
import { View, ActivityIndicator } from "react-native";
import { router } from "expo-router";
import { useAuthState } from "../lib/authContext";

export default function Index() {
  const { status } = useAuthState();

  useEffect(() => {
    if (status === "no-server") {
      router.replace("/server-setup");
    } else if (status === "unauthenticated") {
      router.replace("/login");
    } else if (status === "authenticated") {
      router.replace("/home");
    }
  }, [status]);

  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <ActivityIndicator />
    </View>
  );
}
