import { renderHook, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useBatches, useTastingNotes } from "../hooks/useBatches";
import * as batchesApi from "../api/batches";

jest.mock("../api/batches");
const mockedApi = batchesApi as jest.Mocked<typeof batchesApi>;

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

const baseBatch = {
  id: 1,
  recipe: null,
  name: "Test Batch",
  batch_size: "5.0",
  og: "1.090",
  fg: null,
  primary_date: "2026-01-01",
  secondary_date: null,
  bottling_date: null,
  notes: "",
  is_public: false,
  is_owner: true,
  create_must_done: false,
  create_must_date: null,
  create_must_note: "",
  pitch_yeast_done: false,
  pitch_yeast_date: null,
  pitch_yeast_note: "",
  fo_24h_done: false,
  fo_24h_date: null,
  fo_24h_note: "",
  fo_48h_done: false,
  fo_48h_date: null,
  fo_48h_note: "",
  fo_72h_done: false,
  fo_72h_date: null,
  fo_72h_note: "",
  fo_1_3_break_done: false,
  fo_1_3_break_date: null,
  fo_1_3_break_note: "",
  rack_secondary_done: false,
  rack_secondary_date: null,
  rack_secondary_note: "",
  bottled_done: false,
  bottled_date: null,
  bottled_note: "",
  bottle_count: null,
  storage_location: "",
  stage: "planned" as const,
  checklist_progress: 0,
  abv: null,
  bottles_remaining: null,
};

describe("useBatches", () => {
  beforeEach(() => jest.resetAllMocks());

  it("fetches the batch list", async () => {
    mockedApi.listBatches.mockResolvedValue({ count: 1, next: null, previous: null, results: [baseBatch] });

    const { result } = renderHook(() => useBatches(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].name).toBe("Test Batch");
  });

  it("fetches tasting notes filtered by batch", async () => {
    mockedApi.listTastingNotes.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 1, batch: 1, date: "2026-02-01", aroma: "", flavor: "", overall: "Great", score: 9 }],
    });

    const { result } = renderHook(() => useTastingNotes(1), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedApi.listTastingNotes).toHaveBeenCalledWith(1);
  });
});
