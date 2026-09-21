import { apiFetch } from "../lib/apiFetch";
import type { Paginated, Recipe, RecipeInput } from "./types";

export function listRecipes(page = 1): Promise<Paginated<Recipe>> {
  return apiFetch<Paginated<Recipe>>(`/api/v1/recipes/?page=${page}`);
}

export function getRecipe(id: number): Promise<Recipe> {
  return apiFetch<Recipe>(`/api/v1/recipes/${id}/`);
}

export function createRecipe(input: RecipeInput): Promise<Recipe> {
  return apiFetch<Recipe>("/api/v1/recipes/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateRecipe(id: number, input: RecipeInput): Promise<Recipe> {
  return apiFetch<Recipe>(`/api/v1/recipes/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteRecipe(id: number): Promise<void> {
  return apiFetch<void>(`/api/v1/recipes/${id}/`, { method: "DELETE" });
}

export function cloneRecipe(id: number): Promise<Recipe> {
  return apiFetch<Recipe>(`/api/v1/recipes/${id}/clone/`, { method: "POST" });
}
