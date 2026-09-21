import * as SecureStore from "expo-secure-store";

const SERVER_URL_KEY = "skal_server_url";
const ACCESS_TOKEN_KEY = "skal_access_token";
const REFRESH_TOKEN_KEY = "skal_refresh_token";

export async function getServerUrl(): Promise<string | null> {
  return SecureStore.getItemAsync(SERVER_URL_KEY);
}

export async function setServerUrl(url: string): Promise<void> {
  await SecureStore.setItemAsync(SERVER_URL_KEY, url);
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export async function getTokens(): Promise<TokenPair | null> {
  const [access, refresh] = await Promise.all([
    SecureStore.getItemAsync(ACCESS_TOKEN_KEY),
    SecureStore.getItemAsync(REFRESH_TOKEN_KEY),
  ]);
  if (!access || !refresh) return null;
  return { access, refresh };
}

export async function setTokens(tokens: TokenPair): Promise<void> {
  await Promise.all([
    SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access),
    SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh),
  ]);
}

export async function setAccessToken(access: string): Promise<void> {
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, access);
}

export async function clearTokens(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY),
    SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY),
  ]);
}
