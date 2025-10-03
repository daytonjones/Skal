// static/js/calculators.js

// TOSNA factors
const N = { LOW: 0.75, MED: 0.90, HIGH: 1.25 };

// Yeast → N-factor mapping (corrected)
const YEAST_N_FACTORS = {
  // Lalvin / Lallemand
  "Lalvin 71-B": N.LOW,
  "Lalvin BOURGOVIN RC 212": N.HIGH,
  "Lalvin EC-1118": N.LOW,
  "Lalvin ICV D-47": N.LOW,
  "Lalvin KIV-1116": N.LOW,
  "Lalvin K1V-1116": N.LOW,

  // Red Star
  "Red Star Cote des Blancs": N.MED,
  "Red Star Flor Sherry": N.MED,
  "Red Star Montrachet (Premier Classique)": N.MED,
  "Red Star Pasteur Champagne (Premier Blanc)": N.LOW,
  "Red Star Pasteur Red (Premier Rouge)": N.HIGH,
  "Red Star Premier Cuvée": N.LOW,

  // Vintner’s Harvest
  "Vintner’s Harvest Saccharomyces Bayanus #1": N.MED,
  "Vintner’s Harvest Saccharomyces Bayanus #2": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #1": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #2": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #3": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #4": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #5": N.MED,

  // White Labs
  "White Labs Assmanshausen Wine Yeast": N.MED,
  "White Labs Avise Wine Yeast": N.MED,
  "White Labs Cabernet Red Wine Yeast": N.MED,
  "White Labs Champagne": N.LOW,
  "White Labs Chardonnay White Wine": N.MED,
  "White Labs English Cider": N.MED,
  "White Labs French Red Wine Yeast": N.MED,
  "White Labs French White Wine Yeast": N.MED,
  "White Labs Merlot Red Wine Yeast": N.MED,
  "White Labs Steinberg-Geisenheim Wine Yeast": N.MED,
  "White Labs Suremain Burgundy Wine Yeast": N.MED,
  "White Labs Sweet Mead and Wine": N.MED,

  // Wyeast
  "Wyeast Bordeaux": N.MED,
  "Wyeast Chablis": N.MED,
  "Wyeast Chateau": N.MED,
  "Wyeast Chianti": N.MED,
  "Wyeast Cider": N.MED,
  "Wyeast Dry Mead": N.MED,
  "Wyeast Eau de Vie": N.HIGH,
  "Wyeast Pasteur Champagne": N.LOW,
  "Wyeast Portwine": N.MED,
  "Wyeast Rudesheimer": N.MED,
  "Wyeast Sake #9": N.HIGH,
  "Wyeast Sweet Mead": N.MED,
  "Wyeast Zinfandel": N.MED,
};

// Round a number to two decimal places and return as string
const to2 = x => (Math.round(x * 100) / 100).toFixed(2);

// Convert a decimal teaspoon value to the nearest common fraction or decimal
function decimalToFraction(x) {
  const FRACTIONS = [
    [1/8, "1/8"], [1/6, "1/6"], [1/4, "1/4"], [1/3, "1/3"],
    [3/8, "3/8"], [1/2, "1/2"], [5/8, "5/8"], [2/3, "2/3"],
    [3/4, "3/4"], [7/8, "7/8"]
  ];
  let best = { diff: Infinity, label: "" };
  for (let [val, label] of FRACTIONS) {
    const diff = Math.abs(x - val);
    if (diff < best.diff) best = { diff, label };
  }
  return best.diff <= 0.05 ? best.label : to2(x);
}

// Convert Brix to Specific Gravity
function brixToSG(b) {
  return (b / (258.6 - ((b / 258.2) * 227.1))) + 1;
}

// Convert Specific Gravity to Brix
function sgToBrix(sg) {
  return ((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622;
}

// Populate the sweetness levels table based on an ABV value
function updateSweetTable(abv) {
  const levels = [
    ['Dry',        '1.000–1.010', '15.1–16.4'],
    ['Off-dry',    '1.011–1.020', '13.8–15.0'],
    ['Semi-sweet', '1.021–1.035', '11.8–13.7'],
    ['Sweet',      '1.036–1.060', '8.5–11.7'],
    ['Sack',       '1.061–1.125', '0.0–8.4']
  ];
  document.getElementById('sweet-body').innerHTML = levels.map(([lvl, sgR, abvR]) => {
    const [minABV, maxABV] = abvR.split('–').map(parseFloat);
    const cls = (abv >= minABV && abv <= maxABV) ? ' class="highlight"' : '';
    return `<tr${cls}>
      <td>${lvl}</td>
      <td>${sgR}</td>
      <td>${abvR}%</td>
    </tr>`;
  }).join('');
}

// Guard to prevent infinite loop between SG <-> Brix updates
let isSyncing = false;

// -------- SG Calculator --------
function updateSG() {
  if (isSyncing) return;
  isSyncing = true;

  const og = parseFloat(document.getElementById('og-sg').value);
  const fg = parseFloat(document.getElementById('fg-sg').value);
  const formula = document.querySelector('input[name="abv-formula"]:checked').value;

  let abv = formula === 'standard'
    ? (og - fg) * 131.25
    : (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794);

  const attenuation = ((og - fg) / (og - 1)) * 100;

  // SG calories
  const glassSG = parseFloat(document.getElementById('glass-size-sg').value);
  const caloriesSG = ((abv / 100) * 0.789 * 7) * (glassSG * 29.5735);

  document.getElementById('og-sg-val').textContent   = og.toFixed(3);
  document.getElementById('fg-sg-val').textContent   = fg.toFixed(3);
  document.getElementById('abv-sg').textContent      = to2(abv) + '%';
  document.getElementById('att-sg').textContent      = to2(attenuation) + '%';
  document.getElementById('calories-sg').textContent = to2(caloriesSG);

  // Sync Brix sliders
  const ogBrix = sgToBrix(og);
  const fgBrix = sgToBrix(fg);
  document.getElementById('og-brix').value = ogBrix.toFixed(1);
  document.getElementById('fg-brix').value = fgBrix.toFixed(1);

  // Also update Brix display
  const glassBx = parseFloat(document.getElementById('glass-size-bx').value);
  const caloriesBx = ((abv / 100) * 0.789 * 7) * (glassBx * 29.5735);
  document.getElementById('og-brix-val').textContent = ogBrix.toFixed(1);
  document.getElementById('fg-brix-val').textContent = fgBrix.toFixed(1);
  document.getElementById('abv-bx').textContent      = to2(abv) + '%';
  document.getElementById('att-bx').textContent      = to2(attenuation) + '%';
  document.getElementById('calories-bx').textContent = to2(caloriesBx);

  updateSweetTable(abv);
  updateSNA();

  isSyncing = false;
}

// -------- Brix Calculator --------
function updateBx() {
  if (isSyncing) return;
  isSyncing = true;

  const obx = parseFloat(document.getElementById('og-brix').value);
  const fbx = parseFloat(document.getElementById('fg-brix').value);
  const ogSG = brixToSG(obx);
  const fgSG = brixToSG(fbx);

  const abv = (ogSG - fgSG) * 131.25;
  const attenuation = ((ogSG - fgSG) / (ogSG - 1)) * 100;

  // Brix calories
  const glassBx = parseFloat(document.getElementById('glass-size-bx').value);
  const caloriesBx = ((abv / 100) * 0.789 * 7) * (glassBx * 29.5735);

  document.getElementById('og-brix-val').textContent = obx.toFixed(1);
  document.getElementById('fg-brix-val').textContent = fbx.toFixed(1);
  document.getElementById('abv-bx').textContent      = to2(abv) + '%';
  document.getElementById('att-bx').textContent      = to2(attenuation) + '%';
  document.getElementById('calories-bx').textContent = to2(caloriesBx);

  // Sync SG sliders
  document.getElementById('og-sg').value = ogSG.toFixed(3);
  document.getElementById('fg-sg').value = fgSG.toFixed(3);

  // Also update SG display
  const glassSG = parseFloat(document.getElementById('glass-size-sg').value);
  const caloriesSG = ((abv / 100) * 0.789 * 7) * (glassSG * 29.5735);
  document.getElementById('og-sg-val').textContent = ogSG.toFixed(3);
  document.getElementById('fg-sg-val').textContent = fgSG.toFixed(3);
  document.getElementById('abv-sg').textContent    = to2(abv) + '%';
  document.getElementById('att-sg').textContent    = to2(attenuation) + '%';
  document.getElementById('calories-sg').textContent = to2(caloriesSG);

  updateSweetTable(abv);
  updateSNA();

  isSyncing = false;
}

// -------- SNA Scheduler (TOSNA for Mead) --------
function updateSNA() {
  const og = parseFloat(document.getElementById('og-sg').value);
  const fg = parseFloat(document.getElementById('fg-sg').value);
  const batch = parseFloat(document.getElementById('batch-size').value);
  const yeast = document.getElementById('yeast-strain').value;
  const nutrient = document.getElementById('nutrient-type').value;

  const obrix = sgToBrix(og);
  const nFactor = YEAST_N_FACTORS[yeast] || 1.25;

  const pitchRateNormal = 1.0;
  const pitchRateRobust = 1.5;
  const yeastNeededNormal = pitchRateNormal * batch;
  const yeastNeededRobust = pitchRateRobust * batch;

  let totalNutrient = (obrix * 10 * nFactor / 50) * batch;
  if (nutrient === 'FK') {
    totalNutrient *= 0.6;
  }
  const additionAmt = totalNutrient / 4;

  const sugarBreakSG = og - ((og - fg) / 3);

  document.getElementById('n-factor-display').textContent =
    `${nFactor.toFixed(2)} (for ${yeast})`;
  document.getElementById('pitch-rate').textContent =
    `${pitchRateNormal.toFixed(2)}–${pitchRateRobust.toFixed(2)} g/gal`;
  document.getElementById('yeast-needed').textContent =
    `${to2(yeastNeededNormal)}–${to2(yeastNeededRobust)} g`;
  document.getElementById('nutrient-total').textContent =
    `${to2(totalNutrient)} g (${nutrient})`;

  const schedule = [
    ['Yeast pitch', 0],
    ['24 h', additionAmt],
    ['48 h', additionAmt],
    ['72 h', additionAmt],
    [`1/3 Sugar Break (SG = ${sugarBreakSG.toFixed(3)})`, additionAmt]
  ];

  document.getElementById('sna-body').innerHTML = schedule.map(([stage, g]) => {
    const tsp = g / 5;
    return `
      <tr>
        <td>${stage}</td>
        <td>${to2(g)}</td>
        <td>${decimalToFraction(tsp)}</td>
      </tr>`;
  }).join('');
}

// -------- Batch Builder --------
function updateBuilder() {
  const batch      = parseFloat(document.getElementById('builder-batch-size').value);
  const desiredAbv = parseFloat(document.getElementById('builder-desired-abv').value);
  const builderYeast = document.getElementById('builder-yeast-strain').value;

  const honeyLbs   = ((desiredAbv / 131.25) * 1000 * batch) / 35;

  const fgAssumed = parseFloat(document.getElementById('fg-sg')?.value) || 1.000;
  const ogEstimated = (desiredAbv / 131.25) + fgAssumed;

  const obrixEstimated = sgToBrix(ogEstimated);
  const nFactorBuilder = YEAST_N_FACTORS[builderYeast] || 1.25;

  const totalFO = (obrixEstimated * 10 * nFactorBuilder / 50) * batch;

  const pitchRateNormal = 1.0;
  const pitchRateRobust = 1.5;
  const yeastNeededNormal = pitchRateNormal * batch;
  const yeastNeededRobust = pitchRateRobust * batch;

  document.getElementById('builder-size-val').textContent = batch.toFixed(1);
  document.getElementById('builder-abv-val').textContent  = desiredAbv.toFixed(1);
  document.getElementById('honey-amt').textContent        = to2(honeyLbs);
  document.getElementById('tosna-amt').textContent        = to2(totalFO) + ' g';
  document.getElementById('builder-yeast-pitch').textContent =
    `${to2(yeastNeededNormal)}–${to2(yeastNeededRobust)} g (1.00–1.50 g/gal)`;
}

// -------- Attach Event Listeners --------
// SG section
['og-sg','fg-sg'].forEach(id => {
  document.getElementById(id).addEventListener('input', updateSG);
  document.getElementById(id).addEventListener('input', updateSNA);
});
document.querySelectorAll('input[name="abv-formula"]').forEach(el =>
  el.addEventListener('change', updateSG)
);
document.getElementById('glass-size-sg').addEventListener('change', updateSG);

// Brix section
['og-brix','fg-brix'].forEach(id =>
  document.getElementById(id).addEventListener('input', updateBx)
);
document.getElementById('glass-size-bx').addEventListener('change', updateBx);

// SNA scheduler
document.getElementById('batch-size').addEventListener('input', updateSNA);
document.getElementById('yeast-strain').addEventListener('change', updateSNA);
document.getElementById('nutrient-type').addEventListener('change', updateSNA);

// Batch builder
['builder-batch-size','builder-desired-abv'].forEach(id =>
  document.getElementById(id).addEventListener('input', updateBuilder)
);
document.getElementById('builder-yeast-strain').addEventListener('change', updateBuilder);

// -------- Initial Render --------
updateSG();
updateBx();
updateSNA();
updateBuilder();

