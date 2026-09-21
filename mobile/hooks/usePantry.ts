import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as pantryApi from "../api/pantry";
import type { PantryItemInput } from "../api/types";

export function usePantry(page = 1) {
  return useQuery({ queryKey: ["pantry", page], queryFn: () => pantryApi.listPantry(page) });
}

export function useCreatePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: PantryItemInput) => pantryApi.createPantryItem(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pantry"] }),
  });
}

export function useUpdatePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: Partial<PantryItemInput> }) =>
      pantryApi.updatePantryItem(id, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pantry"] }),
  });
}

export function useDeletePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => pantryApi.deletePantryItem(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pantry"] }),
  });
}
