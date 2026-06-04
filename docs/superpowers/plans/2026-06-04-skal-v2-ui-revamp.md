# Skål v2 — UI Revamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all templates and CSS with the warm amber/honey craft design system — sidebar navigation, cellar-row batch list, combined dashboard, HTMX-powered interactivity throughout.

**Architecture:** Complete CSS rewrite using custom properties (no Tailwind, no Bootstrap). HTMX 2.x loaded via CDN in base template. Sidebar via `templates/includes/sidebar.html`. HTMX partials already wired in Plan A views. Background image (`static/images/mead_background.png`) retained at `opacity: 0.15`.

**Tech Stack:** Django 5.2.3 templates, custom CSS with CSS custom properties, HTMX 2.x (CDN), vanilla JS (calculators.js unchanged)

**Prerequisite:** Plan A (`2026-06-04-skal-v2-backend-foundation.md`) must be complete before starting this plan.

**Spec:** `docs/superpowers/specs/2026-06-04-skal-v2-revamp-design.md`

---

## File Map

**New files:**
- `templates/includes/sidebar.html`
- `templates/includes/toast.html`
- `templates/batches/partials/checklist_item.html`

**Fully replaced files** (content completely rewritten):
- `static/css/styles.css`
- `templates/base.html`
- `templates/home.html`
- `templates/batches/index.html`
- `templates/batches/detail.html`
- `templates/batches/form.html`
- `templates/batches/confirm_delete.html`
- `templates/batches/partials/batch_rows.html` ← placeholder from Plan A, now real
- `templates/recipes/index.html`
- `templates/recipes/detail.html`
- `templates/recipes/form.html`
- `templates/recipes/recipe_confirm_delete.html`
- `templates/recipes/partials/recipe_rows.html` ← placeholder from Plan A, now real
- `templates/calculators/index.html`
- `templates/yeast/yeast.html`
- `templates/accounts/auth.html`
- `templates/accounts/profile.html`
- `templates/404.html`
- `templates/500.html`
- `templates/info.html`

---

## Task 1: CSS Design System

**Files:**
- Modify (full rewrite): `static/css/styles.css`

This is the foundation. All other tasks depend on it being in place.

- [ ] **Replace `static/css/styles.css` entirely**

```css
/* ============================================================
   SKÅL — Design System
   Warm amber/honey craft aesthetic
   ============================================================ */

/* ── Custom Properties ────────────────────────────────────── */
:root {
  --brown-950: #1c0a00;
  --brown-900: #451a03;
  --brown-700: #92400e;
  --brown-500: #b45309;
  --amber-600: #d97706;
  --amber-400: #f59e0b;
  --amber-200: #fde68a;
  --amber-100: #fef3c7;
  --cream-50:  #fef9ef;
  --cream-100: #fef3c7;
  --white:     #ffffff;
  --border:    #e9d5a1;

  --stage-active:    #d97706;
  --stage-secondary: #7c3aed;
  --stage-bottled:   #16a34a;
  --stage-planned:   #94a3b8;

  --sidebar-width: 200px;
  --sidebar-collapsed: 60px;

  --font-serif: 'Georgia', 'Times New Roman', serif;
  --font-ui:    system-ui, -apple-system, sans-serif;

  --radius-sm: 3px;
  --radius:    6px;
  --radius-lg: 10px;

  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
  --shadow:    0 2px 8px rgba(0,0,0,0.10);
}

/* Dark mode overrides */
body.dark {
  --brown-950: #fef9ef;
  --brown-900: #fde68a;
  --brown-700: #fcd97a;
  --amber-600: #f59e0b;
  --cream-50:  #1a0f00;
  --cream-100: #2a1500;
  --white:     #1f1000;
  --border:    #5a3a1a;
}

/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  scroll-behavior: smooth;
  -webkit-tap-highlight-color: transparent;
}

body {
  font-family: var(--font-ui);
  background-color: var(--cream-50);
  color: var(--brown-900);
  min-height: 100vh;
  position: relative;
}

/* Background image — always visible at low opacity */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background: url("/static/images/mead_background.png") no-repeat center center / cover;
  opacity: 0.15;
  z-index: -1;
  pointer-events: none;
}
body.dark::before { opacity: 0.05; }

a { color: var(--amber-600); text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; }

h1 { font-family: var(--font-serif); font-size: 1.5rem; color: var(--brown-900); }
h2 { font-family: var(--font-serif); font-size: 1.1rem; color: var(--brown-900); margin-bottom: 0.5rem; }
h3 { font-size: 0.9rem; font-weight: 600; color: var(--brown-900); }

/* ── App Shell: Sidebar + Content ─────────────────────────── */
.app-shell {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ──────────────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width);
  background: var(--brown-950);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-brand {
  padding: 1.25rem 1rem 1rem;
  font-family: var(--font-serif);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--amber-200);
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0;
  list-style: none;
}

.sidebar-nav li a {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  color: rgba(253,230,138,0.75);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.sidebar-nav li a:hover {
  background: rgba(255,255,255,0.06);
  color: var(--amber-200);
  text-decoration: none;
}

.sidebar-nav li a.active,
.sidebar-nav li a[aria-current="page"] {
  background: rgba(217,119,6,0.15);
  color: var(--amber-200);
  border-left-color: var(--amber-600);
}

.sidebar-nav .nav-icon {
  font-size: 1rem;
  width: 1.2rem;
  text-align: center;
  flex-shrink: 0;
}

.sidebar-divider {
  border: none;
  border-top: 1px solid rgba(255,255,255,0.08);
  margin: 0.5rem 0;
}

.sidebar-user {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.sidebar-user .user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.sidebar-user .user-name {
  font-size: 0.75rem;
  color: var(--amber-200);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.sidebar-user a.logout-link {
  font-size: 0.65rem;
  color: rgba(253,230,138,0.5);
}
.sidebar-user a.logout-link:hover { color: var(--amber-200); }

/* Hamburger toggle (mobile only) */
.sidebar-toggle {
  display: none;
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 200;
  background: var(--brown-950);
  border: none;
  color: var(--amber-200);
  font-size: 1.25rem;
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  line-height: 1;
}

/* ── Main Content Area ────────────────────────────────────── */
.main-content {
  flex: 1;
  min-width: 0;
  padding: 1.5rem 2rem;
  max-width: 1100px;
}

/* When no sidebar (auth pages) */
.main-content--full {
  max-width: 500px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

/* ── Page Header ──────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.page-title {
  font-family: var(--font-serif);
  font-size: 1.4rem;
  color: var(--brown-900);
}

/* ── Buttons ──────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, transform 0.1s, box-shadow 0.1s;
  white-space: nowrap;
}
.btn:hover { text-decoration: none; }
.btn:active { transform: translateY(1px); }

.btn-primary {
  background: var(--amber-600);
  color: #fff;
  border-color: var(--amber-600);
}
.btn-primary:hover { background: var(--amber-400); border-color: var(--amber-400); color: #fff; }

.btn-secondary {
  background: var(--white);
  color: var(--brown-900);
  border-color: var(--border);
}
.btn-secondary:hover { background: var(--amber-100); }

.btn-danger {
  background: #dc2626;
  color: #fff;
  border-color: #dc2626;
}
.btn-danger:hover { background: #b91c1c; }

.btn-ghost {
  background: transparent;
  color: var(--amber-600);
  border-color: transparent;
}
.btn-ghost:hover { background: var(--amber-100); }

.btn-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}

/* ── Form Elements ────────────────────────────────────────── */
label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--brown-700);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.3rem;
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
input[type="date"],
input[type="search"],
select,
textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  font-family: var(--font-ui);
  background: var(--white);
  color: var(--brown-900);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--amber-600);
  box-shadow: 0 0 0 3px rgba(217,119,6,0.15);
}

textarea { resize: vertical; min-height: 100px; }

.form-group { margin-bottom: 1rem; }

.errorlist {
  list-style: none;
  color: #dc2626;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

input[type="checkbox"] {
  width: auto;
  accent-color: var(--amber-600);
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

/* ── Card / Panel ─────────────────────────────────────────── */
.card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.card + .card { margin-top: 1rem; }

/* ── Section Label ────────────────────────────────────────── */
.section-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brown-700);
  margin-bottom: 0.5rem;
}

/* ── Stage Badges ─────────────────────────────────────────── */
.badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 7px;
  border-radius: 2px;
}
.badge-active    { background: #fef3c7; color: var(--stage-active); }
.badge-secondary { background: #ede9fe; color: var(--stage-secondary); }
.badge-bottled   { background: #dcfce7; color: var(--stage-bottled); }
.badge-planned   { background: #f1f5f9; color: var(--stage-planned); }
.badge-public    { background: #dbeafe; color: #1d4ed8; }
.badge-private   { background: #f1f5f9; color: #64748b; }

/* ── Flask Fill Indicator ─────────────────────────────────── */
.flask {
  width: 16px;
  height: 22px;
  border: 2px solid currentColor;
  border-radius: 2px 2px 6px 6px;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.flask::before {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--fill, 0%);
  background: currentColor;
  opacity: 0.3;
  transition: height 0.3s ease;
}

.flask[data-stage="active"]    { color: var(--stage-active); }
.flask[data-stage="secondary"] { color: var(--stage-secondary); }
.flask[data-stage="bottled"]   { color: var(--stage-bottled); }
.flask[data-stage="planned"]   { color: var(--stage-planned); }

/* ── Progress Bar ─────────────────────────────────────────── */
.progress-track {
  background: var(--amber-100);
  border-radius: 2px;
  height: 5px;
  width: 100%;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--amber-600);
  transition: width 0.3s ease;
}
.progress-fill[data-stage="secondary"] { background: var(--stage-secondary); }
.progress-fill[data-stage="bottled"]   { background: var(--stage-bottled); }

/* ── Dashboard ────────────────────────────────────────────── */
.dash-greeting {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.dash-greeting h1 { margin: 0; }

.dash-greeting .subtext {
  font-size: 0.8rem;
  color: var(--brown-700);
  margin-top: 0.15rem;
}

.stat-tiles {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.stat-tile {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  text-align: center;
}

.stat-tile.highlight { border-color: var(--amber-200); background: var(--amber-100); }

.stat-value {
  font-family: var(--font-serif);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--amber-600);
  line-height: 1;
}

.stat-label {
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--brown-700);
  margin-top: 0.25rem;
}

.dash-body {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

/* Active fermentation rows inside dashboard */
.fermentation-row {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.75rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.fermentation-row .flask { margin-top: 0.1rem; }

.fermentation-info { flex: 1; min-width: 0; }
.fermentation-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--brown-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.fermentation-meta { font-size: 0.72rem; color: var(--brown-700); margin-top: 0.1rem; }

.quick-actions { display: flex; flex-direction: column; gap: 0.4rem; }

/* Photo strip */
.photo-strip-section { border-top: 1px solid var(--border); padding-top: 1rem; }

.photo-strip {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}

.photo-strip a {
  flex-shrink: 0;
  display: block;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}

.photo-strip img {
  width: 90px;
  height: 70px;
  object-fit: cover;
  display: block;
}

/* ── Cellar Rows (Batch List) ─────────────────────────────── */
.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  align-items: center;
}

.search-bar input { flex: 1; }

.stage-filters {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.stage-btn {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--white);
  color: var(--brown-700);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.stage-btn:hover,
.stage-btn.active { background: var(--amber-100); border-color: var(--amber-600); color: var(--brown-900); }

.batch-rows { display: flex; flex-direction: column; gap: 0.4rem; }

.batch-row {
  background: var(--white);
  border: 1px solid var(--border);
  border-left: 4px solid var(--stage-planned);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 0.6rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: box-shadow 0.15s;
}
.batch-row:hover { box-shadow: var(--shadow); text-decoration: none; }
.batch-row[data-stage="active"]    { border-left-color: var(--stage-active); }
.batch-row[data-stage="secondary"] { border-left-color: var(--stage-secondary); }
.batch-row[data-stage="bottled"]   { border-left-color: var(--stage-bottled); }

.batch-row-info { flex: 1; min-width: 0; }
.batch-row-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--brown-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.batch-row-meta { font-size: 0.72rem; color: var(--brown-700); margin-top: 0.1rem; }

.batch-row-abv {
  text-align: right;
  flex-shrink: 0;
  min-width: 3.5rem;
}
.batch-row-abv .abv-value {
  font-family: var(--font-serif);
  font-size: 1rem;
  font-weight: 700;
}
.batch-row-abv .abv-label { font-size: 0.6rem; text-transform: uppercase; color: var(--brown-700); }

.batch-row-progress {
  flex-shrink: 0;
  width: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.batch-row-progress .steps-label { font-size: 0.6rem; color: var(--brown-700); }

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--brown-700);
}
.empty-state p { margin-bottom: 1rem; }

/* ── Batch / Recipe Detail ────────────────────────────────── */
.detail-panel {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  max-width: 720px;
}

.detail-hero {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.detail-hero .flask-lg {
  width: 28px;
  height: 44px;
  border: 3px solid currentColor;
  border-radius: 3px 3px 10px 10px;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  margin-top: 0.25rem;
}
.detail-hero .flask-lg::before {
  content: "";
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: var(--fill, 0%);
  background: currentColor;
  opacity: 0.3;
}

.detail-hero-info { flex: 1; }
.detail-hero h1 { margin-bottom: 0.25rem; }
.detail-hero .meta { font-size: 0.8rem; color: var(--brown-700); }

.detail-stats {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
.detail-stat { text-align: center; }
.detail-stat-value {
  font-family: var(--font-serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--amber-600);
}
.detail-stat-label { font-size: 0.65rem; text-transform: uppercase; color: var(--brown-700); }

/* Checklist */
.checklist { list-style: none; margin: 0.75rem 0; }

.checklist-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}
.checklist-item:last-child { border-bottom: none; }

.checklist-item input[type="checkbox"] {
  margin-top: 0.1rem;
  flex-shrink: 0;
}

.checklist-item-body { flex: 1; }
.checklist-step-name { font-size: 0.875rem; font-weight: 500; }
.checklist-date { font-size: 0.72rem; color: var(--brown-700); margin-top: 0.1rem; }

.note-input {
  margin-top: 0.35rem;
  padding: 0.3rem 0.5rem;
  font-size: 0.8rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  width: 100%;
  background: var(--cream-50);
  color: var(--brown-900);
}
.note-input:focus {
  border-color: var(--amber-600);
  outline: none;
  box-shadow: 0 0 0 2px rgba(217,119,6,0.1);
}

/* ── Recipe Rows ──────────────────────────────────────────── */
.recipe-rows { display: flex; flex-direction: column; gap: 0.4rem; }

.recipe-row {
  background: var(--white);
  border: 1px solid var(--border);
  border-left: 4px solid var(--amber-200);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 0.6rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: box-shadow 0.15s;
}
.recipe-row:hover { box-shadow: var(--shadow); text-decoration: none; }

.recipe-row-info { flex: 1; min-width: 0; }
.recipe-row-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--brown-900);
}
.recipe-row-meta { font-size: 0.72rem; color: var(--brown-700); margin-top: 0.1rem; }

/* Featured recipe panel */
.featured-panel {
  background: var(--cream-100);
  border: 1px solid var(--amber-200);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-top: 1.25rem;
}
.featured-panel h2 { color: var(--brown-700); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
.featured-panel h3 { font-family: var(--font-serif); font-size: 1.1rem; margin: 0.25rem 0 0.75rem; }

/* ── Calc Grid ────────────────────────────────────────────── */
.calc-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.calc-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.calc-card h2 {
  font-size: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.75rem;
}

.calc-inputs { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }
.calc-inputs label { text-transform: none; font-size: 0.82rem; letter-spacing: 0; color: var(--brown-900); }
.calc-inputs input[type="range"] { padding: 0; border: none; box-shadow: none; accent-color: var(--amber-600); }

.calc-results p { font-size: 0.9rem; margin-bottom: 0.25rem; }
.calc-results strong { color: var(--amber-600); font-family: var(--font-serif); }

.calc-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.calc-table th, .calc-table td { border: 1px solid var(--border); padding: 0.4rem 0.6rem; text-align: center; }
.calc-table thead th { background: var(--amber-100); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--brown-700); }
.calc-table tbody tr:hover { background: var(--cream-50); }
.calc-table tbody tr.highlight { background: var(--amber-100); font-weight: 600; }

.batch-builder {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}
.batch-builder h2 { padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); margin-bottom: 0.75rem; }
.builder-inputs { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
.builder-inputs label { color: var(--brown-900); font-size: 0.82rem; letter-spacing: 0; text-transform: none; }
.builder-inputs input[type="range"] { padding: 0; border: none; box-shadow: none; accent-color: var(--amber-600); display: block; width: 100%; }
.builder-results p { margin-bottom: 0.35rem; font-size: 0.9rem; }
.builder-results strong { color: var(--amber-600); }

.calc-info { margin-top: 1rem; }
.calc-info summary { cursor: pointer; font-weight: 600; padding: 0.5rem 0; color: var(--brown-700); font-size: 0.85rem; }
.calc-info pre { background: var(--cream-50); padding: 0.5rem; border-radius: var(--radius-sm); overflow-x: auto; font-size: 0.8rem; margin: 0.5rem 0; }

/* Tooltip */
.tooltip { position: relative; display: inline-block; }
.tooltip-trigger { color: var(--amber-600); cursor: help; margin-left: 0.4rem; font-size: 0.8rem; }
.tooltip-content {
  display: none;
  position: absolute;
  top: 1.5rem; left: 0;
  width: 550px;
  max-height: 380px;
  overflow-y: auto;
  background: var(--white);
  color: var(--brown-900);
  border: 1px solid var(--border);
  padding: 1rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  z-index: 200;
  font-size: 0.85rem;
  line-height: 1.5;
}
.tooltip:hover .tooltip-content { display: block; }

/* ── Auth Page ────────────────────────────────────────────── */
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.auth-box {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow);
}

.auth-brand {
  text-align: center;
  margin-bottom: 1.5rem;
}
.auth-brand h1 {
  font-family: var(--font-serif);
  font-size: 2rem;
  color: var(--brown-900);
}
.auth-brand p { font-size: 0.82rem; color: var(--brown-700); margin-top: 0.25rem; }

.auth-tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--border);
}
.auth-tab {
  flex: 1;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brown-700);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s, border-color 0.15s;
}
.auth-tab.active { color: var(--amber-600); border-bottom-color: var(--amber-600); }

/* ── Toast Notifications ──────────────────────────────────── */
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}

.toast {
  background: var(--white);
  border: 1px solid var(--border);
  border-left: 4px solid var(--amber-600);
  border-radius: var(--radius-sm);
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  box-shadow: var(--shadow);
  pointer-events: all;
  animation: toastIn 0.2s ease;
  max-width: 320px;
  color: var(--brown-900);
}
.toast.toast-error { border-left-color: #dc2626; }
.toast.toast-hiding { animation: toastOut 0.3s ease forwards; }

@keyframes toastIn  { from { opacity: 0; transform: translateX(1rem); } to { opacity: 1; transform: none; } }
@keyframes toastOut { to   { opacity: 0; transform: translateX(1rem); } }

/* ── Info Page ────────────────────────────────────────────── */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1rem;
}
.info-grid dl dt { font-weight: 700; margin-top: 0.75rem; color: var(--brown-900); }
.info-grid dl dd { margin-left: 1rem; font-size: 0.875rem; color: var(--brown-700); margin-top: 0.15rem; }

/* ── Batch Images ─────────────────────────────────────────── */
.batch-images { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 0.75rem; margin-top: 1rem; }
.batch-images img { border-radius: var(--radius-sm); border: 1px solid var(--border); width: 100%; aspect-ratio: 4/3; object-fit: cover; }
.batch-images p { font-size: 0.75rem; color: var(--brown-700); margin-top: 0.25rem; }

/* ── Site Footer ──────────────────────────────────────────── */
.site-footer {
  padding: 1rem 2rem;
  font-size: 0.75rem;
  color: var(--brown-700);
  border-top: 1px solid var(--border);
  text-align: right;
}

/* ── Print ────────────────────────────────────────────────── */
@media print {
  .sidebar, .sidebar-toggle, .btn-group, .no-print,
  .search-bar, .stage-filters, .toast-container { display: none !important; }
  .app-shell { display: block; }
  .main-content { padding: 0; max-width: 100%; }
  body::before { display: none; }
  .detail-panel { box-shadow: none; border: none; padding: 0; }
}

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 900px) {
  .sidebar { width: var(--sidebar-collapsed); }
  .sidebar-brand { font-size: 1rem; padding: 1rem 0.5rem; text-align: center; overflow: hidden; }
  .sidebar-nav li a .nav-label { display: none; }
  .sidebar-nav li a { justify-content: center; padding: 0.65rem 0.5rem; }
  .sidebar-nav .nav-icon { width: auto; }
  .sidebar-user .user-name, .sidebar-user .logout-link { display: none; }
  .sidebar-user { justify-content: center; }
  .stat-tiles { grid-template-columns: repeat(2, 1fr); }
  .dash-body { grid-template-columns: 1fr; }
  .calc-grid { grid-template-columns: 1fr; }
  .info-grid { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .sidebar { display: none; position: fixed; left: 0; top: 0; bottom: 0; z-index: 150; }
  .sidebar.open { display: flex; }
  .sidebar-toggle { display: block; }
  .main-content { padding: 3.5rem 1rem 1rem; }
  .stat-tiles { grid-template-columns: repeat(2, 1fr); }
  .builder-inputs { flex-direction: column; }
  .detail-hero { flex-wrap: wrap; }
}
```

- [ ] **Verify the CSS file saves cleanly (no truncation)**

```bash
wc -l static/css/styles.css
```
Expected: roughly 450-480 lines

- [ ] **Commit**

```bash
git add static/css/styles.css
git commit -m "feat: complete CSS design system — amber/honey craft theme with custom properties"
```

---

## Task 2: Base Template + Sidebar + HTMX

**Files:**
- Create: `templates/includes/sidebar.html`
- Create: `templates/includes/toast.html`
- Modify (full rewrite): `templates/base.html`

- [ ] **Create `templates/includes/sidebar.html`**

```html
{% load static gravatar %}
<aside class="sidebar" id="sidebar">
  <div class="sidebar-brand">Skål</div>
  <ul class="sidebar-nav">
    <li>
      <a href="{% url 'home' %}" {% if request.resolver_match.url_name == 'home' %}aria-current="page"{% endif %}>
        <span class="nav-icon">🏠</span>
        <span class="nav-label">Home</span>
      </a>
    </li>
    <li>
      <a href="{% url 'recipes:index' %}" {% if 'recipes' in request.resolver_match.app_name %}aria-current="page"{% endif %}>
        <span class="nav-icon">📜</span>
        <span class="nav-label">Recipes</span>
      </a>
    </li>
    <li>
      <a href="{% url 'batches:index' %}" {% if 'batches' in request.resolver_match.app_name %}aria-current="page"{% endif %}>
        <span class="nav-icon">🍺</span>
        <span class="nav-label">Batches</span>
      </a>
    </li>
    <li>
      <a href="{% url 'calculators:index' %}" {% if 'calculators' in request.resolver_match.app_name %}aria-current="page"{% endif %}>
        <span class="nav-icon">🧮</span>
        <span class="nav-label">Calculators</span>
      </a>
    </li>
    <li>
      <a href="{% url 'yeast' %}" {% if request.resolver_match.url_name == 'yeast' %}aria-current="page"{% endif %}>
        <span class="nav-icon">🦠</span>
        <span class="nav-label">Yeast Info</span>
      </a>
    </li>
    <li>
      <a href="{% url 'info' %}" {% if request.resolver_match.url_name == 'info' %}aria-current="page"{% endif %}>
        <span class="nav-icon">📖</span>
        <span class="nav-label">Mead History</span>
      </a>
    </li>
  </ul>

  <div class="sidebar-user">
    {% if request.user.avatar %}
      <img src="{{ request.user.avatar.url }}" alt="{{ request.user.get_full_name|default:request.user.username }}" class="user-avatar">
    {% else %}
      <img src="{{ request.user.email|gravatar_url:40 }}" alt="{{ request.user.get_full_name|default:request.user.username }}" class="user-avatar">
    {% endif %}
    <span class="user-name">{{ request.user.get_full_name|default:request.user.username }}</span>
    <form method="post" action="{% url 'accounts:logout' %}" style="display:inline;">
      {% csrf_token %}
      <button type="submit" class="logout-link" style="background:none;border:none;cursor:pointer;font-size:0.65rem;color:rgba(253,230,138,0.5);padding:0;">
        Sign out
      </button>
    </form>
  </div>
</aside>
```

- [ ] **Create `templates/includes/toast.html`**

```html
{% if messages %}
<div class="toast-container" id="toast-container">
  {% for message in messages %}
  <div class="toast {% if message.tags == 'error' %}toast-error{% endif %}" role="alert">
    {{ message }}
  </div>
  {% endfor %}
</div>
<script>
  (function() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function(t) {
      setTimeout(function() {
        t.classList.add('toast-hiding');
        setTimeout(function() { t.remove(); }, 300);
      }, 3500);
    });
  })();
</script>
{% endif %}
```

- [ ] **Rewrite `templates/base.html`**

```html
{% load static gravatar %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Skål — {% block title %}{% endblock %}</title>
  <link rel="icon" href="{% static 'images/skal.ico' %}" type="image/x-icon">
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body class="{% if request.user.is_authenticated and request.user.theme == 'dark' %}dark{% endif %}">

  {% if request.user.is_authenticated %}
    <button class="sidebar-toggle" id="sidebar-toggle" aria-label="Toggle navigation">☰</button>

    <div class="app-shell">
      {% include "includes/sidebar.html" %}
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;">
        <main class="main-content">
          {% include "includes/toast.html" %}
          {% block content %}{% endblock %}
        </main>
        <footer class="site-footer">
          Skål &copy;{% now "Y" %} Dayton Jones
        </footer>
      </div>
    </div>

  {% else %}
    {% include "includes/toast.html" %}
    {% block content %}{% endblock %}
  {% endif %}

  <script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"
          integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+"
          crossorigin="anonymous" defer></script>
  <script>
    // Mobile sidebar toggle
    (function() {
      const toggle = document.getElementById('sidebar-toggle');
      const sidebar = document.getElementById('sidebar');
      if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
          sidebar.classList.toggle('open');
        });
        document.addEventListener('click', function(e) {
          if (sidebar.classList.contains('open') &&
              !sidebar.contains(e.target) &&
              e.target !== toggle) {
            sidebar.classList.remove('open');
          }
        });
      }
    })();
  </script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Verify the site still loads (migrate if needed, run Django dev server briefly)**

```bash
python manage.py check
```
Expected: no errors

- [ ] **Commit**

```bash
git add templates/base.html templates/includes/
git commit -m "feat: new base template with sidebar, HTMX CDN, and toast infrastructure"
```

---

## Task 3: Dashboard Template

**Files:**
- Modify (full rewrite): `templates/home.html`

- [ ] **Rewrite `templates/home.html`**

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Home{% endblock %}

{% block content %}
<div class="dash-greeting">
  <div>
    <h1>Welcome back, {{ request.user.first_name|default:request.user.username }}</h1>
    <p class="subtext">{% now "l, F j" %} · {{ active_count }} batch{{ active_count|pluralize }} fermenting</p>
  </div>
  <div class="btn-group">
    <a href="{% url 'batches:create' %}" class="btn btn-primary">🍯 New Batch</a>
    <a href="{% url 'recipes:create' %}" class="btn btn-secondary">📜 New Recipe</a>
  </div>
</div>

<div class="stat-tiles">
  <div class="stat-tile">
    <div class="stat-value">{{ total_batches }}</div>
    <div class="stat-label">Batches</div>
  </div>
  <div class="stat-tile highlight">
    <div class="stat-value">{{ active_count }}</div>
    <div class="stat-label">Fermenting</div>
  </div>
  <div class="stat-tile">
    <div class="stat-value">{% if avg_abv %}{{ avg_abv }}%{% else %}—{% endif %}</div>
    <div class="stat-label">Avg ABV</div>
  </div>
  <div class="stat-tile">
    <div class="stat-value">{{ total_recipes }}</div>
    <div class="stat-label">Recipes</div>
  </div>
</div>

<div class="dash-body">
  <div>
    <p class="section-label">Active Fermentations</p>
    {% for batch in active_batches %}
    <div class="fermentation-row">
      <div class="flask flask-lg" data-stage="{{ batch.stage }}"
           style="--fill: {{ batch.checklist_progress }}%"></div>
      <div class="fermentation-info">
        <div class="fermentation-name">
          <a href="{% url 'batches:detail' batch.pk %}">{{ batch.name }}</a>
        </div>
        <div class="fermentation-meta">
          {{ batch.stage|capfirst }}
          · {% if batch.fg %}{{ batch.og|floatformat:3 }} → {{ batch.fg|floatformat:3 }}{% else %}OG {{ batch.og|floatformat:3 }}{% endif %}
          · {{ batch.checklist_progress }}% complete
        </div>
      </div>
    </div>
    {% empty %}
    <p style="color:var(--brown-700);font-size:0.875rem;">No active batches.
      <a href="{% url 'batches:create' %}">Start one →</a>
    </p>
    {% endfor %}
  </div>

  <div>
    <p class="section-label">Quick Actions</p>
    <div class="quick-actions" style="margin-bottom:1rem;">
      <a href="{% url 'batches:create' %}" class="btn btn-primary">🍯 New Batch</a>
      <a href="{% url 'recipes:create' %}" class="btn btn-secondary">📜 New Recipe</a>
      <a href="{% url 'calculators:index' %}" class="btn btn-secondary">🧮 Calculators</a>
    </div>

    {% if last_bottled %}
    <p class="section-label">Last Bottled</p>
    <div class="card" style="padding:0.75rem;">
      <a href="{% url 'batches:detail' last_bottled.pk %}" style="font-weight:600;color:var(--brown-900);">
        {{ last_bottled.name }}
      </a>
      <p style="font-size:0.75rem;color:var(--stage-bottled);margin-top:0.2rem;">
        ✓ Bottled
        {% if last_bottled.bottled_date %}{{ last_bottled.bottled_date }}{% endif %}
        {% if last_bottled.fg %} · {{ last_bottled.fg|floatformat:3 }} FG{% endif %}
      </p>
    </div>
    {% endif %}
  </div>
</div>

{% if recent_images %}
<div class="photo-strip-section">
  <p class="section-label">From the Cellar</p>
  <div class="photo-strip">
    {% for img in recent_images %}
    <a href="{% url 'batches:detail' img.batch.pk %}" title="{{ img.batch.name }}">
      <img src="{{ img.image.url }}" alt="{{ img.caption|default:img.batch.name }}">
    </a>
    {% endfor %}
  </div>
</div>
{% endif %}

<script>
  (function() {
    const btn = document.getElementById('play-skal');
    const player = document.getElementById('player-skal');
    if (!btn || !player) return;
    let playing = false;
    btn.addEventListener('click', function() {
      if (!playing) { player.play(); playing = true; btn.textContent = '⏸ Skål'; }
      else { player.pause(); playing = false; btn.textContent = '▶ Skål'; }
    });
    player.addEventListener('ended', function() { playing = false; btn.textContent = '▶ Skål'; });
  })();
</script>
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/home.html
git commit -m "feat: new dashboard template — stats, active fermentations, photo strip"
```

---

## Task 4: Batch List Template (Cellar Rows)

**Files:**
- Modify (full rewrite): `templates/batches/index.html`
- Modify (full rewrite): `templates/batches/partials/batch_rows.html`

- [ ] **Rewrite `templates/batches/partials/batch_rows.html`**

```html
{% load static %}
<div class="batch-rows" id="batch-rows">
{% for batch in batches %}
  <a href="{% url 'batches:detail' batch.pk %}" class="batch-row" data-stage="{{ batch.stage }}">
    <div class="flask" data-stage="{{ batch.stage }}"
         style="--fill: {{ batch.checklist_progress }}%"></div>
    <div class="batch-row-info">
      <div class="batch-row-name">{{ batch.name }}
        {% if batch.user != request.user %}
          <span style="font-weight:400;font-size:0.75rem;color:var(--brown-700);">
            ({{ batch.user.get_full_name|default:batch.user.username }})
          </span>
        {% endif %}
      </div>
      <div class="batch-row-meta">
        {{ batch.primary_date }} · {{ batch.batch_size }} gal
      </div>
    </div>
    <span class="badge badge-{{ batch.stage }}">{{ batch.stage|capfirst }}</span>
    <div class="batch-row-abv">
      {% if batch.fg %}
        <div class="abv-value" style="color:var(--stage-{{ batch.stage }});">
          {% with og=batch.og|floatformat:3 fg=batch.fg|floatformat:3 %}
          {{ batch.og }}
          {% endwith %}
        </div>
        <div class="abv-label">→ {{ batch.fg }}</div>
      {% else %}
        <div class="abv-value" style="color:var(--brown-700);">—</div>
        <div class="abv-label">FG TBD</div>
      {% endif %}
    </div>
    <div class="batch-row-progress">
      <div class="progress-track">
        <div class="progress-fill" data-stage="{{ batch.stage }}"
             style="width:{{ batch.checklist_progress }}%"></div>
      </div>
      <span class="steps-label">{{ batch.checklist_progress }}%</span>
    </div>
    {% if batch.user == request.user %}
      <a href="{% url 'batches:edit' batch.pk %}" class="btn btn-ghost no-print"
         onclick="event.stopPropagation();" style="padding:0.25rem 0.5rem;font-size:0.8rem;">✏️</a>
    {% endif %}
  </a>
{% empty %}
  <div class="empty-state">
    <p>Your cellar is empty.</p>
    <a href="{% url 'batches:create' %}" class="btn btn-primary">Start your first batch →</a>
  </div>
{% endfor %}
</div>
```

- [ ] **Rewrite `templates/batches/index.html`**

```html
{% extends "base.html" %}
{% block title %}Batches{% endblock %}

{% block content %}
<div class="page-header">
  <h1 class="page-title">Your Cellar</h1>
  <a href="{% url 'batches:create' %}" class="btn btn-primary">+ New Batch</a>
</div>

<div class="search-bar">
  <input
    type="search"
    name="q"
    id="batch-search"
    placeholder="Search batches..."
    value="{{ q }}"
    hx-get="{% url 'batches:index' %}"
    hx-trigger="input changed delay:300ms, search"
    hx-target="#batch-rows"
    hx-include=".stage-btn.active"
    autocomplete="off"
  >
</div>

<div class="stage-filters">
  <button class="stage-btn {% if not stage %}active{% endif %}"
          hx-get="{% url 'batches:index' %}"
          hx-target="#batch-rows"
          hx-include="#batch-search"
          hx-vals='{"stage": ""}'>All</button>
  <button class="stage-btn {% if stage == 'active' %}active{% endif %}"
          hx-get="{% url 'batches:index' %}"
          hx-target="#batch-rows"
          hx-include="#batch-search"
          hx-vals='{"stage": "active"}'>Active</button>
  <button class="stage-btn {% if stage == 'secondary' %}active{% endif %}"
          hx-get="{% url 'batches:index' %}"
          hx-target="#batch-rows"
          hx-include="#batch-search"
          hx-vals='{"stage": "secondary"}'>Secondary</button>
  <button class="stage-btn {% if stage == 'bottled' %}active{% endif %}"
          hx-get="{% url 'batches:index' %}"
          hx-target="#batch-rows"
          hx-include="#batch-search"
          hx-vals='{"stage": "bottled"}'>Bottled</button>
</div>

{% include "batches/partials/batch_rows.html" %}
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/batches/index.html templates/batches/partials/batch_rows.html
git commit -m "feat: batch list — cellar rows with HTMX live search and stage filter"
```

---

## Task 5: Batch Detail Template (HTMX Checklist + Notes)

**Files:**
- Modify (full rewrite): `templates/batches/detail.html`
- Create: `templates/batches/partials/checklist_item.html`

- [ ] **Create `templates/batches/partials/checklist_item.html`**

This template is swapped in-place by HTMX when a checkbox is toggled:
```html
<li class="checklist-item" id="chk-{{ field_base }}">
  <input type="checkbox"
    {% if done %}checked{% endif %}
    hx-post="{% url 'batches:update_checklist' batch.pk %}"
    hx-vals='{"field": "{{ field_base }}_done", "value": "{% if done %}false{% else %}true{% endif %}"}'
    hx-target="#chk-{{ field_base }}"
    hx-swap="outerHTML"
  >
  <div class="checklist-item-body">
    <span class="checklist-step-name">{{ label }}</span>
    {% if date %}
      <div class="checklist-date">{{ date }}</div>
    {% endif %}
    <input
      type="text"
      class="note-input"
      placeholder="Add a note..."
      value="{{ note }}"
      hx-post="{% url 'batches:checklist_note' batch.pk %}"
      hx-trigger="blur changed"
      hx-vals='{"field": "{{ field_base }}_note"}'
      hx-swap="none"
      name="note"
    >
  </div>
</li>
```

- [ ] **Rewrite `templates/batches/detail.html`**

```html
{% extends "base.html" %}
{% load static %}
{% block title %}{{ batch.name }}{% endblock %}

{% block content %}
<div class="detail-panel">

  <div class="detail-hero">
    <div class="flask flask-lg" data-stage="{{ batch.stage }}"
         style="--fill: {{ batch.checklist_progress }}%; color: var(--stage-{{ batch.stage }})"></div>
    <div class="detail-hero-info">
      <h1>{{ batch.name }}
        {% if batch.user and request.user != batch.user %}
          <span style="font-size:0.8rem;font-weight:400;color:var(--brown-700);">
            ({{ batch.user.get_full_name|default:batch.user.username }})
          </span>
        {% endif %}
      </h1>
      <div class="meta">
        {{ batch.primary_date }} · {{ batch.batch_size }} gal ·
        <span class="badge badge-{{ batch.stage }}">{{ batch.stage|capfirst }}</span>
        <span class="badge {% if batch.is_public %}badge-public{% else %}badge-private{% endif %}">
          {{ batch.is_public|yesno:"Public,Private" }}
        </span>
      </div>
      {% if batch.recipe %}
        <div class="meta" style="margin-top:0.2rem;">
          Recipe: <a href="{% url 'recipes:detail' batch.recipe.pk %}">{{ batch.recipe.name }}</a>
        </div>
      {% endif %}
      <div class="detail-stats">
        <div class="detail-stat">
          <div class="detail-stat-value">{{ batch.og|floatformat:3 }}</div>
          <div class="detail-stat-label">OG</div>
        </div>
        {% if batch.fg %}
          <div class="detail-stat">
            <div class="detail-stat-value">{{ batch.fg|floatformat:3 }}</div>
            <div class="detail-stat-label">FG</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value" style="color:var(--stage-{{ batch.stage }});">{{ abv|floatformat:1 }}%</div>
            <div class="detail-stat-label">ABV</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ calories|floatformat:0 }}</div>
            <div class="detail-stat-label">Cal/5oz</div>
          </div>
        {% endif %}
      </div>
    </div>
  </div>

  <div style="margin-bottom:1.25rem;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
      <h2 style="margin:0;">Checklist</h2>
      <span style="font-size:0.8rem;color:var(--brown-700);" id="progress-text">{{ batch.checklist_progress }}% complete</span>
    </div>
    <div class="progress-track" style="margin-bottom:0.75rem;">
      <div class="progress-fill" id="progress-bar" data-stage="{{ batch.stage }}"
           style="width:{{ batch.checklist_progress }}%"></div>
    </div>

    <ul class="checklist" id="checklist">
      {% with b=batch %}
      {% include "batches/partials/checklist_item.html" with field_base="create_must"   label="Create Must"           done=b.create_must_done    date=b.create_must_date   note=b.create_must_note %}
      {% include "batches/partials/checklist_item.html" with field_base="pitch_yeast"  label="Pitch Yeast"           done=b.pitch_yeast_done   date=b.pitch_yeast_date  note=b.pitch_yeast_note %}
      {% include "batches/partials/checklist_item.html" with field_base="fo_24h"       label="Fermaid O — 24h"       done=b.fo_24h_done        date=b.fo_24h_date       note=b.fo_24h_note %}
      {% include "batches/partials/checklist_item.html" with field_base="fo_48h"       label="Fermaid O — 48h"       done=b.fo_48h_done        date=b.fo_48h_date       note=b.fo_48h_note %}
      {% include "batches/partials/checklist_item.html" with field_base="fo_72h"       label="Fermaid O — 72h"       done=b.fo_72h_done        date=b.fo_72h_date       note=b.fo_72h_note %}
      {% include "batches/partials/checklist_item.html" with field_base="fo_1_3_break" label="1/3 Sugar Break"       done=b.fo_1_3_break_done  date=b.fo_1_3_break_date note=b.fo_1_3_break_note %}
      {% include "batches/partials/checklist_item.html" with field_base="rack_secondary" label="Rack to Secondary"  done=b.rack_secondary_done date=b.rack_secondary_date note=b.rack_secondary_note %}
      {% include "batches/partials/checklist_item.html" with field_base="bottled"      label="Bottled"               done=b.bottled_done        date=b.bottled_date      note=b.bottled_note %}
      {% endwith %}
    </ul>
  </div>

  {% if batch.notes %}
  <div style="margin-bottom:1.25rem;">
    <h2>Notes</h2>
    <div style="font-size:0.875rem;line-height:1.6;white-space:pre-wrap;">{{ batch.notes }}</div>
  </div>
  {% endif %}

  {% if request.user == batch.user %}
    <div class="btn-group no-print" style="margin-bottom:1rem;">
      <a href="{% url 'batches:edit' batch.pk %}" class="btn btn-primary">✏️ Edit Batch</a>
      <a href="{% url 'batches:delete' batch.pk %}" class="btn btn-danger">🗑️ Delete</a>
      <form method="post" action="{% url 'batches:toggle_visibility' batch.pk %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit" class="btn btn-secondary">
          {{ batch.is_public|yesno:"Make Private,Make Public" }}
        </button>
      </form>
    </div>
  {% endif %}
  <div class="btn-group no-print">
    <a href="{% url 'batches:index' %}" class="btn btn-secondary">← Cellar</a>
    <button onclick="window.print()" class="btn btn-secondary">🖨️ Print</button>
  </div>

  {% if images %}
    <div class="batch-images" style="margin-top:1.5rem;">
      <h2>Photos</h2>
      {% for img in images %}
        <div>
          <img src="{{ img.image.url }}" alt="{{ img.caption|default:batch.name }}">
          {% if img.caption %}<p>{{ img.caption }}</p>{% endif %}
        </div>
      {% endfor %}
    </div>
  {% endif %}

</div>

<script>
document.addEventListener('htmx:afterSwap', function(e) {
  if (e.target.closest('#checklist')) {
    const checks = document.querySelectorAll('#checklist input[type="checkbox"]');
    const done = Array.from(checks).filter(c => c.checked).length;
    const pct = Math.round((done / checks.length) * 100);
    const bar = document.getElementById('progress-bar');
    const txt = document.getElementById('progress-text');
    if (bar) bar.style.width = pct + '%';
    if (txt) txt.textContent = pct + '% complete';
  }
});
</script>
{% endblock %}
```

- [ ] **Update `BatchDetailView` to compute ABV properly**

The existing view computes ABV using a local formula. Verify `apps/batches/views.py` `get_context_data` passes `abv` and `calories` to template (it already does this — just confirm the calculation is in the view, not the template).

- [ ] **Commit**

```bash
git add templates/batches/detail.html templates/batches/partials/checklist_item.html
git commit -m "feat: batch detail — HTMX checklist with inline notes, hero flask gauge"
```

---

## Task 6: Batch Form Template

**Files:**
- Modify (full rewrite): `templates/batches/form.html`
- Modify (full rewrite): `templates/batches/confirm_delete.html`

- [ ] **Rewrite `templates/batches/form.html`**

```html
{% extends "base.html" %}
{% load static %}
{% block title %}{% if object %}Edit{% else %}New{% endif %} Batch{% endblock %}

{% block content %}
<div class="detail-panel">
  <h1>{% if object %}Edit Batch{% else %}New Batch{% endif %}</h1>

  <form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.non_field_errors }}

    <h2 style="margin-top:1rem;">Batch Details</h2>

    <div class="form-group">{{ form.recipe.label_tag }}{{ form.recipe }}{{ form.recipe.errors }}</div>
    <div class="form-group">{{ form.name.label_tag }}{{ form.name }}{{ form.name.errors }}</div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
      <div class="form-group">{{ form.batch_size.label_tag }}{{ form.batch_size }}{{ form.batch_size.errors }}</div>
      <div class="form-group">{{ form.og.label_tag }}{{ form.og }}{{ form.og.errors }}</div>
      <div class="form-group">{{ form.fg.label_tag }}{{ form.fg }}{{ form.fg.errors }}</div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;">
      <div class="form-group">{{ form.primary_date.label_tag }}{{ form.primary_date }}{{ form.primary_date.errors }}</div>
      <div class="form-group">{{ form.secondary_date.label_tag }}{{ form.secondary_date }}{{ form.secondary_date.errors }}</div>
      <div class="form-group">{{ form.bottling_date.label_tag }}{{ form.bottling_date }}{{ form.bottling_date.errors }}</div>
    </div>

    <div class="form-group">{{ form.notes.label_tag }}{{ form.notes }}{{ form.notes.errors }}</div>
    <div class="form-group" style="display:flex;align-items:center;gap:0.5rem;">
      {{ form.is_public }}
      <label for="{{ form.is_public.id_for_label }}" style="text-transform:none;font-size:0.875rem;color:var(--brown-900);margin:0;">
        Make this batch public
      </label>
    </div>

    <hr style="border:none;border-top:1px solid var(--border);margin:1.25rem 0;">
    <h2>Checklist</h2>
    <p style="font-size:0.8rem;color:var(--brown-700);margin-bottom:0.75rem;">
      Check off completed steps. Dates auto-fill when checked.
    </p>

    {% for step_done, step_date, label in checklist_steps %}
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">
      <div style="display:flex;align-items:center;gap:0.4rem;min-width:180px;">
        {{ step_done }}
        <label for="{{ step_done.id_for_label }}" style="text-transform:none;font-size:0.85rem;font-weight:500;color:var(--brown-900);margin:0;">
          {{ label }}
        </label>
      </div>
      <div style="flex:1;">{{ step_date }}</div>
    </div>
    {% endfor %}

    <hr style="border:none;border-top:1px solid var(--border);margin:1.25rem 0;">
    <h2>Photos</h2>
    <div class="form-group">
      <label for="id_images">Upload Images</label>
      <input type="file" name="images" id="id_images" multiple accept="image/*">
    </div>
    <div id="image-preview-container" style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.5rem;"></div>

    <div class="btn-group" style="margin-top:1.5rem;">
      <button type="submit" class="btn btn-primary">
        {% if object %}Save Changes{% else %}Create Batch{% endif %}
      </button>
      <a href="{% url 'batches:index' %}" class="btn btn-secondary">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/batches.js' %}"></script>
{% endblock %}
```

- [ ] **Add `checklist_steps` context to `BatchCreateView` and `BatchUpdateView` in `apps/batches/views.py`**

Add a helper method to both views (or a shared mixin). Add to each view's `get_context_data`:
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    form = ctx['form']
    ctx['checklist_steps'] = [
        (form['create_must_done'],    form['create_must_date'],    'Create Must'),
        (form['pitch_yeast_done'],    form['pitch_yeast_date'],    'Pitch Yeast'),
        (form['fo_24h_done'],         form['fo_24h_date'],         'Fermaid O — 24h'),
        (form['fo_48h_done'],         form['fo_48h_date'],         'Fermaid O — 48h'),
        (form['fo_72h_done'],         form['fo_72h_date'],         'Fermaid O — 72h'),
        (form['fo_1_3_break_done'],   form['fo_1_3_break_date'],   '1/3 Sugar Break'),
        (form['rack_secondary_done'], form['rack_secondary_date'], 'Rack to Secondary'),
        (form['bottled_done'],        form['bottled_date'],        'Bottled'),
    ]
    return ctx
```

- [ ] **Rewrite `templates/batches/confirm_delete.html`**

```html
{% extends "base.html" %}
{% block title %}Delete Batch{% endblock %}
{% block content %}
<div class="detail-panel">
  <h1>Delete Batch</h1>
  <p style="margin:1rem 0;color:var(--brown-700);">
    Are you sure you want to delete <strong>{{ object.name }}</strong>?
    This cannot be undone.
  </p>
  <form method="post">
    {% csrf_token %}
    <div class="btn-group">
      <button type="submit" class="btn btn-danger">Yes, Delete</button>
      <a href="{% url 'batches:detail' object.pk %}" class="btn btn-secondary">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/batches/form.html templates/batches/confirm_delete.html apps/batches/views.py
git commit -m "feat: redesigned batch form with checklist section and confirm delete page"
```

---

## Task 7: Recipe List Template

**Files:**
- Modify (full rewrite): `templates/recipes/index.html`
- Modify (full rewrite): `templates/recipes/partials/recipe_rows.html`

- [ ] **Rewrite `templates/recipes/partials/recipe_rows.html`**

```html
<div class="recipe-rows" id="recipe-rows">
{% for recipe in recipes %}
  <a href="{% url 'recipes:detail' recipe.pk %}" class="recipe-row">
    <div class="recipe-row-info">
      <div class="recipe-row-name">{{ recipe.name }}
        {% if recipe.user and request.user != recipe.user %}
          <span style="font-weight:400;font-size:0.75rem;color:var(--brown-700);">
            ({{ recipe.user.get_full_name|default:recipe.user.username|default:"Skål" }})
          </span>
        {% elif not recipe.user %}
          <span style="font-weight:400;font-size:0.75rem;color:var(--brown-700);">(Skål)</span>
        {% endif %}
      </div>
      <div class="recipe-row-meta">
        {{ recipe.batch_size }} gal ·
        {{ recipe.recipeingredient_set.count }} ingredient{{ recipe.recipeingredient_set.count|pluralize }}
      </div>
    </div>
    <span class="badge {% if recipe.is_public %}badge-public{% else %}badge-private{% endif %}">
      {{ recipe.is_public|yesno:"Public,Private" }}
    </span>
    {% if recipe.user == request.user %}
      <a href="{% url 'recipes:edit' recipe.pk %}" class="btn btn-ghost no-print"
         onclick="event.stopPropagation();" style="padding:0.25rem 0.5rem;font-size:0.8rem;">✏️</a>
    {% endif %}
  </a>
{% empty %}
  <div class="empty-state">
    <p>No recipes found.</p>
    <a href="{% url 'recipes:create' %}" class="btn btn-primary">Create your first recipe →</a>
  </div>
{% endfor %}
</div>
```

- [ ] **Rewrite `templates/recipes/index.html`**

```html
{% extends "base.html" %}
{% block title %}Recipes{% endblock %}

{% block content %}
<div class="page-header">
  <h1 class="page-title">Recipes</h1>
  <a href="{% url 'recipes:create' %}" class="btn btn-primary">+ New Recipe</a>
</div>

<div class="search-bar" style="margin-bottom:1rem;">
  <input
    type="search"
    name="q"
    id="recipe-search"
    placeholder="Search recipes..."
    value="{{ q }}"
    hx-get="{% url 'recipes:index' %}"
    hx-trigger="input changed delay:300ms, search"
    hx-target="#recipe-rows"
    autocomplete="off"
  >
</div>

{% include "recipes/partials/recipe_rows.html" %}

{% if featured %}
<div class="featured-panel">
  <h2>Featured Recipe</h2>
  <h3>
    <a href="{% url 'recipes:detail' featured.pk %}">{{ featured.name }}</a>
    {% if featured.user and request.user != featured.user %}
      <span style="font-weight:400;font-size:0.8rem;color:var(--brown-700);">
        ({{ featured.user.get_full_name|default:featured.user.username|default:"Skål" }})
      </span>
    {% elif not featured.user %}
      <span style="font-weight:400;font-size:0.8rem;color:var(--brown-700);">(Skål)</span>
    {% endif %}
  </h3>
  <p style="font-size:0.82rem;color:var(--brown-700);margin-bottom:0.75rem;">
    {{ featured.batch_size }} gal
  </p>
  <h3 style="font-size:0.82rem;color:var(--brown-700);text-transform:uppercase;letter-spacing:0.5px;">Ingredients</h3>
  <ul style="list-style:disc inside;font-size:0.875rem;margin:0.25rem 0 0.75rem 0.5rem;">
    {% for ri in featured.recipeingredient_set.all %}
      <li>{{ ri.quantity }} {{ ri.ingredient.name }}</li>
    {% endfor %}
  </ul>
  <a href="{% url 'recipes:detail' featured.pk %}" class="btn btn-secondary">View Full Recipe →</a>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/recipes/index.html templates/recipes/partials/recipe_rows.html
git commit -m "feat: recipe list — rows with HTMX live search and featured panel"
```

---

## Task 8: Recipe Detail, Form, and Delete Templates

**Files:**
- Modify (full rewrite): `templates/recipes/detail.html`
- Modify (full rewrite): `templates/recipes/form.html`
- Modify (full rewrite): `templates/recipes/recipe_confirm_delete.html`

- [ ] **Rewrite `templates/recipes/detail.html`**

```html
{% extends "base.html" %}
{% block title %}{{ recipe.name }}{% endblock %}

{% block content %}
<div class="detail-panel">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1rem;gap:0.75rem;flex-wrap:wrap;">
    <div>
      <h1>{{ recipe.name }}
        {% if recipe.user and request.user != recipe.user %}
          <span style="font-size:0.8rem;font-weight:400;color:var(--brown-700);">
            ({{ recipe.user.get_full_name|default:recipe.user.username|default:"Skål" }})
          </span>
        {% elif not recipe.user %}
          <span style="font-size:0.8rem;font-weight:400;color:var(--brown-700);">(Skål)</span>
        {% endif %}
      </h1>
      <div style="margin-top:0.3rem;">
        <span class="badge {% if recipe.is_public %}badge-public{% else %}badge-private{% endif %}">
          {{ recipe.is_public|yesno:"Public,Private" }}
        </span>
        <span style="font-size:0.8rem;color:var(--brown-700);margin-left:0.5rem;">{{ recipe.batch_size }} gal</span>
      </div>
    </div>
  </div>

  <h2>Ingredients</h2>
  <ul style="list-style:disc inside;font-size:0.875rem;margin:0.5rem 0 1rem 0.5rem;line-height:1.7;">
    {% for ri in ingredients %}
      <li>{{ ri.quantity }} {{ ri.ingredient.name }}</li>
    {% empty %}
      <li><em>No ingredients listed.</em></li>
    {% endfor %}
  </ul>

  <h2>Instructions</h2>
  <div style="font-size:0.875rem;line-height:1.7;white-space:pre-wrap;margin-bottom:1.25rem;">{{ recipe.instructions }}</div>

  {% if request.user == recipe.user %}
    <div class="btn-group no-print" style="margin-bottom:0.75rem;">
      <a href="{% url 'batches:create' %}?recipe={{ recipe.pk }}" class="btn btn-primary">🍺 Start a Batch</a>
      <form method="post" action="{% url 'recipes:clone' recipe.pk %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit" class="btn btn-secondary">📋 Clone Recipe</button>
      </form>
    </div>
    <div class="btn-group no-print" style="margin-bottom:0.75rem;">
      <a href="{% url 'recipes:edit' recipe.pk %}" class="btn btn-secondary">✏️ Edit</a>
      <a href="{% url 'recipes:delete' recipe.pk %}" class="btn btn-danger">🗑️ Delete</a>
      <form method="post" action="{% url 'recipes:toggle_visibility' recipe.pk %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit" class="btn btn-ghost">
          {{ recipe.is_public|yesno:"Make Private,Make Public" }}
        </button>
      </form>
    </div>
  {% else %}
    <div class="btn-group no-print" style="margin-bottom:0.75rem;">
      <a href="{% url 'batches:create' %}?recipe={{ recipe.pk }}" class="btn btn-primary">🍺 Start a Batch</a>
      <form method="post" action="{% url 'recipes:clone' recipe.pk %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit" class="btn btn-secondary">📋 Clone to My Recipes</button>
      </form>
    </div>
  {% endif %}

  <div class="btn-group no-print">
    <a href="{% url 'recipes:index' %}" class="btn btn-ghost">← Recipes</a>
    <button onclick="window.print()" class="btn btn-secondary">🖨️ Print</button>
  </div>
</div>
{% endblock %}
```

- [ ] **Rewrite `templates/recipes/form.html`**

```html
{% extends "base.html" %}
{% load static %}
{% block title %}{% if object %}Edit{% else %}New{% endif %} Recipe{% endblock %}

{% block content %}
<div class="detail-panel">
  <h1>{% if object %}Edit Recipe{% else %}New Recipe{% endif %}</h1>

  <form method="post">
    {% csrf_token %}
    {{ form.non_field_errors }}

    <div class="form-group">{{ form.name.label_tag }}{{ form.name }}{{ form.name.errors }}</div>
    <div class="form-group">{{ form.batch_size.label_tag }}{{ form.batch_size }}{{ form.batch_size.errors }}</div>
    <div class="form-group">{{ form.instructions.label_tag }}{{ form.instructions }}{{ form.instructions.errors }}</div>

    <hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">
    <h2>Primary Ingredients</h2>

    <table style="width:100%;border-collapse:collapse;font-size:0.875rem;margin-bottom:0.75rem;">
      <thead>
        <tr style="border-bottom:1px solid var(--border);">
          <th style="text-align:left;padding:0.4rem 0.5rem;color:var(--brown-700);font-size:0.72rem;text-transform:uppercase;">Ingredient</th>
          <th style="text-align:left;padding:0.4rem 0.5rem;color:var(--brown-700);font-size:0.72rem;text-transform:uppercase;">Quantity</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">Honey</label>
            {{ form.honey }}<br>{{ form.honey.errors }}
          </td>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">lbs</label>
            {{ form.honey_quantity }}<br>{{ form.honey_quantity.errors }}
          </td>
        </tr>
        <tr>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">Water</label>
            {{ form.water }}<br>{{ form.water.errors }}
          </td>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">gal</label>
            {{ form.water_quantity }}<br>{{ form.water_quantity.errors }}
          </td>
        </tr>
        <tr>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">Yeast</label>
            {{ form.yeast }}<br>{{ form.yeast.errors }}
          </td>
          <td style="padding:0.35rem 0.5rem;">
            <label style="font-size:0.72rem;text-transform:uppercase;margin-bottom:0.2rem;">Qty</label>
            {{ form.yeast_quantity }}<br>{{ form.yeast_quantity.errors }}
          </td>
        </tr>
      </tbody>
    </table>

    <datalist id="honey-list">{% for n in all_honey %}<option value="{{ n }}">{% endfor %}</datalist>
    <datalist id="water-list">{% for n in all_water %}<option value="{{ n }}">{% endfor %}</datalist>
    <datalist id="yeast-list">{% for n in all_yeast %}<option value="{{ n }}">{% endfor %}</datalist>

    <hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">
    <h2>Additional Ingredients</h2>

    {{ ingredient_formset.management_form }}
    {{ ingredient_formset.non_form_errors }}
    <datalist id="ingredient-list">{% for n in all_ingredients %}<option value="{{ n }}">{% endfor %}</datalist>

    <table style="width:100%;border-collapse:collapse;font-size:0.875rem;margin-bottom:0.5rem;">
      <thead>
        <tr style="border-bottom:1px solid var(--border);">
          <th style="text-align:left;padding:0.4rem 0.5rem;color:var(--brown-700);font-size:0.72rem;text-transform:uppercase;">Ingredient</th>
          <th style="text-align:left;padding:0.4rem 0.5rem;color:var(--brown-700);font-size:0.72rem;text-transform:uppercase;">Quantity</th>
          <th style="padding:0.4rem 0.5rem;color:var(--brown-700);font-size:0.72rem;text-transform:uppercase;">Remove?</th>
        </tr>
      </thead>
      <tbody id="ingredient-rows">
        {% for subform in ingredient_formset %}
          <tr>
            <td style="padding:0.35rem 0.5rem;">{{ subform.ingredient_name.errors }}{{ subform.ingredient_name }}</td>
            <td style="padding:0.35rem 0.5rem;">{{ subform.quantity.errors }}{{ subform.quantity }}</td>
            <td style="padding:0.35rem 0.5rem;text-align:center;">{{ subform.DELETE }}</td>
          </tr>
        {% endfor %}
        <tr id="empty-form-row" style="display:none;">
          <td style="padding:0.35rem 0.5rem;">{{ ingredient_formset.empty_form.ingredient_name }}</td>
          <td style="padding:0.35rem 0.5rem;">{{ ingredient_formset.empty_form.quantity }}</td>
          <td style="padding:0.35rem 0.5rem;text-align:center;">{{ ingredient_formset.empty_form.DELETE }}</td>
        </tr>
      </tbody>
    </table>
    <button type="button" id="add-ingredient" class="btn btn-ghost" style="font-size:0.8rem;">+ Add ingredient</button>

    <hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">
    <div class="form-group" style="display:flex;align-items:center;gap:0.5rem;">
      {{ form.is_public }}
      <label for="{{ form.is_public.id_for_label }}" style="text-transform:none;font-size:0.875rem;color:var(--brown-900);margin:0;">
        Make this recipe public (visible to all users)
      </label>
    </div>

    <div class="btn-group" style="margin-top:1.25rem;">
      <button type="submit" class="btn btn-primary">Save Recipe</button>
      <a href="{% url 'recipes:index' %}" class="btn btn-secondary">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/recipes.js' %}"></script>
{% endblock %}
```

- [ ] **Rewrite `templates/recipes/recipe_confirm_delete.html`**

```html
{% extends "base.html" %}
{% block title %}Delete Recipe{% endblock %}
{% block content %}
<div class="detail-panel">
  <h1>Delete Recipe</h1>
  <p style="margin:1rem 0;color:var(--brown-700);">
    Are you sure you want to delete <strong>{{ object.name }}</strong>?
    Any batches linked to this recipe will remain (the link will be removed).
  </p>
  <form method="post">
    {% csrf_token %}
    <div class="btn-group">
      <button type="submit" class="btn btn-danger">Yes, Delete</button>
      <a href="{% url 'recipes:detail' object.pk %}" class="btn btn-secondary">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/recipes/
git commit -m "feat: recipe detail with Start Batch + Clone, redesigned form and delete pages"
```

---

## Task 9: Supporting Pages

**Files:**
- Modify (full rewrite): `templates/calculators/index.html`
- Modify (full rewrite): `templates/yeast/yeast.html`
- Modify (full rewrite): `templates/accounts/auth.html`
- Modify (full rewrite): `templates/accounts/profile.html`
- Modify: `templates/info.html`
- Modify: `templates/404.html`
- Modify: `templates/500.html`

- [ ] **Rewrite `templates/calculators/index.html`**

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Calculators{% endblock %}

{% block content %}
<div class="page-header">
  <h1 class="page-title">Calculators</h1>
</div>

<div class="calc-grid">
  <section class="calc-card">
    <h2>ABV &amp; Calories — Specific Gravity</h2>
    <div class="calc-inputs">
      <label>OG: <span id="og-sg-val">1.120</span>
        <input type="range" id="og-sg" min="1.000" max="1.300" step="0.001" value="1.120">
      </label>
      <label>FG: <span id="fg-sg-val">1.000</span>
        <input type="range" id="fg-sg" min="0.900" max="1.300" step="0.001" value="1.000">
      </label>
    </div>
    <div style="display:flex;gap:1rem;margin-bottom:0.75rem;font-size:0.82rem;">
      <label style="text-transform:none;font-size:0.82rem;font-weight:400;"><input type="radio" name="abv-formula" value="standard" checked> Standard</label>
      <label style="text-transform:none;font-size:0.82rem;font-weight:400;"><input type="radio" name="abv-formula" value="alternate"> Alternate</label>
    </div>
    <div class="calc-results">
      <p>ABV: <strong id="abv-sg">--</strong></p>
      <p>Attenuation: <strong id="att-sg">--</strong></p>
      <hr style="border:none;border-top:1px solid var(--border);margin:0.5rem 0;">
      <label style="text-transform:none;font-size:0.82rem;font-weight:400;">Glass size (oz):
        <select id="glass-size-sg" style="width:auto;"><option>5</option><option>8</option><option>12</option></select>
      </label>
      <p>Calories: <strong id="calories-sg">--</strong></p>
    </div>
  </section>

  <section class="calc-card">
    <h2>ABV &amp; Calories — Brix</h2>
    <div class="calc-inputs">
      <label>OG °Bx: <span id="og-brix-val">20.0</span>
        <input type="range" id="og-brix" min="0" max="40" step="0.1" value="20">
      </label>
      <label>FG °Bx: <span id="fg-brix-val">0.0</span>
        <input type="range" id="fg-brix" min="0" max="40" step="0.1" value="0">
      </label>
    </div>
    <div class="calc-results">
      <p>ABV: <strong id="abv-bx">--</strong></p>
      <p>Attenuation: <strong id="att-bx">--</strong></p>
      <hr style="border:none;border-top:1px solid var(--border);margin:0.5rem 0;">
      <label style="text-transform:none;font-size:0.82rem;font-weight:400;">Glass size (oz):
        <select id="glass-size-bx" style="width:auto;"><option>5</option><option>8</option><option>12</option></select>
      </label>
      <p>Calories: <strong id="calories-bx">--</strong></p>
    </div>
  </section>

  <section class="calc-card">
    <h2 class="tooltip">TOSNA 3.0 Schedule
      <span class="tooltip-trigger">(what is this?)</span>
      <div class="tooltip-content">
        <p><strong>TOSNA 3.0</strong> — Tailored Organic Staggered Nutrient Addition. Calculates Fermaid O/K additions based on OG (in Brix), yeast strain N-factor, and batch size. Split into 4 equal additions.</p>
        <p style="margin-top:0.5rem;"><strong>Formula:</strong> Total = (Brix × 10 × N-factor ÷ 50) × gallons. Fermaid K uses 60% of this amount.</p>
      </div>
    </h2>
    <p style="font-size:0.78rem;color:var(--brown-700);margin-bottom:0.75rem;">
      4 equal additions at 24h, 48h, 72h, and 1/3 sugar break.
    </p>
    <div class="calc-inputs">
      <label>Batch size (gal):
        <input type="number" id="batch-size" min="0.5" step="0.1" value="5" style="width:80px;">
      </label>
      <label>Nutrient:
        <select id="nutrient-type" style="width:auto;">
          <option value="FO">Fermaid O</option>
          <option value="FK">Fermaid K</option>
        </select>
      </label>
      <label>Yeast:
        <select id="yeast-strain" style="width:100%;">
          {% for y in yeasts %}<option>{{ y.name }}</option>{% endfor %}
        </select>
      </label>
    </div>
    <div class="calc-results" style="font-size:0.82rem;margin-bottom:0.75rem;">
      <p>N-factor: <strong id="n-factor-display">--</strong></p>
      <p>Pitch rate: <strong id="pitch-rate">--</strong> · Yeast needed: <strong id="yeast-needed">--</strong></p>
      <p>Total nutrient: <strong id="nutrient-total">--</strong></p>
    </div>
    <table class="calc-table">
      <thead><tr><th>Stage</th><th>Grams</th><th>tsp</th></tr></thead>
      <tbody id="sna-body"></tbody>
    </table>
  </section>

  <section class="calc-card">
    <h2>Sweetness Levels</h2>
    <table class="calc-table">
      <thead><tr><th>Style</th><th>SG Range</th><th>ABV Range</th></tr></thead>
      <tbody id="sweet-body"></tbody>
    </table>
  </section>
</div>

<div class="batch-builder">
  <h2>Batch Builder</h2>
  <div class="builder-inputs">
    <label>Batch size (gal): <span id="builder-size-val">5.0</span>
      <input type="range" id="builder-batch-size" min="1" max="10" step="0.5" value="5">
    </label>
    <label>Desired ABV (%): <span id="builder-abv-val">12.0</span>
      <input type="range" id="builder-desired-abv" min="0" max="20" step="0.5" value="12">
    </label>
    <label>Yeast:
      <select id="builder-yeast-strain">{% for y in yeasts %}<option>{{ y.name }}</option>{% endfor %}</select>
    </label>
    <label>Nutrient:
      <select id="builder-nutrient-type"><option value="FO">Fermaid O</option><option value="FK">Fermaid K</option></select>
    </label>
  </div>
  <div class="builder-results">
    <p>Honey needed: <strong id="honey-amt">--</strong> lbs</p>
    <p>TOSNA nutrient: <strong id="tosna-amt">--</strong></p>
    <p>Yeast pitch: <strong id="builder-yeast-pitch">--</strong></p>
  </div>
</div>

<details class="calc-info">
  <summary>How These Calculations Work</summary>
  <p><strong>Standard ABV:</strong></p>
  <pre><code>ABV = (OG – FG) × 131.25</code></pre>
  <p><strong>Alternate ABV</strong> (more accurate for higher-gravity meads):</p>
  <pre><code>ABV = (76.08 × (OG – FG) / (1.775 – OG)) × (FG / 0.794)</code></pre>
  <p><strong>Brix:</strong> <code>ABV ≈ (OB – FB) × 0.55</code></p>
  <p><strong>Attenuation:</strong> <code>((OG – FG) / (OG – 1)) × 100</code></p>
  <p><strong>Calories</strong> per glass: <code>((ABV/100) × 0.789 × 7) × (oz × 29.5735)</code></p>
</details>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/calculators.js' %}"></script>
{% endblock %}
```

- [ ] **Rewrite `templates/yeast/yeast.html`**

```html
{% extends "base.html" %}
{% block title %}Yeast Reference{% endblock %}

{% block content %}
<div class="page-header">
  <h1 class="page-title">Yeast Reference</h1>
</div>

<form method="get" style="display:flex;flex-wrap:wrap;gap:0.75rem;align-items:flex-end;margin-bottom:1rem;">
  <div>
    <label>Search</label>
    <input type="text" name="q" placeholder="Name or notes..." value="{{ q }}" style="width:200px;">
  </div>
  <div>
    <label>Tolerance</label>
    <select name="tolerance" style="width:auto;">
      <option value="">Any</option>
      {% for t in tolerance_options %}
        <option value="{{ t }}" {% if tolerance|default:'' == t|stringformat:"s" %}selected{% endif %}>{{ t }}%</option>
      {% endfor %}
    </select>
  </div>
  <div>
    <label>Attenuation</label>
    <select name="attenuation" style="width:auto;">
      <option value="">Any</option>
      {% for a in attenuation_options %}
        <option value="{{ a }}" {% if attenuation|default:'' == a|stringformat:"s" %}selected{% endif %}>{{ a }}%</option>
      {% endfor %}
    </select>
  </div>
  <button type="submit" class="btn btn-secondary">Filter</button>
  {% if q or tolerance or attenuation %}
    <a href="{% url 'yeast' %}" class="btn btn-ghost">Clear</a>
  {% endif %}
</form>

<div style="overflow-x:auto;">
<table class="calc-table" id="yeast-table" style="font-size:0.85rem;">
  <thead>
    <tr>
      <th style="cursor:pointer;">Name</th>
      <th style="cursor:pointer;">Type</th>
      <th style="cursor:pointer;">Tolerance</th>
      <th style="cursor:pointer;">Attenuation</th>
      <th>Temp Range</th>
      <th>Best For</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    {% for yeast in page_obj.object_list %}
    <tr>
      <td style="font-weight:600;">{{ yeast.name }}</td>
      <td><span class="badge {% if yeast.type == 'dry' %}badge-public{% else %}badge-private{% endif %}">{{ yeast.type }}</span></td>
      <td>{{ yeast.tolerance }}%</td>
      <td>{{ yeast.attenuation }}%</td>
      <td style="white-space:nowrap;">{{ yeast.temp_range }}</td>
      <td>{{ yeast.mead_style }}</td>
      <td style="font-size:0.78rem;color:var(--brown-700);">{{ yeast.notes }}</td>
    </tr>
    {% empty %}
    <tr><td colspan="7" style="text-align:center;color:var(--brown-700);padding:1.5rem;">No yeast strains found.</td></tr>
    {% endfor %}
  </tbody>
</table>
</div>

{% if page_obj.has_other_pages %}
<div style="display:flex;justify-content:center;gap:0.5rem;margin-top:1rem;">
  {% if page_obj.has_previous %}
    <a href="?{% if q %}q={{ q }}&{% endif %}{% if tolerance %}tolerance={{ tolerance }}&{% endif %}{% if attenuation %}attenuation={{ attenuation }}&{% endif %}page={{ page_obj.previous_page_number }}" class="btn btn-secondary">← Prev</a>
  {% endif %}
  <span class="btn btn-ghost" style="cursor:default;">{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
  {% if page_obj.has_next %}
    <a href="?{% if q %}q={{ q }}&{% endif %}{% if tolerance %}tolerance={{ tolerance }}&{% endif %}{% if attenuation %}attenuation={{ attenuation }}&{% endif %}page={{ page_obj.next_page_number }}" class="btn btn-secondary">Next →</a>
  {% endif %}
</div>
{% endif %}
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener("DOMContentLoaded", function() {
  const table = document.getElementById("yeast-table");
  const headers = table.querySelectorAll("th");
  let sortDir = 1;
  headers.forEach(function(header, index) {
    header.addEventListener("click", function() {
      const tbody = table.querySelector("tbody");
      const rows = Array.from(tbody.querySelectorAll("tr"));
      const isNum = !isNaN(parseFloat(rows[0]?.cells[index]?.textContent));
      rows.sort(function(a, b) {
        const at = a.cells[index]?.textContent.trim() || '';
        const bt = b.cells[index]?.textContent.trim() || '';
        return isNum ? sortDir * (parseFloat(at) - parseFloat(bt))
                     : sortDir * at.localeCompare(bt);
      });
      sortDir *= -1;
      rows.forEach(function(r) { tbody.appendChild(r); });
    });
  });
});
</script>
{% endblock %}
```

- [ ] **Rewrite `templates/accounts/auth.html`**

```html
{% extends "base.html" %}
{% block title %}Login or Register{% endblock %}

{% block content %}
<div class="auth-container">
  <div class="auth-box">
    <div class="auth-brand">
      <h1>Skål</h1>
      <p>Your mead brewing companion</p>
    </div>

    <div class="auth-tabs">
      <div class="auth-tab active" id="tab-login" onclick="showTab('login')">Login</div>
      <div class="auth-tab" id="tab-signup" onclick="showTab('signup')">Register</div>
    </div>

    <div id="form-login">
      <form method="post" action="{% url 'accounts:login' %}">
        {% csrf_token %}
        {% for field in login_form %}
          <div class="form-group">
            {{ field.label_tag }}
            {{ field }}
            {{ field.errors }}
          </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:0.5rem;">
          Sign In
        </button>
      </form>
    </div>

    <div id="form-signup" style="display:none;">
      <form method="post" action="{% url 'accounts:signup' %}">
        {% csrf_token %}
        {% for field in signup_form %}
          <div class="form-group">
            {{ field.label_tag }}
            {{ field }}
            {{ field.errors }}
          </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:0.5rem;">
          Create Account
        </button>
      </form>
    </div>
  </div>
</div>

<script>
function showTab(tab) {
  document.getElementById('form-login').style.display = tab === 'login' ? '' : 'none';
  document.getElementById('form-signup').style.display = tab === 'signup' ? '' : 'none';
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-signup').classList.toggle('active', tab === 'signup');
}
// If there are signup form errors, show the signup tab
{% if signup_form.errors %}showTab('signup');{% endif %}
</script>
{% endblock %}
```

- [ ] **Rewrite `templates/accounts/profile.html`**

```html
{% extends "base.html" %}
{% block title %}Profile{% endblock %}

{% block content %}
<div class="detail-panel">
  <h1>Profile</h1>
  <p style="font-size:0.8rem;color:var(--brown-700);margin-bottom:1.25rem;">
    Profile picture uses <a href="https://gravatar.com" target="_blank">Gravatar</a> based on your email.
  </p>

  <h2>Account Info</h2>
  <form method="post" enctype="multipart/form-data" style="margin-bottom:1.5rem;">
    {% csrf_token %}
    {% for field in form %}
      <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {{ field.errors }}
      </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Save Changes</button>
  </form>

  <hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0;">
  <h2>Change Password</h2>
  <form method="post" action="{% url 'accounts:password_change' %}" style="margin-bottom:1.5rem;">
    {% csrf_token %}
    {% for field in password_form %}
      <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {{ field.errors }}
      </div>
    {% endfor %}
    <button type="submit" class="btn btn-secondary">Update Password</button>
  </form>

  <hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0;">
  <h2>Export Your Data</h2>
  <form method="post" action="{% url 'accounts:export_user_data' %}">
    {% csrf_token %}
    <div class="form-group">
      <label for="format">Format</label>
      <select name="format" id="format" style="width:auto;">
        <option value="json">JSON</option>
        <option value="csv">CSV</option>
        <option value="txt">Text</option>
        <option value="pdf">PDF</option>
        <option value="sql">SQL Dump</option>
      </select>
    </div>
    <div class="form-group" style="display:flex;align-items:center;gap:0.5rem;">
      <input type="checkbox" name="include_public" id="include_public" style="width:auto;">
      <label for="include_public" style="text-transform:none;font-size:0.875rem;color:var(--brown-900);margin:0;">
        Include public recipes and batches
      </label>
    </div>
    <button type="submit" class="btn btn-secondary">Download Export</button>
  </form>
</div>
{% endblock %}
```

- [ ] **Update `templates/info.html`** — the written content (history paragraphs, mead type definitions, brewing terms) is unchanged. Only the outer structural wrappers are replaced.

Open the current `templates/info.html`. Keep every `<p>`, `<ul>`, `<li>`, `<dt>`, `<dd>` element exactly as-is. Change only:

1. Replace the outer `<div class="container mx-auto mt-6"><div class="calc-section p-6"><div class="grid grid-cols-1 gap-8"><div>` wrapper around the History section with `<div class="card" style="margin-bottom:1.25rem;">`

2. Replace the outer `<div class="container mx-auto mt-6"><div class="calc-section p-6"><div class="grid grid-cols-2 gap-8">` wrapper around the Types/Terms section with `<div class="info-grid">`

3. Replace each `<div>` column inside the grid with `<div class="card">`

4. Update the `{% extends %}` and `{% block title %}` to:
```html
{% extends "base.html" %}
{% block title %}Mead History &amp; Types{% endblock %}

{% block content %}
<div class="page-header">
  <h1 class="page-title">History &amp; Reference</h1>
</div>
```

The closing `{% endblock %}` stays at the end. No content changes — structural wrappers only.

- [ ] **Rewrite `templates/404.html`**

```html
{% extends "base.html" %}
{% block title %}404 — Not Found{% endblock %}
{% block content %}
<div style="text-align:center;padding:4rem 1rem;">
  <p style="font-size:4rem;">🍯</p>
  <h1 style="font-family:var(--font-serif);margin-bottom:0.5rem;">404</h1>
  <p style="color:var(--brown-700);margin-bottom:1.5rem;">This page seems to have fermented away.</p>
  <a href="/" class="btn btn-primary">Back to Home</a>
</div>
{% endblock %}
```

- [ ] **Rewrite `templates/500.html`**

```html
{% extends "base.html" %}
{% block title %}500 — Server Error{% endblock %}
{% block content %}
<div style="text-align:center;padding:4rem 1rem;">
  <p style="font-size:4rem;">⚗️</p>
  <h1 style="font-family:var(--font-serif);margin-bottom:0.5rem;">500</h1>
  <p style="color:var(--brown-700);margin-bottom:1.5rem;">Something went sideways in the fermentation chamber.</p>
  <a href="/" class="btn btn-primary">Back to Home</a>
</div>
{% endblock %}
```

- [ ] **Commit**

```bash
git add templates/
git commit -m "feat: redesign calculators, yeast table, auth, profile, info, error pages"
```

---

## Task 10: Profile View — Add password_form Context

The profile template uses `password_form` in context but `ProfileUpdateView` doesn't currently pass it.

**Files:**
- Modify: `apps/accounts/views.py`

- [ ] **Add `password_form` to `ProfileUpdateView.get_context_data`**

```python
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    login_url = reverse_lazy("accounts:login")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['password_form'] = CustomPasswordChangeForm(self.request.user)
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated.')
        return super().form_valid(form)
```

- [ ] **Run full test suite**

```bash
pytest -v --tb=short
```
Expected: all tests pass

- [ ] **Commit**

```bash
git add apps/accounts/views.py
git commit -m "fix: pass password_form context to profile template"
```

---

## Final Verification

- [ ] **Run full test suite**

```bash
pytest -v
```
Expected: all tests pass

- [ ] **Django system check**

```bash
python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

- [ ] **Verify no missing migrations**

```bash
python manage.py makemigrations --check --dry-run
```
Expected: `No changes detected`

- [ ] **Manual smoke test** — start dev server (requires a running Postgres or adjust DATABASES in local settings) and check:
  - Home page loads with sidebar
  - Batch list shows cellar rows
  - Recipe list shows recipe rows
  - Calculators render and compute
  - Auth page shows login/register tabs
  - Profile page has all three sections
