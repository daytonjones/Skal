def calculate_abv(og: float, fg: float) -> float:
    # standard: ABV = (76.08*(OG-FG)/(1.775-OG)) * (FG/0.794)
    return (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)

def calculate_calories(og: float, fg: float, volume_ml: float) -> float:
    abv = calculate_abv(og, fg)
    grams_alcohol = (volume_ml * abv * 8) / 1000
    return grams_alcohol * 7  # 7 cal/g

def sna_schedule(og: float, desired_fg: float) -> dict:
    # Example staggered nutrient schedule
    delta = og - desired_fg
    return {
        "starter": 2.5,
        "24h": round(delta * 0.2, 2),
        "48h": round(delta * 0.3, 2),
        "72h": round(delta * 0.5, 2),
    }

