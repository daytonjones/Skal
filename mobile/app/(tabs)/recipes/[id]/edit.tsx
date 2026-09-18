import { View, ActivityIndicator } from "react-native";
import { Text } from "react-native-paper";
import { useLocalSearchParams, router, Stack } from "expo-router";
import RecipeForm from "../../../../components/RecipeForm";
import { useRecipe, useUpdateRecipe } from "../../../../hooks/useRecipes";

export default function EditRecipeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const recipeId = Number(id);
  const { data: recipe, isLoading, isError } = useRecipe(recipeId);
  const updateMutation = useUpdateRecipe(recipeId);

  if (isError) {
    return (
      <>
        <Stack.Screen options={{ title: "Edit Recipe" }} />
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <Text>Couldn't load this recipe.</Text>
        </View>
      </>
    );
  }

  if (isLoading || !recipe) {
    return (
      <>
        <Stack.Screen options={{ title: "Edit Recipe" }} />
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator />
        </View>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: "Edit Recipe" }} />
      <RecipeForm
        initial={recipe}
        submitLabel="Save changes"
        onSubmit={async (input) => {
          await updateMutation.mutateAsync(input);
          router.replace(`/recipes/${recipeId}`);
        }}
      />
    </>
  );
}
