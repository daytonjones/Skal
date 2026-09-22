import {
  abvStandard,
  abvAlternate,
  caloriesPerGlass,
  attenuation,
  brixToSG,
  sgToBrix,
  nFactorFor,
  DEFAULT_N_FACTOR,
  tosnaSchedule,
  batchBuilder,
} from "../lib/calculators";

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

describe("attenuation", () => {
  it("computes attenuation for a known OG/FG pair", () => {
    // (1.090 - 1.000) / (1.090 - 1) * 100 = 100
    expect(attenuation(1.09, 1.0)).toBeCloseTo(100, 5);
    // (1.090 - 1.020) / (1.090 - 1) * 100 = 77.777...
    expect(attenuation(1.09, 1.02)).toBeCloseTo(77.7778, 3);
  });
});

describe("brix/SG conversion", () => {
  it("round-trips sgToBrix(brixToSG(x)) back to x within tolerance", () => {
    for (const brix of [0, 5, 10, 20, 25, 30]) {
      const sg = brixToSG(brix);
      const roundTripped = sgToBrix(sg);
      expect(roundTripped).toBeCloseTo(brix, 1);
    }
  });

  it("converts a known SG reference point to Brix", () => {
    // SG of 1.000 (pure water) should be ~0 Brix.
    expect(sgToBrix(1.0)).toBeCloseTo(0, 0);
  });
});

describe("nFactorFor", () => {
  it("returns the mapped N-factor for a known yeast", () => {
    expect(nFactorFor("Lalvin EC-1118")).toBeCloseTo(0.75, 5);
    expect(nFactorFor("Lalvin BOURGOVIN RC 212")).toBeCloseTo(1.25, 5);
  });

  it("falls back to DEFAULT_N_FACTOR for an unknown yeast", () => {
    expect(nFactorFor("Some Unknown Yeast Strain")).toBe(DEFAULT_N_FACTOR);
  });
});

describe("tosnaSchedule", () => {
  it("produces 5 additions with the first at 0g and the remaining 4 equal", () => {
    const schedule = tosnaSchedule(1.09, 1.0, 5, "Lalvin EC-1118", "FO");
    expect(schedule.additions).toHaveLength(5);
    expect(schedule.additions[0].grams).toBe(0);
    const rest = schedule.additions.slice(1).map((a) => a.grams);
    rest.forEach((g) => expect(g).toBeCloseTo(rest[0], 6));
    expect(rest[0]).toBeGreaterThan(0);
  });

  it("multiplies total nutrient by 0.6 for Fermaid K vs Fermaid O", () => {
    const fo = tosnaSchedule(1.09, 1.0, 5, "Lalvin EC-1118", "FO");
    const fk = tosnaSchedule(1.09, 1.0, 5, "Lalvin EC-1118", "FK");
    expect(fk.totalNutrientG).toBeCloseTo(fo.totalNutrientG * 0.6, 5);
  });
});

describe("batchBuilder", () => {
  it("produces a positive honey amount for a reasonable target ABV/batch size", () => {
    const result = batchBuilder(5, 12, "Lalvin EC-1118", "FO");
    expect(result.honeyLbs).toBeGreaterThan(0);
    expect(result.estimatedOgSG).toBeGreaterThan(1.0);
    expect(result.totalNutrientG).toBeGreaterThan(0);
  });
});
