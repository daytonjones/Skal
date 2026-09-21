import { useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { Text, Switch, Button, ActivityIndicator, SegmentedButtons, HelperText } from "react-native-paper";
import { router, Stack } from "expo-router";
import { useMe, useUpdateMe } from "../../../hooks/useMe";
import { useAuthState } from "../../../lib/authContext";
import { firstErrorMessage } from "../../../lib/errors";

export default function ProfileScreen() {
  const { data: me, isLoading } = useMe();
  const updateMutation = useUpdateMe();
  const { signOut } = useAuthState();
  const [error, setError] = useState<string | null>(null);

  if (isLoading || !me) {
    return (
      <>
        <Stack.Screen options={{ title: "Profile" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  const prefs = me.notification_prefs;

  function togglePref(key: string, value: boolean) {
    updateMutation.mutate({ notification_prefs: { ...prefs, [key]: value } });
  }

  function changeTheme(theme: "light" | "dark") {
    setError(null);
    updateMutation.mutate({ theme }, { onError: (err) => setError(firstErrorMessage(err)) });
  }

  async function handleLogout() {
    await signOut();
    router.replace("/login");
  }

  return (
    <>
      <Stack.Screen options={{ title: "Profile" }} />
      <ScrollView contentContainerStyle={styles.container}>
      <Text variant="headlineSmall">{me.username}</Text>
      <Text variant="bodyMedium" style={styles.section}>{me.email}</Text>

      <Text variant="titleMedium" style={styles.section}>Theme</Text>
      <SegmentedButtons
        value={me.theme}
        onValueChange={(v) => changeTheme(v as "light" | "dark")}
        buttons={[
          { value: "light", label: "Light" },
          { value: "dark", label: "Dark" },
        ]}
      />
      {error ? <HelperText type="error">{error}</HelperText> : null}

      <Text variant="titleMedium" style={styles.section}>Notifications</Text>
      {prefs ? (
        <>
          <View style={styles.row}>
            <Text>Email notifications</Text>
            <Switch
              value={prefs.email_notifications}
              onValueChange={(v) => togglePref("email_notifications", v)}
            />
          </View>
          <View style={styles.row}>
            <Text>TOSNA reminders</Text>
            <Switch value={prefs.notify_tosna} onValueChange={(v) => togglePref("notify_tosna", v)} />
          </View>
          <View style={styles.row}>
            <Text>Gravity check reminders</Text>
            <Switch value={prefs.notify_sg_check} onValueChange={(v) => togglePref("notify_sg_check", v)} />
          </View>
          <View style={styles.row}>
            <Text>Racking reminders</Text>
            <Switch value={prefs.notify_rack} onValueChange={(v) => togglePref("notify_rack", v)} />
          </View>
          <View style={styles.row}>
            <Text>Bottling reminders</Text>
            <Switch value={prefs.notify_bottle} onValueChange={(v) => togglePref("notify_bottle", v)} />
          </View>
        </>
      ) : (
        <Text variant="bodyMedium">Notification preferences are not set up yet.</Text>
      )}

      <Button mode="outlined" onPress={() => router.push("/more/settings")} style={styles.button}>
        Server settings
      </Button>
      <Button mode="outlined" textColor="red" onPress={handleLogout} style={styles.button}>
        Log out
      </Button>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  section: { marginTop: 16, marginBottom: 8 },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 8 },
  button: { marginTop: 16 },
});
