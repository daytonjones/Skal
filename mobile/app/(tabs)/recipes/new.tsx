import { router } from "expo-router";
import RecipeForm from "../../../components/RecipeForm";
import { useCreateRecipe } from "../../../hooks/useRecipes";

export default function NewRecipeScreen() {
  const createMutation = useCreateRecipe();

  return (
    <RecipeForm
      submitLabel="Create recipe"
      onSubmit={async (input) => {
        const recipe = await createMutation.mutateAsync(input);
        router.replace(`/recipes/${recipe.id}`);
      }}
    />
  );
}
