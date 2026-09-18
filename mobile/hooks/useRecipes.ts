import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as recipesApi from "../api/recipes";
import type { RecipeInput } from "../api/types";

export function useRecipes(page = 1) {
  return useQuery({
    queryKey: ["recipes", page],
    queryFn: () => recipesApi.listRecipes(page),
  });
}

export function useRecipe(id: number) {
  return useQuery({
    queryKey: ["recipes", id],
    queryFn: () => recipesApi.getRecipe(id),
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RecipeInput) => recipesApi.createRecipe(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] }),
  });
}

export function useUpdateRecipe(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RecipeInput) => recipesApi.updateRecipe(id, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      queryClient.invalidateQueries({ queryKey: ["recipes", id] });
    },
  });
}

export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => recipesApi.deleteRecipe(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] }),
  });
}

export function useCloneRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => recipesApi.cloneRecipe(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] }),
  });
}
