import { apiFetch, ApiError, NetworkError, SessionExpiredError } from "../lib/apiFetch";
import * as secureStorage from "../lib/secureStorage";

jest.mock("../lib/secureStorage");

const mockedStorage = secureStorage as jest.Mocked<typeof secureStorage>;

describe("apiFetch", () => {
  beforeEach(() => {
    jest.resetAllMocks();
    mockedStorage.getServerUrl.mockResolvedValue("https://skal.example.com");
    global.fetch = jest.fn();
  });

  it("attaches the access token and returns parsed JSON on success", async () => {
    mockedStorage.getTokens.mockResolvedValue({ access: "access-1", refresh: "refresh-1" });
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 1 }),
    });

    const result = await apiFetch<{ id: number }>("/api/v1/recipes/1/");

    const headers = (global.fetch as jest.Mock).mock.calls[0][1].headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer access-1");
    expect(result).toEqual({ id: 1 });
  });

  it("refreshes and retries once on a 401, then succeeds", async () => {
    mockedStorage.getTokens.mockResolvedValue({ access: "expired", refresh: "refresh-1" });
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access: "fresh" }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ id: 1 }) });

    const result = await apiFetch<{ id: number }>("/api/v1/recipes/1/");

    expect(result).toEqual({ id: 1 });
    expect(mockedStorage.setAccessToken).toHaveBeenCalledWith("fresh");
    expect(global.fetch).toHaveBeenCalledTimes(3);
  });

  it("clears tokens and throws SessionExpiredError when refresh fails", async () => {
    mockedStorage.getTokens.mockResolvedValue({ access: "expired", refresh: "bad-refresh" });
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) });

    await expect(apiFetch("/api/v1/recipes/")).rejects.toBeInstanceOf(SessionExpiredError);
    expect(mockedStorage.clearTokens).toHaveBeenCalled();
  });

  it("throws ApiError with the parsed body on a 400", async () => {
    mockedStorage.getTokens.mockResolvedValue({ access: "a", refresh: "r" });
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ name: ["This field is required."] }),
    });

    await expect(apiFetch("/api/v1/recipes/", { method: "POST", body: "{}" })).rejects.toMatchObject({
      status: 400,
      body: { name: ["This field is required."] },
    });
  });

  it("throws NetworkError when fetch rejects", async () => {
    mockedStorage.getTokens.mockResolvedValue({ access: "a", refresh: "r" });
    (global.fetch as jest.Mock).mockRejectedValue(new Error("offline"));

    await expect(apiFetch("/api/v1/recipes/")).rejects.toBeInstanceOf(NetworkError);
  });
});
