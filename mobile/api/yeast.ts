import { apiFetch } from "../lib/apiFetch";
import type { Yeast } from "./types";

export function listYeast(): Promise<Yeast[]> {
  return apiFetch<Yeast[]>("/api/v1/yeast/");
}
