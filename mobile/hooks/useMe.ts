import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMe, updateMe } from "../api/auth";
import type { Me, NotificationPrefs } from "../api/types";

export function useMe() {
  return useQuery({ queryKey: ["me"], queryFn: getMe });
}

export function useUpdateMe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (patch: Partial<Pick<Me, "theme" | "email">> & { notification_prefs?: Partial<NotificationPrefs> }) =>
      updateMe(patch),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["me"] }),
  });
}
