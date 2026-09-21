import { useState } from "react";
import { View, StyleSheet } from "react-native";
import { Text, TextInput, Button, HelperText } from "react-native-paper";
import { Link, router } from "expo-router";
import { login } from "../../api/auth";
import { useAuthState } from "../../lib/authContext";

export default function LoginScreen() {
  const { refreshStatus } = useAuthState();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setLoading(true);
    setError(null);
    const result = await login(username, password);
    setLoading(false);
    if (result.ok) {
      await refreshStatus();
      router.replace("/home");
      return;
    }
    if (result.reason === "pending_approval") {
      router.push("/pending-approval");
      return;
    }
    setError("Incorrect username or password.");
  }

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>Skål</Text>
      <TextInput
        mode="outlined"
        label="Username"
        autoCapitalize="none"
        autoCorrect={false}
        value={username}
        onChangeText={setUsername}
        style={styles.input}
      />
      <TextInput
        mode="outlined"
        label="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        style={styles.input}
      />
      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="contained" onPress={handleLogin} loading={loading} disabled={loading}>
        Log in
      </Button>
      <Link href="/register" style={styles.link}>
        <Text>Need an account? Register</Text>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24 },
  title: { textAlign: "center", marginBottom: 24 },
  input: { marginBottom: 12 },
  link: { marginTop: 16, alignSelf: "center" },
});
