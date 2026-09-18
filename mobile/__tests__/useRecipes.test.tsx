import { renderHook, waitFor } from "@testing-library/react-native";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useRecipes, useCreateRecipe } from "../hooks/useRecipes";
import * as recipesApi from "../api/recipes";

jest.mock("../api/recipes");
const mockedApi = recipesApi as jest.Mocked<typeof recipesApi>;

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("useRecipes", () => {
  beforeEach(() => jest.resetAllMocks());

  it("fetches the recipe list", async () => {
    mockedApi.listRecipes.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 1, name: "Mead", batch_size: "5.0", instructions: "", is_public: false, is_owner: true, recipe_ingredients: [] }],
    });

    const { result } = renderHook(() => useRecipes(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].name).toBe("Mead");
    expect(mockedApi.listRecipes).toHaveBeenCalledWith(1);
  });

  it("creates a recipe via the mutation", async () => {
    mockedApi.createRecipe.mockResolvedValue({
      id: 2,
      name: "New",
      batch_size: "5.0",
      instructions: "",
      is_public: false,
      is_owner: true,
      recipe_ingredients: [],
    });

    const { result } = renderHook(() => useCreateRecipe(), { wrapper });
    await result.current.mutateAsync({
      name: "New",
      batch_size: "5.0",
      instructions: "",
      is_public: false,
      recipe_ingredients: [],
    });

    expect(mockedApi.createRecipe).toHaveBeenCalled();
  });
});
