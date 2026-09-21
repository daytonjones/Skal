export function abvStandard(og: number, fg: number): number {
  return (og - fg) * 131.25;
}

export function abvAlternate(og: number, fg: number): number {
  return (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794);
}

export function caloriesPerGlass(abvPercent: number, glassOz = 5): number {
  return ((abvPercent / 100) * 0.789 * 7) * (glassOz * 29.5735);
}

export function attenuation(og: number, fg: number): number {
  return ((og - fg) / (og - 1)) * 100;
}

export function brixToSG(brix: number): number {
  return brix / (258.6 - (brix / 258.2) * 227.1) + 1;
}

// Transcribed verbatim from static/js/calculators.js's sgToBrix. Note this is a
// cubic in sg (three nested multiplications) — not the same as a naive reading
// of `(182.4601*sg - 775.6821)*sg + 1262.7794*sg - 669.5622` would produce.
export function sgToBrix(sg: number): number {
  return ((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622;
}

export type NutrientType = "FO" | "FK";

const N_LOW = 0.75;
const N_MED = 0.9;
const N_HIGH = 1.25;
export const DEFAULT_N_FACTOR = N_HIGH; // matches web's `|| 1.25` fallback for unknown yeast

// Transcribed verbatim from static/js/calculators.js's YEAST_N_FACTORS.
export const YEAST_N_FACTORS: Record<string, number> = {
  "Lalvin 71-B": N_LOW,
  "Lalvin BOURGOVIN RC 212": N_HIGH,
  "Lalvin EC-1118": N_LOW,
  "Lalvin ICV D-47": N_LOW,
  "Lalvin KIV-1116": N_LOW,
  "Lalvin K1V-1116": N_LOW,
  "Red Star Cote des Blancs": N_MED,
  "Red Star Flor Sherry": N_MED,
  "Red Star Montrachet (Premier Classique)": N_MED,
  "Red Star Pasteur Champagne (Premier Blanc)": N_LOW,
  "Red Star Pasteur Red (Premier Rouge)": N_HIGH,
  "Red Star Premier Cuvée": N_LOW,
  "Vintner’s Harvest Saccharomyces Bayanus #1": N_MED,
  "Vintner’s Harvest Saccharomyces Bayanus #2": N_MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #1": N_MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #2": N_MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #3": N_MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #4": N_MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #5": N_MED,
  "White Labs Assmanshausen Wine Yeast": N_MED,
  "White Labs Avise Wine Yeast": N_MED,
  "White Labs Cabernet Red Wine Yeast": N_MED,
  "White Labs Champagne": N_LOW,
  "White Labs Chardonnay White Wine": N_MED,
  "White Labs English Cider": N_MED,
  "White Labs French Red Wine Yeast": N_MED,
  "White Labs French White Wine Yeast": N_MED,
  "White Labs Merlot Red Wine Yeast": N_MED,
  "White Labs Steinberg-Geisenheim Wine Yeast": N_MED,
  "White Labs Suremain Burgundy Wine Yeast": N_MED,
  "White Labs Sweet Mead and Wine": N_MED,
  "Wyeast Bordeaux": N_MED,
  "Wyeast Chablis": N_MED,
  "Wyeast Chateau": N_MED,
  "Wyeast Chianti": N_MED,
  "Wyeast Cider": N_MED,
  "Wyeast Dry Mead": N_MED,
  "Wyeast Eau de Vie": N_HIGH,
  "Wyeast Pasteur Champagne": N_LOW,
  "Wyeast Portwine": N_MED,
  "Wyeast Rudesheimer": N_MED,
  "Wyeast Sake #9": N_HIGH,
  "Wyeast Sweet Mead": N_MED,
  "Wyeast Zinfandel": N_MED,
};

export function nFactorFor(yeastName: string): number {
  return YEAST_N_FACTORS[yeastName] ?? DEFAULT_N_FACTOR;
}

export interface TosnaSchedule {
  nFactor: number;
  pitchRateRange: string; // e.g. "1.00–1.50 g/gal"
  yeastNeededRange: string; // e.g. "5.00–7.50 g"
  totalNutrientG: number;
  additions: Array<{ label: string; grams: number }>; // 5 rows: pitch (0g) + 4 equal additions
}

// TOSNA schedule. og/fg are SG. batchSizeGal, nutrient type, yeastName.
export function tosnaSchedule(
  og: number,
  fg: number,
  batchSizeGal: number,
  yeastName: string,
  nutrient: NutrientType
): TosnaSchedule {
  const obrix = sgToBrix(og);
  const nFactor = nFactorFor(yeastName);
  const pitchRateNormal = 1.0;
  const pitchRateRobust = 1.5;
  const yeastNeededNormal = pitchRateNormal * batchSizeGal;
  const yeastNeededRobust = pitchRateRobust * batchSizeGal;

  let totalNutrient = (obrix * 10 * nFactor) / 50 * batchSizeGal;
  if (nutrient === "FK") totalNutrient *= 0.6;
  const additionAmt = totalNutrient / 4;
  const sugarBreakSG = og - (og - fg) / 3;

  return {
    nFactor,
    pitchRateRange: `${pitchRateNormal.toFixed(2)}–${pitchRateRobust.toFixed(2)} g/gal`,
    yeastNeededRange: `${yeastNeededNormal.toFixed(2)}–${yeastNeededRobust.toFixed(2)} g`,
    totalNutrientG: totalNutrient,
    additions: [
      { label: "Yeast pitch", grams: 0 },
      { label: "24 h", grams: additionAmt },
      { label: "48 h", grams: additionAmt },
      { label: "72 h", grams: additionAmt },
      { label: `1/3 Sugar Break (SG = ${sugarBreakSG.toFixed(3)})`, grams: additionAmt },
    ],
  };
}

export interface BatchBuilderResult {
  honeyLbs: number;
  estimatedOgSG: number;
  totalNutrientG: number;
  yeastNeededRange: string;
}

// Batch Builder: given a desired ABV and batch size, estimate honey needed and nutrient schedule.
// fgAssumed defaults to 1.000 to match the web's fallback when no FG is set elsewhere.
export function batchBuilder(
  batchSizeGal: number,
  desiredAbv: number,
  yeastName: string,
  nutrient: NutrientType,
  fgAssumed = 1.0
): BatchBuilderResult {
  const honeyLbs = ((desiredAbv / 131.25) * 1000 * batchSizeGal) / 35;
  const ogEstimated = desiredAbv / 131.25 + fgAssumed;
  const obrixEstimated = sgToBrix(ogEstimated);
  const nFactor = nFactorFor(yeastName);
  let totalNutrient = (obrixEstimated * 10 * nFactor) / 50 * batchSizeGal;
  if (nutrient === "FK") totalNutrient *= 0.6;
  const pitchRateNormal = 1.0;
  const pitchRateRobust = 1.5;
  return {
    honeyLbs,
    estimatedOgSG: ogEstimated,
    totalNutrientG: totalNutrient,
    yeastNeededRange: `${(pitchRateNormal * batchSizeGal).toFixed(2)}–${(pitchRateRobust * batchSizeGal).toFixed(2)} g (1.00–1.50 g/gal)`,
  };
}

export interface SweetnessLevel {
  label: string;
  sgRange: string;
  abvMin: number;
  abvMax: number;
}

export const SWEETNESS_LEVELS: SweetnessLevel[] = [
  { label: "Dry", sgRange: "1.000–1.010", abvMin: 15.1, abvMax: 16.4 },
  { label: "Off-dry", sgRange: "1.011–1.020", abvMin: 13.8, abvMax: 15.0 },
  { label: "Semi-sweet", sgRange: "1.021–1.035", abvMin: 11.8, abvMax: 13.7 },
  { label: "Sweet", sgRange: "1.036–1.060", abvMin: 8.5, abvMax: 11.7 },
  { label: "Sack", sgRange: "1.061–1.125", abvMin: 0.0, abvMax: 8.4 },
];
