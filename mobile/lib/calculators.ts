export function abvStandard(og: number, fg: number): number {
  return (og - fg) * 131.25;
}

export function abvAlternate(og: number, fg: number): number {
  return (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794);
}

export function caloriesPerGlass(abvPercent: number, glassOz = 5): number {
  return ((abvPercent / 100) * 0.789 * 7) * (glassOz * 29.5735);
}
