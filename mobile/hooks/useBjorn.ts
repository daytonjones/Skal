import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as bjornApi from "../api/bjorn";

export function useBjornMessages() {
  return useQuery({ queryKey: ["bjorn-messages"], queryFn: bjornApi.listBjornMessages });
}

export function useSendBjornMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (content: string) => bjornApi.sendBjornMessage(content),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bjorn-messages"] }),
  });
}

export function useSaveBjornRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (messageId: number) => bjornApi.saveBjornRecipe(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bjorn-messages"] });
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
    },
  });
}
