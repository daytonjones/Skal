import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as batchesApi from "../api/batches";
import type { BatchInput, TastingNoteInput, BottleConsumptionInput } from "../api/types";

export function useBatches(page = 1) {
  return useQuery({ queryKey: ["batches", page], queryFn: () => batchesApi.listBatches(page) });
}

export function useBatch(id: number) {
  return useQuery({
    queryKey: ["batches", id],
    queryFn: () => batchesApi.getBatch(id),
    enabled: !!id,
  });
}

export function useCreateBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<BatchInput>) => batchesApi.createBatch(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["batches"] }),
  });
}

export function useUpdateBatch(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<BatchInput>) => batchesApi.updateBatch(id, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      queryClient.invalidateQueries({ queryKey: ["batches", id] });
    },
  });
}

export function useDeleteBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => batchesApi.deleteBatch(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["batches"] }),
  });
}

export function useTastingNotes(batchId: number) {
  return useQuery({
    queryKey: ["tasting-notes", batchId],
    queryFn: () => batchesApi.listTastingNotes(batchId),
    enabled: !!batchId,
  });
}

export function useCreateTastingNote(batchId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: TastingNoteInput) => batchesApi.createTastingNote(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasting-notes", batchId] }),
  });
}

export function useBottleConsumption(batchId: number) {
  return useQuery({
    queryKey: ["bottle-consumption", batchId],
    queryFn: () => batchesApi.listBottleConsumption(batchId),
    enabled: !!batchId,
  });
}

export function useCreateBottleConsumption(batchId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: BottleConsumptionInput) => batchesApi.createBottleConsumption(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bottle-consumption", batchId] });
      queryClient.invalidateQueries({ queryKey: ["batches", batchId] });
    },
  });
}

export function useBatchImages(batchId: number) {
  return useQuery({
    queryKey: ["batch-images", batchId],
    queryFn: () => batchesApi.listBatchImages(batchId),
    enabled: !!batchId,
  });
}

export function useUploadBatchImage(batchId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ uri, caption }: { uri: string; caption: string }) =>
      batchesApi.uploadBatchImage(batchId, uri, caption),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["batch-images", batchId] }),
  });
}
