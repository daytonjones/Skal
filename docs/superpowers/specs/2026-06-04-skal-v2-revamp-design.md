# Skål v2 Revamp — Design Spec
**Date:** 2026-06-04  
**Status:** Approved for implementation planning  
**Branch:** `v2`

---

## 1. Goals & Constraints

### Goals
- Complete visual and UX overhaul — warm amber/honey craft aesthetic
- Fix all known bugs and dead-code artifacts from the initial v2 port
- Add HTMX for server-driven interactivity (replaces ad-hoc fetch() calls)
- Add five new features (dashboard, start-batch-from-recipe, recipe clone, live search, checklist notes)
- Keep every existing feature — no regressions

### Hard Constraints
- **No generic AI aesthetic.** No default SaaS blue, no Bootstrap defaults, no cookie-cutter layouts. Every design decision should feel like a passionate brewer made it.
- **No build step added.** HTMX via CDN, custom CSS (no Tailwind build pipeline). Django templates only — no React, no Vue.
- **All existing data models remain intact.** Migrations only add or remove fields; no destructive schema changes.
- **Docker-first deployment** remains unchanged.

---

## 2. Visual Design System

### Color Palette
| Token | Hex | Usage |
|---|---|---|
| `brown-950` | `#1c0a00` | Sidebar background, darkest text |
| `brown-900` | `#451a03` | Primary text, headings |
| `brown-700` | `#92400e` | Secondary text, labels |
| `amber-600` | `#d97706` | Primary accent, active state, CTAs |
| `amber-400` | `#f59e0b` | Hover states, highlights |
| `amber-100` | `#fef3c7` | Progress bar backgrounds, subtle fills |
| `cream-50`  | `#fef9ef` | Page background |
| `cream-100` | `#fef3c7` | Card backgrounds |
| `white`     | `#ffffff` | Card/panel surfaces |
| `border`    | `#e9d5a1` | All borders, dividers |

**Stage colors** (used on batch status throughout the app):
- Active/Primary: amber `#d97706`
- Secondary: purple `#7c3aed`
- Bottled/Complete: green `#16a34a`
- No FG yet (in progress): amber at lower opacity

### Typography
- **Body/UI:** System font stack: `'Georgia', 'Times New Roman', serif` for the journal feel on headings and prominent text; `system-ui, sans-serif` for UI labels, inputs, small text
- **Heading sizes:** 1.5rem (h1), 1.1rem (h2), 0.85rem (h3)
- **Label style:** `font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: brown-700`

### Flask Fill Indicator
A reusable CSS component: a small flask/vial shape (border-radius bottom, rectangular top) with a fill level driven by a CSS custom property `--fill`. The fill color shifts:
- 0–33%: amber-100 (just started)
- 34–66%: amber-400
- 67–99%: amber-600
- 100%: green (complete)

Used on batch list rows and dashboard active fermentation cards.

### Dark Mode
Retained as a user preference (stored in `User.theme`). The dark palette inverts: cream backgrounds → `#1a0f00`, white surfaces → `#2a1500`, border → `#5a3a1a`, text → `#f5e6c8`.

---

## 3. Layout & Navigation

### Sidebar (persistent, all authenticated pages)
- **Width:** 200px desktop, collapses to 60px icon-only on tablet (≤900px), slides off-canvas on mobile (≤600px) with a hamburger toggle
- **Background:** `brown-950` (`#1c0a00`)
- **Logo/brand:** "Skål" in amber serif at top
- **Nav items** (icon + label): Home, Recipes, Batches, Calculators, Yeast Info, — divider — Profile
- **Active state:** amber left border + amber text
- **Bottom:** User avatar (gravatar or uploaded) + username + logout link

### Main content area
- Fills remaining width after sidebar
- Background: `cream-50`
- Max-width: 1100px, centered with padding

### Mobile nav
- Sidebar hidden by default; hamburger button (top-left) toggles it as an overlay drawer
- No bottom tab bar — the drawer approach is sufficient for this app's usage pattern

---

## 4. Pages

### 4.1 Home / Dashboard
Rendered by `HomeView`. Requires login.

**Sections (top to bottom):**

1. **Greeting header** — "Welcome back, {first_name}" + current date + two inline buttons: "🍯 New Batch", "📜 New Recipe"
2. **Stat tiles** — 4 tiles in a row: Total Batches · Currently Fermenting (highlighted in amber) · Average ABV · Total Recipes
3. **Two-column body:**
   - Left (60%): "Active Fermentations" — one row per non-bottled batch owned by user; each row has flask fill indicator + name + day count + stage + progress bar + "X of 8 steps"
   - Right (40%): "Quick Actions" (New Batch, New Recipe, Calculators) + "Last Bottled" (most recent `bottled_done=True` batch)
4. **Photo strip** — "From the Cellar": horizontal scrollable strip of the most recent 10 `BatchImage` records across all the user's batches. **Only rendered when at least one image exists.** Images are clickable (link to their batch detail). If no images: section omitted entirely, no empty state shown.

**Context additions needed in HomeView:**
- `active_batches`: Batch queryset where `user=request.user` and `bottled_done=False`, ordered by `-primary_date`
- `total_batches`, `active_count`, `avg_abv`, `total_recipes`: computed stats
- `last_bottled`: most recent batch with `bottled_done=True`
- `recent_images`: `BatchImage.objects.filter(batch__user=request.user).select_related('batch').order_by('-id')[:10]`

---

### 4.2 Batch List (`/batches/`)
**Cellar Rows** layout.

- Page heading: "Your Cellar" + "Add New Batch" button (top right)
- **Search bar** (HTMX live search): `hx-get="/batches/" hx-trigger="input changed delay:300ms" hx-target="#batch-rows" hx-include="[name='q']"` — filters by batch name, returns only the `#batch-rows` partial
- **Filter strip**: Stage filter buttons (All · Active · Secondary · Bottled) — also HTMX, same target
- **Batch rows** (`#batch-rows`): each row contains:
  - Flask fill indicator (CSS, fill % = `(count of _done=True fields / 8) * 100`)
  - Color-coded left border (stage color)
  - Batch name + linked to detail
  - Date + batch size
  - ABV (if fg set) or "—"
  - Stage badge (Active / Secondary / Bottled / In Progress)
  - Checklist mini-progress bar + "X/8"
  - Edit icon (owner only)

**No more `<select>` dropdown.** If zero batches: friendly empty state with a "Start your first batch" CTA.

**Computed property on Batch model** (`stage` property):
```python
@property
def stage(self):
    if self.bottled_done: return 'bottled'
    if self.rack_secondary_done: return 'secondary'
    if self.pitch_yeast_done: return 'active'
    return 'planned'
```

---

### 4.3 Batch Detail (`/batches/<pk>/`)
No structural changes to existing data, improved visual layout.

- **Hero section**: Batch name, date, batch size, OG/FG, ABV (large), stage badge
- **Flask gauge** (larger version, 80px tall) as the visual centerpiece
- **Checklist** (HTMX-powered, replaces existing manual fetch):
  - Each item: checkbox (`hx-post`, `hx-target` replaces the list item) + label + date stamp when done + **inline note field**
  - Note field: appears when step is checked (or always shown if note already exists); saves on blur via `hx-trigger="blur" hx-post="/batches/<pk>/checklist-note/"`
  - Progress bar updates via HTMX out-of-band swap (`HX-Trigger` response header)
- **Notes section**: batch-level notes (unchanged)
- **Images gallery**: unchanged behavior, improved visual layout
- **Actions** (owner only): Edit · Delete · Toggle Visibility · Print

---

### 4.4 Batch Create/Edit (`/batches/new/`, `/batches/<pk>/edit/`)
- Split into two logical sections with a visual divider:
  1. **Batch Details** — recipe link, name, batch size, OG, FG, dates, notes, visibility, images
  2. **Checklist** — all the done/date fields (can be pre-filled on create, updated via detail page HTMX after creation)
- Date inputs already use `type="date"` — keep that
- Image upload: keep existing multi-file behavior, improve the preview UI (batches.js already handles this)

---

### 4.5 Recipe List (`/recipes/`)
Same row-pattern as batch list for consistency.

- Page heading: "Recipes" + "New Recipe" button
- **Search bar** (HTMX live): filters by recipe name
- **Recipe rows**: name + batch size + ingredient count + owner badge (if not current user) + public/private badge + edit icon (owner only)
- **Featured recipe panel** (random, below the list): keep this — it's a nice touch, but re-style it to match the new aesthetic
- **No more `<select>` dropdown.**

---

### 4.6 Recipe Detail (`/recipes/<pk>/`)
- Ingredients list (unchanged data)
- Instructions block (unchanged)
- Two new action buttons (owner only):
  - **"🍺 Start a Batch"** — navigates to `/batches/new/` with `?recipe=<pk>` pre-populating the recipe field and batch name
  - **"📋 Clone Recipe"** — POST to `/recipes/<pk>/clone/`, creates a copy owned by the current user with name "Copy of {name}", redirects to the new recipe's edit page
- Toggle visibility, Edit, Delete (existing, re-styled)

---

### 4.7 Recipe Create/Edit
- No structural changes
- Visual improvements: form layout, ingredient table styling
- `RecipeUpdateView.post()` **fixed**: must update honey/water/yeast RecipeIngredient records (order 0/1/2) when form is submitted, not just the formset (order ≥ 3)

---

### 4.8 Calculators (`/calculators/`)
- Existing calculation logic unchanged (it's correct)
- Visual overhaul: amber-themed calc cards, better mobile layout
- TOSNA tooltip converted from CSS hover to a proper `<details>` element (more accessible, works on mobile)

---

### 4.9 Yeast Reference (`/yeast/`)
- Table re-styled with amber headers, alternating row colors
- Search and filter controls re-styled (already functional via server-side filtering)
- Client-side sort JS kept (it works fine)

---

### 4.10 Auth (`/accounts/login/`, `/accounts/signup/`)
- Single page with two panels: Login left, Register right (current structure)
- Visual overhaul: amber theme, less form-dump feel, proper fieldset styling

---

### 4.11 Profile (`/accounts/profile/`)
- Three clearly separated sections with headings and dividers:
  1. Profile info (name, email, theme toggle)
  2. Change password
  3. Export data
- Logout moved to sidebar (bottom of nav) rather than buried in profile page
- Theme toggle: change from radio buttons to a visual light/dark toggle switch

---

### 4.12 Info Page (`/info/`)
- Content unchanged (mead history + definitions — it's well-written)
- Visual re-styling only: amber headers, better definition list layout, readable line length

---

## 5. Backend Changes

### 5.1 Bug Fixes

**BUG-1: Recipe edit doesn't save primary ingredients**  
`RecipeUpdateView.post()` calls `formset.save()` but never updates the `RecipeIngredient` records at order 0, 1, 2 (honey, water, yeast). Fix: after `self.object = form.save()`, update or create the three primary `RecipeIngredient` rows using `update_or_create` based on order position.

**BUG-2: Checklist AJAX endpoint too permissive**  
`update_checklist_item` uses `hasattr(batch, field)` — any field on the Batch model can be set. Fix: whitelist the allowed field names explicitly:
```python
ALLOWED_CHECKLIST_FIELDS = {
    'create_must_done', 'pitch_yeast_done', 'fo_24h_done',
    'fo_48h_done', 'fo_72h_done', 'fo_1_3_break_done',
    'rack_secondary_done', 'bottled_done',
}
```

**BUG-3: ProfileUpdateView wrong model attribute**  
`model = settings.AUTH_USER_MODEL` is a string, not a model class. Fix: `from .models import User` and `model = User`. Works currently only because `get_object()` is overridden, but it's wrong and will break in edge cases.

**BUG-4: RecipeIngredientForm creates ingredients with wrong type**  
`save()` calls `Ingredient.objects.get_or_create(name=name)` without specifying `type`, so new additives added via the extra formset default to `'honey'`. Fix: pass `defaults={'type': 'additive'}` in the `get_or_create` call inside `RecipeIngredientForm.save()` — the extra formset is always for additives, never honey or yeast (those have dedicated form fields).

---

### 5.2 Dead Code Removal

| Item | Action |
|---|---|
| `app/` directory (FastAPI v1) | Delete entirely |
| `apps/calculators/utils.py` | Delete (never imported or called) |
| `static/js/batch_image_preview.js` | Delete (not referenced in any template) |
| `User.gravatar_url` field | Remove field + migration (value is always computed dynamically by the template tag; it was added but never set) |
| `django-crispy-forms` | Remove from `requirements.txt` and `INSTALLED_APPS` (configured but zero templates use it) |

---

### 5.3 Dependency Updates

```
# requirements.txt after changes
Django==5.2.3          # already current LTS — no change
psycopg2-binary==2.9.10
gunicorn==23.0.0
Pillow==11.1.0
reportlab==4.2.5
whitenoise==6.8.0
# removed: django-crispy-forms
```

HTMX added via CDN `<script>` in `base.html` — no pip package needed.

---

### 5.4 New Models / Migrations

**New: `ChecklistNote` on Batch**  
Rather than a separate model (overkill for 8 fields), add 8 nullable `TextField` fields directly to `Batch`:

```python
create_must_note    = models.TextField(blank=True, default='')
pitch_yeast_note    = models.TextField(blank=True, default='')
fo_24h_note         = models.TextField(blank=True, default='')
fo_48h_note         = models.TextField(blank=True, default='')
fo_72h_note         = models.TextField(blank=True, default='')
fo_1_3_break_note   = models.TextField(blank=True, default='')
rack_secondary_note = models.TextField(blank=True, default='')
bottled_note        = models.TextField(blank=True, default='')
```

One migration adds these 8 fields and removes `gravatar_url` from User.

**New: `Batch.stage` property** (no migration — computed):
```python
@property
def stage(self):
    if self.bottled_done: return 'bottled'
    if self.rack_secondary_done: return 'secondary'
    if self.pitch_yeast_done: return 'active'
    return 'planned'
```

---

### 5.5 New URLs & Views

| URL | View | Purpose |
|---|---|---|
| `POST /recipes/<pk>/clone/` | `clone_recipe` | Copy recipe, redirect to edit |
| `GET /batches/new/?recipe=<pk>` | `BatchCreateView` (updated) | Pre-populate recipe + name from query param |
| `POST /batches/<pk>/checklist-note/` | `update_checklist_note` | Save note for one checklist step (HTMX) |
| `GET /batches/?q=&stage=` | `BatchListView` (updated) | HTMX partial response for live search |
| `GET /recipes/?q=` | `RecipeListView` (updated) | HTMX partial response for live search |

**HTMX partial responses**: views detect `HX-Request` header and return only the rows partial template instead of the full page.

---

### 5.6 Django Messages Integration

Add `django.contrib.messages` context processor (already in default install). Add toast notification partial template. On every create/update/delete/clone/export success or failure, call `messages.success(request, "...")` or `messages.error(...)`. Base template renders them as auto-dismissing toasts (amber for success, red for error) positioned top-right.

---

### 5.7 `apps/yeast` Registration

Currently `apps/yeast` is not in `INSTALLED_APPS` (has no models so Django never complained). Add a proper `AppConfig`, add `"apps.yeast"` to `INSTALLED_APPS`, add `apps/yeast/__init__.py`. No migrations needed (no models).

---

## 6. CSS Architecture

Single `static/css/styles.css` remains (no build step). Restructured into sections:

1. **CSS custom properties** (`:root` + `.dark`) — all colors, spacing, font stacks as variables
2. **Reset / base** — minimal
3. **Layout** — sidebar, main content area, responsive breakpoints
4. **Components** — flask indicator, stat tiles, cellar rows, stage badges, progress bars, toast notifications, buttons, form elements
5. **Page-specific** — dashboard, batch detail, recipe form, calculators, yeast table
6. **Print** — existing `@media print` rules, updated for new layout

The existing CSS file is replaced entirely (it has significant dead/conflicting rules and mixes layout utilities with component styles).

---

## 7. HTMX Integration Points

| Feature | HTMX pattern |
|---|---|
| Batch checklist toggle | `hx-post`, `hx-target="closest li"`, `hx-swap="outerHTML"` |
| Checklist note save | `hx-post`, `hx-trigger="blur"`, `hx-swap="none"` + `HX-Trigger` response for toast |
| Batch live search | `hx-get`, `hx-trigger="input changed delay:300ms"`, `hx-target="#batch-rows"` |
| Recipe live search | Same pattern, `hx-target="#recipe-rows"` |
| Stage filter (batches) | `hx-get`, `hx-trigger="click"`, `hx-include="[name='q']"` |
| Toast messages | Out-of-band swap via `HX-Trigger: {"showToast": "..."}` response header + JS handler |

No Alpine.js needed — the HTMX patterns above cover all interactivity without additional JS libraries.

---

## 8. What Does NOT Change

- All existing URL patterns (no breaking changes to routes)
- All existing database migrations (additive only)
- Docker Compose setup and entrypoint
- Export functionality (JSON/CSV/TXT/PDF/SQL) — works, just gets a success toast
- Yeast data (hardcoded list in `apps/yeast/views.py`)
- ABV and calorie calculation formulas
- TOSNA schedule calculation
- Session management and auth settings
- Media file handling (image upload + 800×800 resize)
- Gravatar template tag

---

## 9. Out of Scope for This Revamp

- API endpoints / REST API
- Email verification or password reset via email
- Batch sharing via public URL (is_public covers this already)
- Notifications / reminders (e.g., "it's been 7 days since you checked your batch")
- Mobile app
- Multi-tenancy or teams

---

## 10. Implementation Order

Recommended sequence to minimize broken states during development:

1. **Foundation** — dead code removal, dependency bumps, bug fixes, yeast app registration
2. **Models + migrations** — checklist notes fields, remove gravatar_url, add `stage` property
3. **CSS + base template** — new design system, sidebar, dark mode, toast infrastructure
4. **Dashboard** — HomeView context additions, dashboard template
5. **Batch list + partial** — HTMX live search, cellar rows, stage filter
6. **Batch detail + checklist** — HTMX checklist, notes inline, flask gauge
7. **Recipe list + partial** — HTMX live search, recipe rows
8. **Recipe detail** — clone action, start-batch action
9. **Remaining pages** — calculators, yeast, auth, profile
10. **Polish pass** — messages/toasts throughout, responsive QA, print styles
