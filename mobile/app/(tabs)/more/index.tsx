import { View, StyleSheet } from "react-native";
import { List } from "react-native-paper";
import { router, Stack } from "expo-router";

export default function MoreScreen() {
  return (
    <>
      <Stack.Screen options={{ title: "More" }} />
      <View style={styles.container}>
      <List.Item title="Pantry" left={(props) => <List.Icon {...props} icon="basket" />} onPress={() => router.push("/more/pantry")} />
      <List.Item title="Yeast Reference" left={(props) => <List.Icon {...props} icon="flask-outline" />} onPress={() => router.push("/more/yeast")} />
      <List.Item title="Calculators" left={(props) => <List.Icon {...props} icon="calculator" />} onPress={() => router.push("/more/calculators")} />
      <List.Item title="Profile" left={(props) => <List.Icon {...props} icon="account" />} onPress={() => router.push("/more/profile")} />
      <List.Item title="Settings" left={(props) => <List.Icon {...props} icon="cog" />} onPress={() => router.push("/more/settings")} />
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
});
