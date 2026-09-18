import { useState } from "react";
import { View, StyleSheet } from "react-native";
import { Text, TextInput, Button, HelperText } from "react-native-paper";
import { router } from "expo-router";
import { setServerUrl } from "../lib/secureStorage";
import { normalizeUrl } from "../lib/url";

export default function ServerSetupScreen() {
  const [input, setInput] = useState("");
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleContinue() {
    if (!input.trim()) {
      setError("Enter your Skål server address.");
      return;
    }
    const url = normalizeUrl(input);
    setChecking(true);
    setError(null);
    try {
      await fetch(url, { method: "GET" });
      await setServerUrl(url);
      router.replace("/login");
    } catch {
      setError("Couldn't reach that server. Check the address and your connection.");
    } finally {
      setChecking(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>Skål</Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        Enter the address of your Skål server.
      </Text>
      <TextInput
        mode="outlined"
        label="Server address"
        placeholder="skal.example.com"
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
        value={input}
        onChangeText={setInput}
        style={styles.input}
      />
      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="contained" onPress={handleContinue} loading={checking} disabled={checking}>
        Continue
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24 },
  title: { textAlign: "center", marginBottom: 8 },
  subtitle: { textAlign: "center", marginBottom: 24 },
  input: { marginBottom: 8 },
});
