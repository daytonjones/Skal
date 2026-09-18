import { renderHook, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useBjornMessages, useSendBjornMessage } from "../hooks/useBjorn";
import * as bjornApi from "../api/bjorn";

jest.mock("../api/bjorn");
const mockedApi = bjornApi as jest.Mocked<typeof bjornApi>;

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("useBjorn", () => {
  beforeEach(() => jest.resetAllMocks());

  it("fetches the message list", async () => {
    mockedApi.listBjornMessages.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 1, role: "assistant", content: "Skål!", pending_recipe: null, created_at: "2026-01-01T00:00:00Z" }],
    });

    const { result } = renderHook(() => useBjornMessages(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].content).toBe("Skål!");
  });

  it("sends a message via the mutation", async () => {
    mockedApi.sendBjornMessage.mockResolvedValue({
      id: 2,
      role: "assistant",
      content: "Try adding cinnamon.",
      pending_recipe: null,
      created_at: "2026-01-01T00:00:00Z",
    });

    const { result } = renderHook(() => useSendBjornMessage(), { wrapper });
    await result.current.mutateAsync("Any tips for spiced mead?");

    expect(mockedApi.sendBjornMessage).toHaveBeenCalledWith("Any tips for spiced mead?");
  });
});
