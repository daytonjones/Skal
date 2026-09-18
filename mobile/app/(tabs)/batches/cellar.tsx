import { FlatList, View, StyleSheet } from "react-native";
import { Text, Card, ActivityIndicator } from "react-native-paper";
import { router } from "expo-router";
import { useBatches } from "../../../hooks/useBatches";

export default function CellarScreen() {
  const { data, isLoading, isError } = useBatches();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  if (isError) {
    return (
      <View style={styles.center}>
        <Text>Couldn't load the cellar.</Text>
      </View>
    );
  }

  const bottled = (data?.results ?? []).filter((b) => b.bottled_done && b.bottle_count != null);

  return (
    <FlatList
      data={bottled}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => (
        <Card style={styles.card} onPress={() => router.push(`/batches/${item.id}`)}>
          <Card.Title title={item.name} subtitle={`${item.bottles_remaining} bottles remaining`} />
        </Card>
      )}
      ListEmptyComponent={<Text style={styles.empty}>No bottled batches yet.</Text>}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  card: { marginHorizontal: 12, marginVertical: 6 },
  empty: { textAlign: "center", marginTop: 32 },
});
