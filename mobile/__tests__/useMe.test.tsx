import { renderHook, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useMe, useUpdateMe } from "../hooks/useMe";
import * as authApi from "../api/auth";

jest.mock("../api/auth");
const mockedApi = authApi as jest.Mocked<typeof authApi>;

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("useMe", () => {
  beforeEach(() => jest.resetAllMocks());

  it("fetches the current user's profile", async () => {
    mockedApi.getMe.mockResolvedValue({
      id: 1,
      username: "admin",
      email: "admin@example.com",
      theme: "dark",
      is_approved: true,
      notification_prefs: null,
    });

    const { result } = renderHook(() => useMe(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.username).toBe("admin");
  });

  it("updates the profile via the mutation", async () => {
    mockedApi.updateMe.mockResolvedValue({
      id: 1,
      username: "admin",
      email: "admin@example.com",
      theme: "light",
      is_approved: true,
      notification_prefs: null,
    });

    const { result } = renderHook(() => useUpdateMe(), { wrapper });
    await result.current.mutateAsync({ theme: "light" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockedApi.updateMe).toHaveBeenCalledWith({ theme: "light" });
  });
});
