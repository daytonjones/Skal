# Bjorn Pantry Awareness — Design Spec
**Date:** 2026-06-09
**Branch:** bjorn_pantry_access
**Status:** Approved

## Goal

Give Bjorn (the AI brewing assistant) awareness of the user's pantry so recipe suggestions are grounded in what the user has on hand. Bjorn should prefer on-hand ingredients, suggest pantry substitutes when a needed ingredient is missing, and only flag must-buy gaps when no reasonable substitute exists.

## Approach

Option A: system prompt injection only. No new models, migrations, tool schemas, or templates. The pantry data is injected into the existing `_build_system_prompt()` function alongside recipes and batches.

Option B (future): extend the `suggest_recipe` tool schema with an optional `missing_ingredients` array (each item: `name`, `substitute_from_pantry` or `null`) and render a structured "what you need" card in the chat UI. Deferred until plain-text callouts prove insufficient.

## Data Injection

Add a pantry query to `_build_system_prompt(user)` in `apps/ai/views.py`:

```python
from apps.pantry.models import PantryItem

pantry_items = (
    PantryItem.objects.filter(user=user)
    .select_related('ingredient')
    .order_by('ingredient__type', 'ingredient__name')
)
```

Group by ingredient type and render as a compact block:

```
The user's pantry:
Honey: Wildflower (12 lbs), Orange Blossom (6 lbs)
Yeast: Lalvin D-47 (2 packets), EC-1118 (1 packet)
Additives: Fermaid-O, GoFerm, Bentonite
```

If a type has no items, omit it. If the pantry is entirely empty, emit `Pantry: (empty)` so Bjorn knows it exists but has nothing to offer.

Quantity and notes are included when present; omitted when blank.

## System Prompt Instructions

Append the following paragraph to the system prompt, after the pantry block:

> "When suggesting a recipe, cross-reference the ingredients against the user's pantry. If a needed ingredient is on hand, note it. If it's missing but a pantry substitute could work (e.g. EC-1118 instead of 71B), suggest the substitution and explain the trade-off briefly. Only flag an ingredient as 'needs to be purchased' when no reasonable substitute exists in the pantry."

## Scope

- **One file changed:** `apps/ai/views.py`
  - Add `PantryItem` import
  - Add pantry query in `_build_system_prompt()`
  - Add pantry text block construction (grouped by type)
  - Add pantry section and substitution instructions to the returned prompt string
- No model changes, no migrations, no new templates, no tool schema changes

## Testing

Add a unit test to `tests/apps/ai/test_views.py` covering:
- Pantry items appear in the system prompt output, grouped by type
- Empty pantry emits `Pantry: (empty)`
- Quantities and notes render correctly when present

Existing view tests continue to pass unchanged.
