import { View, StyleSheet } from "react-native";
import { Text, Button } from "react-native-paper";
import { router } from "expo-router";

export default function PendingApprovalScreen() {
  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>Almost there</Text>
      <Text variant="bodyMedium" style={styles.body}>
        Your account has been created and is waiting for an admin to approve
        it. You'll be able to log in once that happens.
      </Text>
      <Button mode="contained" onPress={() => router.replace("/login")}>
        Back to login
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24 },
  title: { textAlign: "center", marginBottom: 16 },
  body: { textAlign: "center", marginBottom: 24 },
});
