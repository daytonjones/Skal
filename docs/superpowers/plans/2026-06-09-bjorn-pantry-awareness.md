# Bjorn Pantry Awareness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inject the user's pantry into Bjorn's system prompt so he can suggest pantry-grounded recipes, propose substitutes from on-hand ingredients, and flag must-buy gaps.

**Architecture:** `_build_system_prompt(user)` in `apps/ai/views.py` already injects recipes and batches; we add a pantry query and text block in the same function, plus substitution instructions at the end of the prompt. No schema, template, or model changes required.

**Tech Stack:** Django ORM, pytest-django, existing `PantryItem` / `Ingredient` models.

---

### Task 1: Write failing tests for pantry section in system prompt

**Files:**
- Modify: `tests/apps/ai/test_views.py`

- [ ] **Step 1: Add the new test class at the bottom of `tests/apps/ai/test_views.py`**

Append this class after the existing `TestAiContextProcessor` class:

```python
@pytest.mark.django_db
class TestBuildSystemPromptPantry:
    def test_pantry_items_appear_grouped_by_type(self, user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        honey = Ingredient.objects.create(name='Wildflower', type=Ingredient.TYPE_HONEY)
        yeast = Ingredient.objects.create(name='Lalvin D-47', type=Ingredient.TYPE_YEAST)
        PantryItem.objects.create(user=user, ingredient=honey, quantity='12 lbs')
        PantryItem.objects.create(user=user, ingredient=yeast)

        prompt = _build_system_prompt(user)

        assert 'Honey: Wildflower (12 lbs)' in prompt
        assert 'Yeast: Lalvin D-47' in prompt

    def test_quantity_omitted_when_blank(self, user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        additive = Ingredient.objects.create(name='Fermaid-O', type=Ingredient.TYPE_ADDITIVE)
        PantryItem.objects.create(user=user, ingredient=additive, quantity='')

        prompt = _build_system_prompt(user)

        assert 'Fermaid-O' in prompt
        assert 'Fermaid-O ()' not in prompt

    def test_empty_pantry_shows_empty_label(self, user):
        from apps.ai.views import _build_system_prompt

        prompt = _build_system_prompt(user)

        assert 'Pantry: (empty)' in prompt

    def test_other_user_pantry_not_included(self, user, other_user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        honey = Ingredient.objects.create(name='Manuka', type=Ingredient.TYPE_HONEY)
        PantryItem.objects.create(user=other_user, ingredient=honey)

        prompt = _build_system_prompt(user)

        assert 'Manuka' not in prompt

    def test_substitution_instructions_in_prompt(self, user):
        from apps.ai.views import _build_system_prompt

        prompt = _build_system_prompt(user)

        assert 'substitute' in prompt.lower()
        assert 'needs to be purchased' in prompt
```

- [ ] **Step 2: Run the new tests to verify they all fail**

```bash
pytest tests/apps/ai/test_views.py::TestBuildSystemPromptPantry -v
```

Expected: 5 failures. The first four fail because `_build_system_prompt` doesn't yet include pantry data; the last fails because the substitution instructions aren't in the prompt.

---

### Task 2: Implement pantry injection in `_build_system_prompt`

**Files:**
- Modify: `apps/ai/views.py:11-72`

- [ ] **Step 1: Add the `PantryItem` import**

In `apps/ai/views.py`, the current imports block is:

```python
from apps.batches.models import Batch
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient
```

Change it to:

```python
from apps.batches.models import Batch
from apps.pantry.models import PantryItem
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient
```

- [ ] **Step 2: Replace `_build_system_prompt` with the pantry-aware version**

Replace the entire `_build_system_prompt` function (lines 27–72) with:

```python
def _build_system_prompt(user):
    recipes = (
        Recipe.objects.filter(user=user)
        .prefetch_related('ingredients')
        .order_by('-pk')[:10]
    )
    batches = Batch.objects.filter(user=user).order_by('-primary_date')[:10]
    pantry_items = (
        PantryItem.objects.filter(user=user)
        .select_related('ingredient')
        .order_by('ingredient__type', 'ingredient__name')
    )

    recipe_lines = []
    for r in recipes:
        all_ings = list(r.ingredients.all())
        honeys = [ing.name for ing in all_ings if ing.type == 'honey']
        yeasts = [ing.name for ing in all_ings if ing.type == 'yeast']
        recipe_lines.append(
            f"- {r.name}: {r.batch_size} gal, "
            f"honey: {', '.join(honeys) or 'unspecified'}, "
            f"yeast: {', '.join(yeasts) or 'unspecified'}"
        )

    batch_lines = []
    for b in batches:
        gravity = f"OG {b.og}"
        if b.fg:
            gravity += f" → FG {b.fg}"
        batch_lines.append(f"- {b.name}: {b.stage}, {gravity}")

    pantry_by_type = {}
    for item in pantry_items:
        t = item.ingredient.type
        label = item.ingredient.name
        if item.quantity:
            label += f" ({item.quantity})"
        pantry_by_type.setdefault(t, []).append(label)

    if pantry_by_type:
        type_labels = {'honey': 'Honey', 'yeast': 'Yeast', 'additive': 'Additives'}
        pantry_lines = [
            f"{type_labels[t]}: {', '.join(pantry_by_type[t])}"
            for t in ['honey', 'yeast', 'additive']
            if t in pantry_by_type
        ]
        pantry_text = "The user's pantry:\n" + '\n'.join(pantry_lines)
    else:
        pantry_text = "Pantry: (empty)"

    recipes_text = '\n'.join(recipe_lines) if recipe_lines else 'No recipes yet.'
    batches_text = '\n'.join(batch_lines) if batch_lines else 'No batches yet.'

    return (
        "You are Bjorn, a friendly Viking mead-making expert and brewing assistant "
        "for Skål, a mead tracking app. You help with mead recipes, fermentation questions, "
        "ingredient suggestions, and troubleshooting. Be warm and knowledgeable — a Viking "
        "who loves sharing mead wisdom. Occasional Viking flavour is welcome but keep it "
        "natural, not forced.\n\n"
        "IMPORTANT: You ONLY answer questions related to mead making, homebrewing, "
        "fermentation, brewing ingredients, brewing equipment, and mead or brewing history. "
        "If asked about anything outside these topics — coding, general knowledge, writing, "
        "or any other unrelated subject — politely decline and redirect the user to mead "
        "topics. Do not assist with tasks outside your brewing expertise.\n\n"
        f"The user's recipes:\n{recipes_text}\n\n"
        f"The user's batches:\n{batches_text}\n\n"
        f"{pantry_text}\n\n"
        "When suggesting a new recipe, structure it with: name, batch size (gallons), "
        "honey type and amount (lbs), yeast strain, any additional ingredients, and brief "
        "notes — so the user can easily add it to Skål.\n\n"
        "When suggesting a recipe, cross-reference the ingredients against the user's pantry. "
        "If a needed ingredient is on hand, note it. If it's missing but a pantry substitute "
        "could work (e.g. EC-1118 instead of 71B), suggest the substitution and explain the "
        "trade-off briefly. Only flag an ingredient as 'needs to be purchased' when no "
        "reasonable substitute exists in the pantry."
    )
```

- [ ] **Step 3: Run the new tests to verify they all pass**

```bash
pytest tests/apps/ai/test_views.py::TestBuildSystemPromptPantry -v
```

Expected: 5 passed.

- [ ] **Step 4: Run the full AI test suite to verify no regressions**

```bash
pytest tests/apps/ai/test_views.py -v
```

Expected: 25 passed (20 existing + 5 new).

---

### Task 3: Commit

- [ ] **Step 1: Stage and commit**

```bash
git add apps/ai/views.py tests/apps/ai/test_views.py
git commit -m "$(cat <<'EOF'
feat: give Bjorn pantry awareness for ingredient-grounded suggestions

Injects the user's pantry (grouped by type) into Bjorn's system prompt.
Bjorn now prefers on-hand ingredients, suggests pantry substitutes when
something is missing, and flags must-buy gaps only when no substitute exists.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 2: Verify clean state**

```bash
git status
```

Expected: `nothing to commit, working tree clean`
