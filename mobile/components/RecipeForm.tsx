import { useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { TextInput, Button, Switch, Text, IconButton } from "react-native-paper";
import type { Recipe, RecipeInput, RecipeIngredientInput } from "../api/types";

interface Props {
  initial?: Recipe;
  onSubmit: (input: RecipeInput) => Promise<void>;
  submitLabel: string;
}

export default function RecipeForm({ initial, onSubmit, submitLabel }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [batchSize, setBatchSize] = useState(initial?.batch_size ?? "5.0");
  const [instructions, setInstructions] = useState(initial?.instructions ?? "");
  const [isPublic, setIsPublic] = useState(initial?.is_public ?? false);
  const [ingredients, setIngredients] = useState<RecipeIngredientInput[]>(
    initial?.recipe_ingredients.map((ri) => ({
      ingredient_id: ri.ingredient.id,
      quantity: ri.quantity,
      order: ri.order,
    })) ?? []
  );
  const [submitting, setSubmitting] = useState(false);

  function addIngredientRow() {
    setIngredients((prev) => [...prev, { ingredient_id: 0, quantity: "", order: prev.length }]);
  }

  function updateIngredient(index: number, patch: Partial<RecipeIngredientInput>) {
    setIngredients((prev) => prev.map((ing, i) => (i === index ? { ...ing, ...patch } : ing)));
  }

  function removeIngredient(index: number) {
    setIngredients((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit() {
    setSubmitting(true);
    try {
      await onSubmit({
        name,
        batch_size: batchSize,
        instructions,
        is_public: isPublic,
        recipe_ingredients: ingredients.filter((ing) => ing.ingredient_id > 0),
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TextInput mode="outlined" label="Name" value={name} onChangeText={setName} style={styles.input} />
      <TextInput
        mode="outlined"
        label="Batch size (gal)"
        value={batchSize}
        onChangeText={setBatchSize}
        keyboardType="decimal-pad"
        style={styles.input}
      />
      <TextInput
        mode="outlined"
        label="Instructions"
        value={instructions}
        onChangeText={setInstructions}
        multiline
        numberOfLines={6}
        style={styles.input}
      />
      <View style={styles.row}>
        <Text>Public</Text>
        <Switch value={isPublic} onValueChange={setIsPublic} />
      </View>

      <Text variant="titleMedium" style={styles.sectionTitle}>Ingredients</Text>
      {ingredients.map((ing, index) => (
        <View key={index} style={styles.ingredientRow}>
          <TextInput
            mode="outlined"
            label="Ingredient ID"
            value={ing.ingredient_id ? String(ing.ingredient_id) : ""}
            onChangeText={(v) => updateIngredient(index, { ingredient_id: Number(v) || 0 })}
            keyboardType="number-pad"
            style={styles.ingredientIdInput}
          />
          <TextInput
            mode="outlined"
            label="Quantity"
            value={ing.quantity}
            onChangeText={(v) => updateIngredient(index, { quantity: v })}
            style={styles.ingredientQtyInput}
          />
          <IconButton icon="delete" onPress={() => removeIngredient(index)} />
        </View>
      ))}
      <Button mode="text" onPress={addIngredientRow}>Add ingredient</Button>

      <Button mode="contained" onPress={handleSubmit} loading={submitting} disabled={submitting} style={styles.submit}>
        {submitLabel}
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  input: { marginBottom: 12 },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 16 },
  sectionTitle: { marginBottom: 8 },
  ingredientRow: { flexDirection: "row", alignItems: "center", marginBottom: 8 },
  ingredientIdInput: { flex: 1, marginRight: 8 },
  ingredientQtyInput: { flex: 2 },
  submit: { marginTop: 24 },
});
