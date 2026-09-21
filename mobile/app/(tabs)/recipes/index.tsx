import { FlatList, View, StyleSheet } from "react-native";
import { Text, Card, FAB, ActivityIndicator, Chip } from "react-native-paper";
import { router, Stack } from "expo-router";
import { useRecipes } from "../../../hooks/useRecipes";

export default function RecipesListScreen() {
  const { data, isLoading, isError, refetch, isFetching } = useRecipes();

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={{ title: "Recipes" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  if (isError) {
    return (
      <>
        <Stack.Screen options={{ title: "Recipes" }} />
        <View style={styles.center}>
          <Text>Couldn't load recipes.</Text>
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: "Recipes" }} />
      <View style={styles.container}>
      <FlatList
        data={data?.results ?? []}
        keyExtractor={(item) => String(item.id)}
        onRefresh={refetch}
        refreshing={isFetching}
        renderItem={({ item }) => (
          <Card style={styles.card} onPress={() => router.push(`/recipes/${item.id}`)}>
            <Card.Title
              title={item.name}
              right={() => (item.is_public ? <Chip compact>Public</Chip> : null)}
            />
          </Card>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No recipes yet.</Text>}
      />
      <FAB icon="plus" style={styles.fab} onPress={() => router.push("/recipes/new")} />
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  card: { marginHorizontal: 12, marginVertical: 6 },
  empty: { textAlign: "center", marginTop: 32 },
  fab: { position: "absolute", right: 16, bottom: 16 },
});
