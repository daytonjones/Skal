import { FlatList, View, StyleSheet } from "react-native";
import { Text, Card, FAB, ActivityIndicator, Chip, ProgressBar, Button } from "react-native-paper";
import { router, Stack } from "expo-router";
import { useBatches } from "../../../hooks/useBatches";

export default function BatchesListScreen() {
  const { data, isLoading, isError, refetch, isFetching } = useBatches();

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={{ title: "Batches" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  if (isError) {
    return (
      <>
        <Stack.Screen options={{ title: "Batches" }} />
        <View style={styles.center}>
          <Text>Couldn't load batches.</Text>
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: "Batches" }} />
      <View style={styles.container}>
      <Button mode="text" onPress={() => router.push("/batches/cellar")} style={styles.cellarLink}>
        View Cellar
      </Button>
      <FlatList
        data={data?.results ?? []}
        keyExtractor={(item) => String(item.id)}
        onRefresh={refetch}
        refreshing={isFetching}
        renderItem={({ item }) => (
          <Card style={styles.card} onPress={() => router.push(`/batches/${item.id}`)}>
            <Card.Title title={item.name} subtitle={item.stage} right={() => <Chip compact>{item.stage}</Chip>} />
            <Card.Content>
              <ProgressBar progress={item.checklist_progress / 100} />
            </Card.Content>
          </Card>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No batches yet.</Text>}
      />
      <FAB icon="plus" style={styles.fab} onPress={() => router.push("/batches/new")} />
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  cellarLink: { alignSelf: "flex-end", marginRight: 8 },
  card: { marginHorizontal: 12, marginVertical: 6 },
  empty: { textAlign: "center", marginTop: 32 },
  fab: { position: "absolute", right: 16, bottom: 16 },
});
