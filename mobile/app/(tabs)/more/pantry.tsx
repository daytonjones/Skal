import { useState } from "react";
import { FlatList, View, StyleSheet } from "react-native";
import { Text, List, IconButton, TextInput, Button, ActivityIndicator } from "react-native-paper";
import { usePantry, useCreatePantryItem, useDeletePantryItem } from "../../../hooks/usePantry";

export default function PantryScreen() {
  const { data, isLoading, isError } = usePantry();
  const createMutation = useCreatePantryItem();
  const deleteMutation = useDeletePantryItem();
  const [ingredientId, setIngredientId] = useState("");
  const [quantity, setQuantity] = useState("");

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
        <Text>Couldn't load your pantry.</Text>
      </View>
    );
  }

  async function handleAdd() {
    if (!ingredientId) return;
    await createMutation.mutateAsync({
      ingredient_id: Number(ingredientId),
      quantity,
      notes: "",
    });
    setIngredientId("");
    setQuantity("");
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={data?.results ?? []}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <List.Item
            title={item.ingredient.name}
            description={item.quantity}
            right={() => (
              <IconButton icon="delete" onPress={() => deleteMutation.mutate(item.id)} />
            )}
          />
        )}
        ListEmptyComponent={<Text style={styles.empty}>Your pantry is empty.</Text>}
      />
      <View style={styles.addRow}>
        <TextInput
          mode="outlined"
          label="Ingredient ID"
          value={ingredientId}
          onChangeText={setIngredientId}
          keyboardType="number-pad"
          style={styles.idInput}
        />
        <TextInput
          mode="outlined"
          label="Quantity"
          value={quantity}
          onChangeText={setQuantity}
          style={styles.qtyInput}
        />
        <Button mode="contained" onPress={handleAdd} loading={createMutation.isPending}>
          Add
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  empty: { textAlign: "center", marginTop: 32 },
  addRow: { flexDirection: "row", alignItems: "center", padding: 12, gap: 8 },
  idInput: { flex: 1 },
  qtyInput: { flex: 1 },
});
