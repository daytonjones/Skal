import { apiFetch } from "../lib/apiFetch";

export function getServerVersion(): Promise<{ version: string }> {
  return apiFetch<{ version: string }>("/api/v1/version/", { skipAuth: true });
}
