import { ApiError } from "./apiFetch";

export function firstErrorMessage(err: unknown, fallback = "Something went wrong. Please try again."): string {
  if (err instanceof ApiError && err.body && typeof err.body === "object") {
    const values = Object.values(err.body as Record<string, unknown>);
    const first = values[0];
    if (Array.isArray(first) && typeof first[0] === "string") return first[0];
    if (typeof first === "string") return first;
  }
  return fallback;
}
