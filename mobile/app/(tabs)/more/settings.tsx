import { useState, useEffect } from "react";
import { View, StyleSheet } from "react-native";
import { Text, TextInput, Button, HelperText } from "react-native-paper";
import { router, Stack } from "expo-router";
import { getServerUrl, setServerUrl } from "../../../lib/secureStorage";
import { useAuthState } from "../../../lib/authContext";
import { normalizeUrl } from "../../../lib/url";

export default function SettingsScreen() {
  const { signOut } = useAuthState();
  const [current, setCurrent] = useState("");
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getServerUrl().then((url) => {
      setCurrent(url ?? "");
      setInput(url ?? "");
    });
  }, []);

  async function handleSave() {
    if (!input.trim()) {
      setError("Enter a server address.");
      return;
    }
    const url = normalizeUrl(input);
    setSaving(true);
    setError(null);
    try {
      await fetch(url, { method: "GET" });
      await setServerUrl(url);
      if (url !== current) {
        // Switching servers invalidates any existing session for the old one.
        await signOut();
        router.replace("/login");
        return;
      }
      router.back();
    } catch {
      setError("Couldn't reach that server. Check the address and your connection.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Stack.Screen options={{ title: "Server Settings" }} />
      <View style={styles.container}>
      <Text variant="titleMedium" style={styles.title}>Server address</Text>
      <TextInput
        mode="outlined"
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
        value={input}
        onChangeText={setInput}
        style={styles.input}
      />
      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="contained" onPress={handleSave} loading={saving} disabled={saving}>
        Save
      </Button>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { marginBottom: 12 },
  input: { marginBottom: 8 },
});
