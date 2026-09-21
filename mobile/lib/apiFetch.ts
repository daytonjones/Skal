import { getServerUrl, getTokens, setTokens, clearTokens } from "./secureStorage";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(
      typeof body === "object" && body && "detail" in (body as any)
        ? String((body as any).detail)
        : "Request failed"
    );
    this.status = status;
    this.body = body;
  }
}

export class NetworkError extends Error {
  constructor() {
    super("Network request failed");
  }
}

export class SessionExpiredError extends Error {
  constructor() {
    super("Session expired");
  }
}

let sessionExpiredHandler: (() => void) | null = null;
export function setSessionExpiredHandler(handler: () => void): void {
  sessionExpiredHandler = handler;
}

interface ApiFetchOptions extends RequestInit {
  skipAuth?: boolean;
}

async function doFetch(url: string, options: ApiFetchOptions, accessToken: string | null): Promise<Response> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken && !options.skipAuth) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  try {
    return await fetch(url, { ...options, headers });
  } catch {
    throw new NetworkError();
  }
}

async function refreshAccessToken(serverUrl: string, refresh: string): Promise<{ access: string; refresh: string } | null> {
  try {
    const res = await fetch(`${serverUrl}/api/v1/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return { access: data.access as string, refresh: data.refresh as string };
  } catch {
    return null;
  }
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const serverUrl = await getServerUrl();
  if (!serverUrl) throw new Error("No server configured");

  const tokens = options.skipAuth ? null : await getTokens();
  let response = await doFetch(`${serverUrl}${path}`, options, tokens?.access ?? null);

  if (response.status === 401 && tokens && !options.skipAuth) {
    const refreshed = await refreshAccessToken(serverUrl, tokens.refresh);
    if (!refreshed) {
      await clearTokens();
      sessionExpiredHandler?.();
      throw new SessionExpiredError();
    }
    await setTokens(refreshed);
    response = await doFetch(`${serverUrl}${path}`, options, refreshed.access);
    if (response.status === 401) {
      await clearTokens();
      sessionExpiredHandler?.();
      throw new SessionExpiredError();
    }
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(response.status, body);
  }

  return body as T;
}
