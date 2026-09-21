import { useState } from "react";
import { View, StyleSheet } from "react-native";
import { Text, TextInput, Button, HelperText } from "react-native-paper";
import { router } from "expo-router";
import { register } from "../../api/auth";
import { firstErrorMessage } from "../../lib/errors";

export default function RegisterScreen() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleRegister() {
    setLoading(true);
    setError(null);
    try {
      await register(username, email, password);
      router.replace("/pending-approval");
    } catch (err) {
      setError(firstErrorMessage(err, "Couldn't reach the server."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>Create account</Text>
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
        label="Email"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
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
      <Button mode="contained" onPress={handleRegister} loading={loading} disabled={loading}>
        Register
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24 },
  title: { textAlign: "center", marginBottom: 24 },
  input: { marginBottom: 12 },
});
