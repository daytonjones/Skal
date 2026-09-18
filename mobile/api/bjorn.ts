import { apiFetch } from "../lib/apiFetch";
import type { Paginated, ChatMessage, Recipe } from "./types";

export function listBjornMessages(): Promise<Paginated<ChatMessage>> {
  return apiFetch<Paginated<ChatMessage>>("/api/v1/bjorn/messages/");
}

export function sendBjornMessage(content: string): Promise<ChatMessage> {
  return apiFetch<ChatMessage>("/api/v1/bjorn/messages/", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function saveBjornRecipe(messageId: number): Promise<Recipe> {
  return apiFetch<Recipe>(`/api/v1/bjorn/messages/${messageId}/save-recipe/`, {
    method: "POST",
  });
}
