import { apiFetch } from "../lib/apiFetch";
import type { Paginated, PantryItem, PantryItemInput } from "./types";

export function listPantry(page = 1): Promise<Paginated<PantryItem>> {
  return apiFetch<Paginated<PantryItem>>(`/api/v1/pantry/?page=${page}`);
}

export function createPantryItem(input: PantryItemInput): Promise<PantryItem> {
  return apiFetch<PantryItem>("/api/v1/pantry/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updatePantryItem(id: number, input: Partial<PantryItemInput>): Promise<PantryItem> {
  return apiFetch<PantryItem>(`/api/v1/pantry/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deletePantryItem(id: number): Promise<void> {
  return apiFetch<void>(`/api/v1/pantry/${id}/`, { method: "DELETE" });
}
