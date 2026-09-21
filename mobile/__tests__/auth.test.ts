import { login } from "../api/auth";
import { apiFetch } from "../lib/apiFetch";
import { setTokens } from "../lib/secureStorage";

jest.mock("../lib/apiFetch");
jest.mock("../lib/secureStorage");

const mockedApiFetch = apiFetch as jest.Mock;
const mockedSetTokens = setTokens as jest.Mock;

describe("login", () => {
  beforeEach(() => jest.resetAllMocks());

  it("returns ok and stores tokens on success", async () => {
    mockedApiFetch.mockResolvedValue({ access: "a", refresh: "r" });
    const result = await login("user", "pass");
    expect(result).toEqual({ ok: true });
    expect(mockedSetTokens).toHaveBeenCalledWith({ access: "a", refresh: "r" });
  });

  it("returns pending_approval when the server reports a pending admin approval", async () => {
    const ApiError = jest.requireActual("../lib/apiFetch").ApiError;
    mockedApiFetch.mockRejectedValue(
      new ApiError(400, { detail: "Your account is pending admin approval." })
    );
    const result = await login("user", "pass");
    expect(result).toEqual({ ok: false, reason: "pending_approval" });
  });

  it("returns invalid_credentials on a generic 400", async () => {
    const ApiError = jest.requireActual("../lib/apiFetch").ApiError;
    mockedApiFetch.mockRejectedValue(new ApiError(400, { detail: "No active account found." }));
    const result = await login("user", "pass");
    expect(result).toEqual({ ok: false, reason: "invalid_credentials" });
  });
});
