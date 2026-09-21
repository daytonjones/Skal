import { useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { Text, ActivityIndicator, Button, List, Chip, HelperText } from "react-native-paper";
import { useLocalSearchParams, router, Stack } from "expo-router";
import { useRecipe, useCloneRecipe, useDeleteRecipe } from "../../../hooks/useRecipes";
import { firstErrorMessage } from "../../../lib/errors";

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const recipeId = Number(id);
  const { data: recipe, isLoading, isError } = useRecipe(recipeId);
  const cloneMutation = useCloneRecipe();
  const deleteMutation = useDeleteRecipe();
  const [error, setError] = useState<string | null>(null);

  if (isLoading) {
    return (
      <>
        <Stack.Screen options={{ title: "Recipe" }} />
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  if (isError || !recipe) {
    return (
      <>
        <Stack.Screen options={{ title: "Recipe" }} />
        <View style={styles.center}>
          <Text>Couldn't load this recipe.</Text>
        </View>
      </>
    );
  }

  async function handleClone() {
    setError(null);
    try {
      const cloned = await cloneMutation.mutateAsync(recipeId);
      router.replace(`/recipes/${cloned.id}`);
    } catch (err) {
      setError(firstErrorMessage(err));
    }
  }

  async function handleDelete() {
    setError(null);
    try {
      await deleteMutation.mutateAsync(recipeId);
      router.back();
    } catch (err) {
      setError(firstErrorMessage(err));
    }
  }

  return (
    <>
      <Stack.Screen options={{ title: "Recipe" }} />
      <ScrollView contentContainerStyle={styles.container}>
      <Text variant="headlineMedium">{recipe.name}</Text>
      {recipe.is_public ? <Chip style={styles.chip}>Public</Chip> : null}
      <Text variant="bodyMedium" style={styles.section}>
        Batch size: {recipe.batch_size} gal
      </Text>
      <List.Section title="Ingredients">
        {recipe.recipe_ingredients.map((ri) => (
          <List.Item key={ri.id} title={ri.ingredient.name} description={ri.quantity} />
        ))}
      </List.Section>
      <Text variant="titleMedium" style={styles.section}>Instructions</Text>
      <Text variant="bodyMedium">{recipe.instructions}</Text>

      {error ? <HelperText type="error">{error}</HelperText> : null}
      <Button mode="outlined" onPress={handleClone} loading={cloneMutation.isPending} style={styles.button}>
        Clone this recipe
      </Button>
      {recipe.is_owner ? (
        <>
          <Button mode="outlined" onPress={() => router.push(`/recipes/${recipeId}/edit`)} style={styles.button}>
            Edit
          </Button>
          <Button
            mode="outlined"
            textColor="red"
            onPress={handleDelete}
            loading={deleteMutation.isPending}
            style={styles.button}
          >
            Delete
          </Button>
        </>
      ) : null}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  chip: { alignSelf: "flex-start", marginVertical: 8 },
  section: { marginTop: 16, marginBottom: 4 },
  button: { marginTop: 12 },
});
