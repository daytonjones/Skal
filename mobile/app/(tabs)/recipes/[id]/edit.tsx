import { View, ActivityIndicator } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import RecipeForm from "../../../../components/RecipeForm";
import { useRecipe, useUpdateRecipe } from "../../../../hooks/useRecipes";

export default function EditRecipeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const recipeId = Number(id);
  const { data: recipe, isLoading } = useRecipe(recipeId);
  const updateMutation = useUpdateRecipe(recipeId);

  if (isLoading || !recipe) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <RecipeForm
      initial={recipe}
      submitLabel="Save changes"
      onSubmit={async (input) => {
        await updateMutation.mutateAsync(input);
        router.replace(`/recipes/${recipeId}`);
      }}
    />
  );
}
