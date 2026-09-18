import { useQuery } from "@tanstack/react-query";
import { getServerVersion } from "../api/version";

export function useServerVersion() {
  return useQuery({
    queryKey: ["server-version"],
    queryFn: getServerVersion,
    retry: false,
    staleTime: Infinity,
  });
}
