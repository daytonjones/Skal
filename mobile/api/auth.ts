import { apiFetch } from "../lib/apiFetch";
import { setTokens, clearTokens } from "../lib/secureStorage";
import type { Me, NotificationPrefs } from "./types";

export type LoginOutcome =
  | { ok: true }
  | { ok: false; reason: "pending_approval" }
  | { ok: false; reason: "invalid_credentials" };

export async function login(username: string, password: string): Promise<LoginOutcome> {
  try {
    const data = await apiFetch<{ access: string; refresh: string }>("/api/v1/auth/token/", {
      method: "POST",
      skipAuth: true,
      body: JSON.stringify({ username, password }),
    });
    await setTokens(data);
    return { ok: true };
  } catch (err: any) {
    if (err?.status === 400) {
      const msg = JSON.stringify(err.body ?? "");
      if (msg.includes("pending admin approval")) {
        return { ok: false, reason: "pending_approval" };
      }
    }
    return { ok: false, reason: "invalid_credentials" };
  }
}

export async function register(username: string, email: string, password: string): Promise<void> {
  await apiFetch("/api/v1/auth/register/", {
    method: "POST",
    skipAuth: true,
    body: JSON.stringify({ username, email, password }),
  });
}

export async function logout(): Promise<void> {
  await clearTokens();
}

export function getMe(): Promise<Me> {
  return apiFetch<Me>("/api/v1/auth/me/");
}

export function updateMe(
  patch: Partial<Pick<Me, "theme" | "email">> & { notification_prefs?: Partial<NotificationPrefs> }
): Promise<Me> {
  return apiFetch<Me>("/api/v1/auth/me/", {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}
