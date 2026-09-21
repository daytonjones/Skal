import { useQuery } from "@tanstack/react-query";
import { listYeast } from "../api/yeast";

export function useYeast() {
  return useQuery({ queryKey: ["yeast"], queryFn: listYeast, staleTime: Infinity });
}
