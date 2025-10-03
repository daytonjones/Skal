// static/js/calculators.js

// TOSNA factors
const N = { LOW: 0.75, MED: 0.90, HIGH: 1.25 };

// Yeast → N-factor mapping (corrected)
const YEAST_N_FACTORS = {
  // Lalvin / Lallemand
  "Lalvin 71-B": N.LOW,                    // 71B has low nitrogen demand
  "Lalvin BOURGOVIN RC 212": N.HIGH,       // often treated as high in mead to avoid sulfides (see note)
  "Lalvin EC-1118": N.LOW,                 // Prise de Mousse, low N need
  "Lalvin ICV D-47": N.LOW,                // D47 listed as low N need
  "Lalvin KIV-1116": N.LOW,                // alias typo kept for compatibility
  "Lalvin K1V-1116": N.LOW,                // K1V is low/low–avg; treat as LOW

  // Red Star
  "Red Star Cote des Blancs": N.MED,       // manufacturer/vendo r lists medium
  "Red Star Flor Sherry": N.MED,           // limited data; default MED for primary ferment
  "Red Star Montrachet (Premier Classique)": N.MED,
  "Red Star Pasteur Champagne (Premier Blanc)": N.LOW,
  "Red Star Pasteur Red (Premier Rouge)": N.HIGH,
  "Red Star Premier Cuvée": N.LOW,

  // Vintner’s Harvest (generic defaults; specific docs vary by strain)
  "Vintner’s Harvest Saccharomyces Bayanus #1": N.MED,
  "Vintner’s Harvest Saccharomyces Bayanus #2": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #1": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #2": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #3": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #4": N.MED,
  "Vintner’s Harvest Saccharomyces Cerevisiae #5": N.MED,

  // White Labs (specific N-need rarely published; defaults chosen from style)
  "White Labs Assmanshausen Wine Yeast": N.MED,
  "White Labs Avise Wine Yeast": N.MED,
  "White Labs Cabernet Red Wine Yeast": N.MED,
  "White Labs Champagne": N.LOW,           // WLP715 analogue → low
  "White Labs Chardonnay White Wine": N.MED,
  "White Labs English Cider": N.MED,
  "White Labs French Red Wine Yeast": N.MED,
  "White Labs French White Wine Yeast": N.MED,
  "White Labs Merlot Red Wine Yeast": N.MED,
  "White Labs Steinberg-Geisenheim Wine Yeast": N.MED,
  "White Labs Suremain Burgundy Wine Yeast": N.MED,
  "White Labs Sweet Mead and Wine": N.MED, // WLP720: treat as MED

  // Wyeast
  "Wyeast Bordeaux": N.MED,
  "Wyeast Chablis": N.MED,
  "Wyeast Chateau": N.MED,
  "Wyeast Chianti": N.MED,
  "Wyeast Cider": N.MED,
  "Wyeast Dry Mead": N.MED,                // 4632 needs added nutrients
  "Wyeast Eau de Vie": N.HIGH,             // 4347 “Extreme” high-ABV work; set HIGH
  "Wyeast Pasteur Champagne": N.LOW,
  "Wyeast Portwine": N.MED,
  "Wyeast Rudesheimer": N.MED,
  "Wyeast Sake #9": N.HIGH,                // sake yeasts are typically higher N-demand
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

// -------- SG Calculator --------
function updateSG() {
  const og = parseFloat(document.getElementById('og-sg').value);
  const fg = parseFloat(document.getElementById('fg-sg').value);
  const formula = document.querySelector('input[name="abv-formula"]:checked').value;

  let abv = formula === 'standard'
    ? (og - fg) * 131.25
    : (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794);

  const attenuation = ((og - fg) / (og - 1)) * 100;
  const glass = parseFloat(document.getElementById('glass-size-sg').value);
  const calories = ((abv / 100) * 0.789 * 7) * (glass * 29.5735);

  document.getElementById('og-sg-val').textContent   = og.toFixed(3);
  document.getElementById('fg-sg-val').textContent   = fg.toFixed(3);
  document.getElementById('abv-sg').textContent      = to2(abv) + '%';
  document.getElementById('att-sg').textContent      = to2(attenuation) + '%';
  document.getElementById('calories-sg').textContent = to2(calories);

  updateSweetTable(abv);
  updateSNA();
}

// -------- Brix Calculator --------
function updateBx() {
  const obx = parseFloat(document.getElementById('og-brix').value);
  const fbx = parseFloat(document.getElementById('fg-brix').value);
  const ogSG = brixToSG(obx);
  const fgSG = brixToSG(fbx);

  const abv = (ogSG - fgSG) * 131.25;
  const attenuation = ((ogSG - fgSG) / (ogSG - 1)) * 100;
  const glass = parseFloat(document.getElementById('glass-size-bx').value);
  const calories = ((abv / 100) * 0.789 * 7) * (glass * 29.5735);

  document.getElementById('og-brix-val').textContent   = obx.toFixed(1);
  document.getElementById('fg-brix-val').textContent   = fbx.toFixed(1);
  document.getElementById('abv-bx').textContent        = to2(abv) + '%';
  document.getElementById('att-bx').textContent        = to2(attenuation) + '%';
  document.getElementById('calories-bx').textContent   = to2(calories);
}

// -------- SNA Scheduler (TOSNA for Mead) --------
function updateSNA() {
  const og = parseFloat(document.getElementById('og-sg').value);
  const fg = parseFloat(document.getElementById('fg-sg').value);
  const batch = parseFloat(document.getElementById('batch-size').value);
  const yeast = document.getElementById('yeast-strain').value;

  // Convert OG SG → Brix
  const obrix = ((182.4601 * og - 775.6821) * og + 1262.7794) * og - 669.5622;

  // Look up N-factor
  const nFactor = YEAST_N_FACTORS[yeast] || 1.25;

  // Update display of N-factor
  const nDisplay = document.getElementById('n-factor-display');
  if (nDisplay) {
    nDisplay.textContent = nFactor.toFixed(2) + ` (for ${yeast})`;
  }

  // Mead Made Right formula
  const totalFermaid = (obrix * 10 * nFactor / 50) * batch;
  const additionAmt = totalFermaid / 4;
  const sugarBreakSG = og - ((og - fg) / 3);

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
  const honeyLbs   = ((desiredAbv / 131.25) * 1000 * batch) / 35;

  document.getElementById('builder-size-val').textContent = batch.toFixed(1);
  document.getElementById('builder-abv-val').textContent  = desiredAbv.toFixed(1);
  document.getElementById('honey-amt').textContent        = to2(honeyLbs);
  document.getElementById('fm-amt').textContent           = to2(1.5 * batch);
  document.getElementById('yeast-amt').textContent        = to2(0.5 * batch);
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

// Batch builder
['builder-batch-size','builder-desired-abv'].forEach(id =>
  document.getElementById(id).addEventListener('input', updateBuilder)
);

// -------- Initial Render --------
updateSG();
updateBx();
updateSNA();
updateBuilder();
