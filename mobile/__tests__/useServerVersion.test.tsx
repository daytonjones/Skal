import { renderHook, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useServerVersion } from "../hooks/useServerVersion";
import * as versionApi from "../api/version";

jest.mock("../api/version");
const mockedApi = versionApi as jest.Mocked<typeof versionApi>;

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("useServerVersion", () => {
  beforeEach(() => jest.resetAllMocks());

  it("fetches the server's reported version", async () => {
    mockedApi.getServerVersion.mockResolvedValue({ version: "2.2.0" });

    const { result } = renderHook(() => useServerVersion(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.version).toBe("2.2.0");
  });

  it("settles into an error state without throwing when the endpoint fails", async () => {
    mockedApi.getServerVersion.mockRejectedValue(new Error("Not Found"));

    const { result } = renderHook(() => useServerVersion(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
  });
});
