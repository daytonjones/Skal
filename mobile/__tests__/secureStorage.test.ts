import * as SecureStore from "expo-secure-store";
import { getServerUrl, setServerUrl, getTokens, setTokens, clearTokens } from "../lib/secureStorage";

jest.mock("expo-secure-store", () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

describe("secureStorage", () => {
  beforeEach(() => jest.clearAllMocks());

  it("stores the server url", async () => {
    await setServerUrl("https://skal.example.com");
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith("skal_server_url", "https://skal.example.com");
  });

  it("retrieves the server url", async () => {
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue("https://skal.example.com");
    expect(await getServerUrl()).toBe("https://skal.example.com");
  });

  it("returns null tokens when either half is missing", async () => {
    (SecureStore.getItemAsync as jest.Mock)
      .mockResolvedValueOnce("access-token")
      .mockResolvedValueOnce(null);
    expect(await getTokens()).toBeNull();
  });

  it("returns both tokens when present", async () => {
    (SecureStore.getItemAsync as jest.Mock)
      .mockResolvedValueOnce("access-token")
      .mockResolvedValueOnce("refresh-token");
    expect(await getTokens()).toEqual({ access: "access-token", refresh: "refresh-token" });
  });

  it("stores both tokens", async () => {
    await setTokens({ access: "a", refresh: "r" });
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith("skal_access_token", "a");
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith("skal_refresh_token", "r");
  });

  it("clears both tokens", async () => {
    await clearTokens();
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("skal_access_token");
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("skal_refresh_token");
  });
});
