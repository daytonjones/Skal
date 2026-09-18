import { abvStandard, abvAlternate, caloriesPerGlass } from "../lib/calculators";

describe("calculators", () => {
  it("computes standard ABV", () => {
    expect(abvStandard(1.09, 1.0)).toBeCloseTo(11.8125, 3);
  });

  it("computes alternate ABV", () => {
    expect(abvAlternate(1.09, 1.0)).toBeCloseTo(12.589, 2);
  });

  it("computes calories for a 5oz glass", () => {
    const calories = caloriesPerGlass(12, 5);
    expect(calories).toBeCloseTo(97.96, 1);
  });
});
