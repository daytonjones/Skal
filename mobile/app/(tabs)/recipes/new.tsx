import { router, Stack } from "expo-router";
import RecipeForm from "../../../components/RecipeForm";
import { useCreateRecipe } from "../../../hooks/useRecipes";

export default function NewRecipeScreen() {
  const createMutation = useCreateRecipe();

  return (
    <>
      <Stack.Screen options={{ title: "New Recipe" }} />
      <RecipeForm
        submitLabel="Create recipe"
        onSubmit={async (input) => {
          const recipe = await createMutation.mutateAsync(input);
          router.replace(`/recipes/${recipe.id}`);
        }}
      />
    </>
  );
}
