import { FlatList, View, StyleSheet } from "react-native";
import { Text, Card, ActivityIndicator, Button } from "react-native-paper";
import { router } from "expo-router";
import { useBatches } from "../../../hooks/useBatches";

export default function HomeScreen() {
  const { data, isLoading, isError } = useBatches();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  const recent = (data?.results ?? []).slice(0, 5);

  return (
    <View style={styles.container}>
      <Text variant="headlineSmall" style={styles.title}>Skål</Text>
      <Text variant="titleMedium" style={styles.section}>Recent batches</Text>
      {isError ? (
        <Text>Couldn't load your batches.</Text>
      ) : (
        <FlatList
          data={recent}
          keyExtractor={(item) => String(item.id)}
          renderItem={({ item }) => (
            <Card style={styles.card} onPress={() => router.push(`/batches/${item.id}`)}>
              <Card.Title title={item.name} subtitle={item.stage} />
            </Card>
          )}
          ListEmptyComponent={<Text style={styles.empty}>No batches yet — start one!</Text>}
        />
      )}
      <View style={styles.links}>
        <Button mode="outlined" onPress={() => router.push("/recipes")} style={styles.linkButton}>
          Browse recipes
        </Button>
        <Button mode="outlined" onPress={() => router.push("/batches/new")} style={styles.linkButton}>
          Start a batch
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  title: { marginBottom: 16 },
  section: { marginBottom: 8 },
  card: { marginBottom: 8 },
  empty: { textAlign: "center", marginTop: 16 },
  links: { marginTop: 16, gap: 8 },
  linkButton: { marginBottom: 8 },
});
