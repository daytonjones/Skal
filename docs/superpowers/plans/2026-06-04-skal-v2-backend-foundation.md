# Skål v2 — Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all known bugs, remove dead code, bump dependencies, add new models/endpoints, and wire up HTMX-compatible views — leaving every existing feature working and tested.

**Architecture:** Additive-only migrations; new endpoints alongside existing ones; HTMX partials via `HX-Request` header detection in existing class-based views. No frontend changes in this plan.

**Tech Stack:** Django 5.2.3, PostgreSQL, pytest + pytest-django (new), HTMX 2.x (CDN only — no Python package needed yet, referenced in Plan B templates)

**Spec:** `docs/superpowers/specs/2026-06-04-skal-v2-revamp-design.md`

---

## File Map

**New files:**
- `pytest.ini`
- `skal/test_settings.py`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/apps/__init__.py`
- `tests/apps/batches/__init__.py`
- `tests/apps/batches/test_models.py`
- `tests/apps/batches/test_views.py`
- `tests/apps/recipes/__init__.py`
- `tests/apps/recipes/test_views.py`
- `tests/apps/accounts/__init__.py`
- `tests/apps/accounts/test_views.py`
- `apps/yeast/__init__.py` ← was missing, makes yeast a proper app
- `apps/yeast/apps.py`

**Modified files:**
- `requirements.txt` — bump deps, remove crispy-forms, add pytest-django
- `skal/settings.py` — remove crispy_forms from INSTALLED_APPS, add apps.yeast
- `apps/accounts/models.py` — remove `gravatar_url` field
- `apps/accounts/views.py` — fix `ProfileUpdateView.model`; add `messages` calls
- `apps/accounts/migrations/0003_remove_user_gravatar_url.py` — new migration
- `apps/batches/models.py` — add 8 note fields, `stage` property, `checklist_progress` property
- `apps/batches/views.py` — fix checklist security; add HTMX partial support; add `update_checklist_note`
- `apps/batches/urls.py` — add `checklist-note/` URL
- `apps/batches/migrations/0004_batch_checklist_notes.py` — new migration
- `apps/recipes/models.py` — no change
- `apps/recipes/views.py` — fix `RecipeUpdateView.post()`; add `clone_recipe`; update `BatchCreateView` pre-fill
- `apps/recipes/forms.py` — fix ingredient type default to `'additive'`
- `apps/recipes/urls.py` — add `clone/` URL

**Deleted files:**
- `app/` — entire directory (FastAPI v1 artifacts)
- `apps/calculators/utils.py` — dead code
- `static/js/batch_image_preview.js` — unused

---

## Task 1: Testing Infrastructure

**Files:**
- Create: `pytest.ini`
- Create: `skal/test_settings.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: `requirements.txt`

- [ ] **Add pytest-django to requirements.txt**

Replace the file contents:
```
Django==5.2.3
psycopg2-binary==2.9.10
gunicorn==23.0.0
Pillow==11.1.0
reportlab==4.2.5
whitenoise==6.8.0
pytest==8.3.5
pytest-django==4.9.0
```

- [ ] **Create `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = skal.test_settings
python_files = tests/**/test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Create `skal/test_settings.py`**

```python
from skal.settings import *

SECRET_KEY = 'test-secret-key-only-for-testing'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Faster password hashing in tests
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

MEDIA_ROOT = '/tmp/skal_test_media/'
```

- [ ] **Create `tests/__init__.py`** (empty file)

- [ ] **Create `tests/conftest.py`**

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testbrewer',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Brewer',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otherbrewer',
        email='other@example.com',
        password='testpass123',
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username='testbrewer', password='testpass123')
    return client
```

- [ ] **Create `tests/apps/__init__.py`**, `tests/apps/batches/__init__.py`, `tests/apps/recipes/__init__.py`, `tests/apps/accounts/__init__.py` (all empty)

- [ ] **Install the new dependencies**

```bash
pip install pytest==8.3.5 pytest-django==4.9.0
```

- [ ] **Verify pytest discovers tests (zero tests, should exit 0 with "no tests ran")**

```bash
pytest --co -q 2>&1 | head -5
```
Expected output: `no tests ran` or similar (not an error)

- [ ] **Commit**

```bash
git add pytest.ini skal/test_settings.py requirements.txt tests/
git commit -m "test: add pytest + pytest-django testing infrastructure"
```

---

## Task 2: Dead Code Removal

**Files:**
- Delete: `app/` (entire directory)
- Delete: `apps/calculators/utils.py`
- Delete: `static/js/batch_image_preview.js`

- [ ] **Delete the v1 FastAPI directory**

```bash
rm -rf app/
```

- [ ] **Delete unused calculator utility module**

```bash
rm apps/calculators/utils.py
```

- [ ] **Delete unused image preview JS**

```bash
rm static/js/batch_image_preview.js
```

- [ ] **Verify nothing imports from these locations**

```bash
grep -r "from app\." . --include="*.py" | grep -v ".git"
grep -r "calculators.utils" . --include="*.py" | grep -v ".git"
grep -r "batch_image_preview" . --include="*.html" | grep -v ".git"
```
Expected: no output from any of the three commands

- [ ] **Commit**

```bash
git add -A
git commit -m "chore: remove dead v1 FastAPI code and unused files"
```

---

## Task 3: Register Yeast App Properly

**Files:**
- Create: `apps/yeast/__init__.py`
- Create: `apps/yeast/apps.py`
- Modify: `skal/settings.py`

- [ ] **Create `apps/yeast/__init__.py`** (empty)

- [ ] **Create `apps/yeast/apps.py`**

```python
from django.apps import AppConfig


class YeastConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.yeast'
    label = 'yeast'
```

- [ ] **Update `skal/settings.py` INSTALLED_APPS** — remove `crispy_forms`, add `apps.yeast`

Find the `INSTALLED_APPS` list and replace it with:
```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.recipes",
    "apps.batches",
    "apps.calculators",
    "apps.yeast",
]
```

- [ ] **Remove `CRISPY_TEMPLATE_PACK` setting from `skal/settings.py`**

Delete this line:
```python
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

- [ ] **Verify Django starts cleanly**

```bash
python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

- [ ] **Commit**

```bash
git add apps/yeast/__init__.py apps/yeast/apps.py skal/settings.py
git commit -m "chore: register yeast app, remove unused crispy_forms"
```

---

## Task 4: Fix BUG-3 — ProfileUpdateView Wrong Model

**Files:**
- Modify: `apps/accounts/views.py`
- Create: `tests/apps/accounts/test_views.py`

- [ ] **Write the failing test**

Create `tests/apps/accounts/test_views.py`:
```python
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestProfileUpdateView:
    def test_profile_page_loads(self, auth_client):
        response = auth_client.get(reverse('accounts:profile'))
        assert response.status_code == 200

    def test_profile_update_saves_theme(self, auth_client, user):
        response = auth_client.post(reverse('accounts:profile'), {
            'first_name': 'Dayton',
            'last_name': 'Jones',
            'email': 'test@example.com',
            'theme': 'dark',
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.theme == 'dark'

    def test_profile_update_saves_name(self, auth_client, user):
        response = auth_client.post(reverse('accounts:profile'), {
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'email': 'test@example.com',
            'theme': 'light',
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == 'NewFirst'
```

- [ ] **Run test to verify it fails (or passes — either way, document current state)**

```bash
pytest tests/apps/accounts/test_views.py -v
```

- [ ] **Fix `ProfileUpdateView` in `apps/accounts/views.py`**

Change the class definition from:
```python
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = settings.AUTH_USER_MODEL
    form_class = ProfileForm
```
To:
```python
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
```

Add the import at the top of the imports from `.forms`:
```python
from .models import User
```

- [ ] **Run tests to confirm pass**

```bash
pytest tests/apps/accounts/test_views.py -v
```
Expected: 3 passed

- [ ] **Commit**

```bash
git add apps/accounts/views.py tests/apps/accounts/test_views.py
git commit -m "fix: ProfileUpdateView model attribute was a string not a class"
```

---

## Task 5: Fix BUG-2 — Checklist AJAX Security

**Files:**
- Modify: `apps/batches/views.py`
- Create: `tests/apps/batches/test_views.py`

- [ ] **Write the failing security test**

Create `tests/apps/batches/test_views.py`:
```python
import pytest
from django.urls import reverse
from apps.batches.models import Batch
import datetime


@pytest.fixture
def batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Test Batch',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date.today(),
    )


@pytest.mark.django_db
class TestUpdateChecklistItem:
    def test_valid_field_toggles(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'create_must_done', 'value': 'true'},
        )
        assert response.status_code == 200
        batch.refresh_from_db()
        assert batch.create_must_done is True

    def test_invalid_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'user_id', 'value': '999'},
        )
        assert response.status_code == 400

    def test_arbitrary_model_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'og', 'value': '1.000'},
        )
        assert response.status_code == 400

    def test_other_user_cannot_update(self, client, other_user, batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'create_must_done', 'value': 'true'},
        )
        assert response.status_code == 404
```

- [ ] **Run tests to confirm they fail (the security tests should currently fail)**

```bash
pytest tests/apps/batches/test_views.py::TestUpdateChecklistItem -v
```
Expected: `test_invalid_field_rejected` and `test_arbitrary_model_field_rejected` FAIL

- [ ] **Fix `update_checklist_item` in `apps/batches/views.py`**

Replace the function body:
```python
ALLOWED_CHECKLIST_FIELDS = {
    'create_must_done', 'pitch_yeast_done', 'fo_24h_done',
    'fo_48h_done', 'fo_72h_done', 'fo_1_3_break_done',
    'rack_secondary_done', 'bottled_done',
}


@login_required
def update_checklist_item(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    field = request.POST.get("field")
    value = request.POST.get("value") == "true"

    if field not in ALLOWED_CHECKLIST_FIELDS:
        return JsonResponse({"success": False, "error": "Invalid field"}, status=400)

    setattr(batch, field, value)

    date_value = None
    if field.endswith("_done"):
        date_field = field.replace("_done", "_date")
        if value:
            date_value = date.today()
            setattr(batch, date_field, date_value)
        else:
            setattr(batch, date_field, None)

    batch.save()
    return JsonResponse({
        "success": True,
        "field": field,
        "value": value,
        "date": str(date_value) if date_value else "",
    })
```

- [ ] **Run tests to confirm all pass**

```bash
pytest tests/apps/batches/test_views.py::TestUpdateChecklistItem -v
```
Expected: 4 passed

- [ ] **Commit**

```bash
git add apps/batches/views.py tests/apps/batches/test_views.py
git commit -m "fix: whitelist checklist fields to prevent arbitrary model field writes"
```

---

## Task 6: Fix BUG-4 — RecipeIngredientForm Wrong Ingredient Type

**Files:**
- Modify: `apps/recipes/forms.py`
- Create: `tests/apps/recipes/test_views.py`

- [ ] **Write the failing test**

Create `tests/apps/recipes/test_views.py`:
```python
import pytest
from django.urls import reverse
from apps.recipes.models import Ingredient, Recipe


@pytest.mark.django_db
class TestRecipeIngredientType:
    def test_extra_ingredient_created_as_additive(self, auth_client):
        """Ingredients added via the extra formset should be typed 'additive', not 'honey'."""
        response = auth_client.post(reverse('recipes:create'), {
            'name': 'Test Recipe',
            'batch_size': '1.0',
            'instructions': 'Test instructions',
            'honey': 'Wildflower Honey',
            'honey_quantity': '3.0',
            'water': 'Filtered Water',
            'water_quantity': '1.0',
            'yeast': 'Lalvin EC-1118',
            'yeast_quantity': '1 packet',
            'is_public': '',
            # Extra formset ingredient
            'recipeingredient_set-TOTAL_FORMS': '1',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000',
            'recipeingredient_set-0-ingredient_name': 'Pectic Enzyme',
            'recipeingredient_set-0-quantity': '1/2 tsp',
            'recipeingredient_set-0-DELETE': '',
        })
        assert response.status_code == 302
        ingredient = Ingredient.objects.get(name='Pectic Enzyme')
        assert ingredient.type == 'additive', (
            f"Expected 'additive', got '{ingredient.type}'"
        )
```

- [ ] **Run test to confirm it fails**

```bash
pytest tests/apps/recipes/test_views.py::TestRecipeIngredientType -v
```
Expected: FAIL — ingredient type will be `'honey'`

- [ ] **Fix `RecipeIngredientForm.save()` in `apps/recipes/forms.py`**

Change the save method:
```python
def save(self, commit=True):
    name = self.cleaned_data.get('ingredient_name')
    ingredient, _ = Ingredient.objects.get_or_create(
        name=name,
        defaults={'type': Ingredient.TYPE_ADDITIVE}
    )
    self.instance.ingredient = ingredient
    return super().save(commit=commit)
```

- [ ] **Run test to confirm it passes**

```bash
pytest tests/apps/recipes/test_views.py::TestRecipeIngredientType -v
```
Expected: 1 passed

- [ ] **Commit**

```bash
git add apps/recipes/forms.py tests/apps/recipes/test_views.py
git commit -m "fix: extra formset ingredients default to 'additive' type not 'honey'"
```

---

## Task 7: Fix BUG-1 — Recipe Edit Doesn't Update Primary Ingredients

**Files:**
- Modify: `apps/recipes/views.py`
- Modify: `tests/apps/recipes/test_views.py`

- [ ] **Write the failing test** (add to `tests/apps/recipes/test_views.py`)

```python
import datetime
from apps.recipes.models import Recipe, RecipeIngredient, Ingredient


@pytest.fixture
def recipe_with_ingredients(db, user):
    recipe = Recipe.objects.create(
        user=user, name='Original Mead', batch_size='5.0',
        instructions='Original instructions',
    )
    honey, _ = Ingredient.objects.get_or_create(name='Wildflower Honey', defaults={'type': 'honey'})
    water, _ = Ingredient.objects.get_or_create(name='Water', defaults={'type': 'additive'})
    yeast, _ = Ingredient.objects.get_or_create(name='Lalvin EC-1118', defaults={'type': 'yeast'})
    RecipeIngredient.objects.create(recipe=recipe, ingredient=honey, quantity='15.0 lbs', order=0)
    RecipeIngredient.objects.create(recipe=recipe, ingredient=water, quantity='5.0 gal', order=1)
    RecipeIngredient.objects.create(recipe=recipe, ingredient=yeast, quantity='2 packets', order=2)
    return recipe


@pytest.mark.django_db
class TestRecipeUpdatePrimaryIngredients:
    def test_editing_honey_quantity_saves(self, auth_client, recipe_with_ingredients):
        recipe = recipe_with_ingredients
        auth_client.post(reverse('recipes:edit', kwargs={'pk': recipe.pk}), {
            'name': 'Original Mead',
            'batch_size': '5.0',
            'instructions': 'Updated instructions',
            'honey': 'Wildflower Honey',
            'honey_quantity': '18.0',   # changed from 15
            'water': 'Water',
            'water_quantity': '5.0',
            'yeast': 'Lalvin EC-1118',
            'yeast_quantity': '2 packets',
            'is_public': '',
            'recipeingredient_set-TOTAL_FORMS': '0',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000',
        })
        ri = RecipeIngredient.objects.get(recipe=recipe, order=0)
        assert ri.quantity == '18.0 lbs', f"Expected '18.0 lbs', got '{ri.quantity}'"

    def test_editing_yeast_saves(self, auth_client, recipe_with_ingredients):
        recipe = recipe_with_ingredients
        auth_client.post(reverse('recipes:edit', kwargs={'pk': recipe.pk}), {
            'name': 'Original Mead',
            'batch_size': '5.0',
            'instructions': 'Updated instructions',
            'honey': 'Wildflower Honey',
            'honey_quantity': '15.0',
            'water': 'Water',
            'water_quantity': '5.0',
            'yeast': 'Lalvin 71-B',    # changed yeast
            'yeast_quantity': '1 packet',
            'is_public': '',
            'recipeingredient_set-TOTAL_FORMS': '0',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000',
        })
        ri = RecipeIngredient.objects.get(recipe=recipe, order=2)
        assert ri.ingredient.name == 'Lalvin 71-B'
        assert ri.quantity == '1 packet'
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/recipes/test_views.py::TestRecipeUpdatePrimaryIngredients -v
```
Expected: both tests FAIL

- [ ] **Fix `RecipeUpdateView.post()` in `apps/recipes/views.py`**

Replace the `post` method:
```python
def post(self, request, *args, **kwargs):
    form = self.get_form()
    formset = RecipeIngredientFormSet(request.POST, instance=self.object)
    if form.is_valid() and formset.is_valid():
        self.object = form.save()
        self._update_primary_ingredients(form)
        formset.instance = self.object
        formset.save()
        return HttpResponseRedirect(self.get_success_url())
    return self.render_to_response(
        self.get_context_data(form=form, ingredient_formset=formset)
    )

def _update_primary_ingredients(self, form):
    cd = form.cleaned_data

    honey_obj, _ = Ingredient.objects.get_or_create(
        name=cd['honey'], defaults={'type': Ingredient.TYPE_HONEY}
    )
    RecipeIngredient.objects.update_or_create(
        recipe=self.object, order=0,
        defaults={'ingredient': honey_obj, 'quantity': f"{cd['honey_quantity']} lbs"}
    )

    water_obj, _ = Ingredient.objects.get_or_create(
        name=cd['water'], defaults={'type': Ingredient.TYPE_ADDITIVE}
    )
    RecipeIngredient.objects.update_or_create(
        recipe=self.object, order=1,
        defaults={'ingredient': water_obj, 'quantity': f"{cd['water_quantity']} gal"}
    )

    yeast_obj, _ = Ingredient.objects.get_or_create(
        name=cd['yeast'], defaults={'type': Ingredient.TYPE_YEAST}
    )
    RecipeIngredient.objects.update_or_create(
        recipe=self.object, order=2,
        defaults={'ingredient': yeast_obj, 'quantity': cd['yeast_quantity']}
    )
```

- [ ] **Run tests to confirm they pass**

```bash
pytest tests/apps/recipes/test_views.py::TestRecipeUpdatePrimaryIngredients -v
```
Expected: 2 passed

- [ ] **Commit**

```bash
git add apps/recipes/views.py tests/apps/recipes/test_views.py
git commit -m "fix: recipe edit now updates honey/water/yeast primary ingredients"
```

---

## Task 8: Remove `gravatar_url` Field + Add Checklist Note Fields

**Files:**
- Modify: `apps/accounts/models.py`
- Create: `apps/accounts/migrations/0003_remove_user_gravatar_url.py`
- Modify: `apps/batches/models.py`
- Create: `apps/batches/migrations/0004_batch_checklist_notes.py`
- Create: `tests/apps/batches/test_models.py`

- [ ] **Write model tests first**

Create `tests/apps/batches/test_models.py`:
```python
import pytest
import datetime
from apps.batches.models import Batch


@pytest.fixture
def batch(db, user):
    return Batch.objects.create(
        user=user, name='Test', batch_size='5.0',
        og='1.100', primary_date=datetime.date.today(),
    )


@pytest.mark.django_db
class TestBatchStageProperty:
    def test_planned_stage(self, batch):
        assert batch.stage == 'planned'

    def test_active_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.save()
        assert batch.stage == 'active'

    def test_secondary_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.rack_secondary_done = True
        batch.save()
        assert batch.stage == 'secondary'

    def test_bottled_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.rack_secondary_done = True
        batch.bottled_done = True
        batch.save()
        assert batch.stage == 'bottled'


@pytest.mark.django_db
class TestBatchChecklistProgress:
    def test_zero_progress(self, batch):
        assert batch.checklist_progress == 0

    def test_partial_progress(self, batch):
        batch.create_must_done = True
        batch.pitch_yeast_done = True
        batch.save()
        assert batch.checklist_progress == 25  # 2/8 * 100

    def test_full_progress(self, batch):
        batch.create_must_done = True
        batch.pitch_yeast_done = True
        batch.fo_24h_done = True
        batch.fo_48h_done = True
        batch.fo_72h_done = True
        batch.fo_1_3_break_done = True
        batch.rack_secondary_done = True
        batch.bottled_done = True
        batch.save()
        assert batch.checklist_progress == 100


@pytest.mark.django_db
class TestChecklistNoteFields:
    def test_note_fields_exist_and_default_empty(self, batch):
        assert batch.create_must_note == ''
        assert batch.pitch_yeast_note == ''
        assert batch.bottled_note == ''

    def test_note_can_be_saved(self, batch):
        batch.fo_24h_note = 'Added 2g Fermaid-O'
        batch.save()
        batch.refresh_from_db()
        assert batch.fo_24h_note == 'Added 2g Fermaid-O'
```

- [ ] **Run tests to confirm they fail (fields don't exist yet)**

```bash
pytest tests/apps/batches/test_models.py -v
```
Expected: multiple failures — `stage`, `checklist_progress`, and note fields don't exist yet

- [ ] **Remove `gravatar_url` from `apps/accounts/models.py`**

Change `User` class — remove this field entirely:
```python
gravatar_url = models.URLField("Gravatar URL", blank=True, null=True)
```

The model should now be:
```python
class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    theme = models.CharField(
        max_length=20,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
    )

    def __str__(self):
        return self.username
```

- [ ] **Add stage property, checklist_progress property, and note fields to `apps/batches/models.py`**

Add after the `bottled_done`/`bottled_date` block and before the `Meta` class:
```python
    # --- Checklist notes ---
    create_must_note    = models.TextField(blank=True, default='')
    pitch_yeast_note    = models.TextField(blank=True, default='')
    fo_24h_note         = models.TextField(blank=True, default='')
    fo_48h_note         = models.TextField(blank=True, default='')
    fo_72h_note         = models.TextField(blank=True, default='')
    fo_1_3_break_note   = models.TextField(blank=True, default='')
    rack_secondary_note = models.TextField(blank=True, default='')
    bottled_note        = models.TextField(blank=True, default='')
    # -------------------------
```

Add these two properties after the `save()` method and before `__str__`:
```python
    @property
    def stage(self):
        if self.bottled_done:
            return 'bottled'
        if self.rack_secondary_done:
            return 'secondary'
        if self.pitch_yeast_done:
            return 'active'
        return 'planned'

    @property
    def checklist_progress(self):
        done = [
            self.create_must_done, self.pitch_yeast_done,
            self.fo_24h_done, self.fo_48h_done, self.fo_72h_done,
            self.fo_1_3_break_done, self.rack_secondary_done, self.bottled_done,
        ]
        return int((sum(done) / 8) * 100)
```

- [ ] **Generate migrations**

```bash
python manage.py makemigrations accounts --name remove_user_gravatar_url
python manage.py makemigrations batches --name batch_checklist_notes
```

- [ ] **Apply migrations**

```bash
python manage.py migrate
```
Expected: applies both migrations successfully

- [ ] **Run model tests to confirm they pass**

```bash
pytest tests/apps/batches/test_models.py -v
```
Expected: all tests pass

- [ ] **Commit**

```bash
git add apps/accounts/models.py apps/batches/models.py \
    apps/accounts/migrations/0003_remove_user_gravatar_url.py \
    apps/batches/migrations/0004_batch_checklist_notes.py \
    tests/apps/batches/test_models.py
git commit -m "feat: add checklist note fields, stage property, remove unused gravatar_url field"
```

---

## Task 9: Clone Recipe Endpoint

**Files:**
- Modify: `apps/recipes/views.py`
- Modify: `apps/recipes/urls.py`
- Modify: `tests/apps/recipes/test_views.py`

- [ ] **Write the failing tests** (add to `tests/apps/recipes/test_views.py`)

```python
@pytest.mark.django_db
class TestCloneRecipe:
    def test_clone_creates_new_recipe(self, auth_client, recipe_with_ingredients):
        recipe = recipe_with_ingredients
        response = auth_client.post(reverse('recipes:clone', kwargs={'pk': recipe.pk}))
        assert response.status_code == 302
        cloned = Recipe.objects.get(name='Copy of Original Mead')
        assert cloned.user.username == 'testbrewer'
        assert cloned.batch_size == recipe.batch_size
        assert cloned.instructions == recipe.instructions
        assert cloned.is_public is False

    def test_clone_copies_ingredients(self, auth_client, recipe_with_ingredients):
        recipe = recipe_with_ingredients
        auth_client.post(reverse('recipes:clone', kwargs={'pk': recipe.pk}))
        cloned = Recipe.objects.get(name='Copy of Original Mead')
        original_count = recipe.recipeingredient_set.count()
        cloned_count = cloned.recipeingredient_set.count()
        assert cloned_count == original_count

    def test_clone_redirects_to_edit(self, auth_client, recipe_with_ingredients):
        response = auth_client.post(
            reverse('recipes:clone', kwargs={'pk': recipe_with_ingredients.pk})
        )
        cloned = Recipe.objects.get(name='Copy of Original Mead')
        assert response['Location'] == reverse('recipes:edit', kwargs={'pk': cloned.pk})

    def test_cannot_clone_private_recipe_of_other_user(
        self, client, other_user, recipe_with_ingredients
    ):
        recipe_with_ingredients.is_public = False
        recipe_with_ingredients.save()
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('recipes:clone', kwargs={'pk': recipe_with_ingredients.pk})
        )
        assert response.status_code == 404
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/recipes/test_views.py::TestCloneRecipe -v
```
Expected: 4 failures — URL doesn't exist yet

- [ ] **Add `clone_recipe` view to `apps/recipes/views.py`**

Add these imports at the top:
```python
from django.contrib import messages
from django.http import Http404
```

Add the function after `toggle_visibility`:
```python
@login_required
def clone_recipe(request, pk):
    if request.method != 'POST':
        return redirect('recipes:index')

    original = get_object_or_404(Recipe, pk=pk)

    # Only allow cloning own recipes or public/seeded ones
    if (original.user != request.user
            and not original.is_public
            and original.user is not None):
        raise Http404

    new_recipe = Recipe.objects.create(
        user=request.user,
        name=f'Copy of {original.name}',
        batch_size=original.batch_size,
        instructions=original.instructions,
        is_public=False,
    )
    for ri in original.recipeingredient_set.order_by('order'):
        RecipeIngredient.objects.create(
            recipe=new_recipe,
            ingredient=ri.ingredient,
            quantity=ri.quantity,
            order=ri.order,
        )
    messages.success(request, f'Recipe cloned as "{new_recipe.name}".')
    return redirect('recipes:edit', pk=new_recipe.pk)
```

- [ ] **Add URL to `apps/recipes/urls.py`**

```python
from .views import (
    RecipeListView,
    RecipeDetailView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
    toggle_visibility,
    clone_recipe,
)

app_name = 'recipes'

urlpatterns = [
    path('<int:pk>/toggle/', toggle_visibility, name='toggle_visibility'),
    path('<int:pk>/clone/', clone_recipe, name='clone'),

    path('',                   RecipeListView.as_view(),   name='index'),
    path('new/',               RecipeCreateView.as_view(), name='create'),
    path('<int:pk>/',          RecipeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/',     RecipeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/',   RecipeDeleteView.as_view(), name='delete'),
]
```

- [ ] **Run tests to confirm they pass**

```bash
pytest tests/apps/recipes/test_views.py::TestCloneRecipe -v
```
Expected: 4 passed

- [ ] **Commit**

```bash
git add apps/recipes/views.py apps/recipes/urls.py tests/apps/recipes/test_views.py
git commit -m "feat: add clone recipe endpoint"
```

---

## Task 10: Start Batch from Recipe

**Files:**
- Modify: `apps/batches/views.py`
- Modify: `tests/apps/batches/test_views.py`

- [ ] **Write the failing test** (add to `tests/apps/batches/test_views.py`)

```python
from apps.recipes.models import Recipe, Ingredient, RecipeIngredient
import datetime


@pytest.fixture
def public_recipe(db, user):
    return Recipe.objects.create(
        user=user, name='Cherry Vanilla', batch_size='5.0',
        instructions='Test', is_public=True,
    )


@pytest.mark.django_db
class TestStartBatchFromRecipe:
    def test_new_batch_form_prepopulates_recipe(self, auth_client, public_recipe):
        response = auth_client.get(
            reverse('batches:create') + f'?recipe={public_recipe.pk}'
        )
        assert response.status_code == 200
        # The form's initial value for recipe should be set
        form = response.context['form']
        assert form.initial.get('recipe') == public_recipe

    def test_new_batch_form_prepopulates_name(self, auth_client, public_recipe):
        response = auth_client.get(
            reverse('batches:create') + f'?recipe={public_recipe.pk}'
        )
        form = response.context['form']
        assert form.initial.get('name') == 'Cherry Vanilla'

    def test_invalid_recipe_pk_is_ignored(self, auth_client):
        response = auth_client.get(
            reverse('batches:create') + '?recipe=99999'
        )
        assert response.status_code == 200  # no 404, just ignored
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/batches/test_views.py::TestStartBatchFromRecipe -v
```
Expected: failures — `get_initial` not overridden yet

- [ ] **Add `get_initial` to `BatchCreateView` in `apps/batches/views.py`**

Add this import at the top:
```python
from apps.recipes.models import Recipe
```

Add `get_initial` to `BatchCreateView`:
```python
class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'batches/form.html'
    success_url = reverse_lazy('batches:index')

    def get_initial(self):
        initial = super().get_initial()
        recipe_pk = self.request.GET.get('recipe')
        if recipe_pk:
            try:
                recipe = Recipe.objects.get(pk=recipe_pk)
                initial['recipe'] = recipe
                initial['name'] = recipe.name
            except Recipe.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        for i, img in enumerate(self.request.FILES.getlist('images')):
            caption = self.request.POST.get(f'caption_{i}', '')
            BatchImage.objects.create(batch=self.object, image=img, caption=caption)
        return response
```

- [ ] **Run tests to confirm they pass**

```bash
pytest tests/apps/batches/test_views.py::TestStartBatchFromRecipe -v
```
Expected: 3 passed

- [ ] **Commit**

```bash
git add apps/batches/views.py tests/apps/batches/test_views.py
git commit -m "feat: pre-populate new batch form from recipe via ?recipe= query param"
```

---

## Task 11: Checklist Note AJAX Endpoint

**Files:**
- Modify: `apps/batches/views.py`
- Modify: `apps/batches/urls.py`
- Modify: `tests/apps/batches/test_views.py`

- [ ] **Write the failing tests** (add to `tests/apps/batches/test_views.py`)

```python
@pytest.mark.django_db
class TestUpdateChecklistNote:
    def test_save_note_for_valid_field(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': 'Added 2g Fermaid-O'},
        )
        assert response.status_code == 204
        batch.refresh_from_db()
        assert batch.fo_24h_note == 'Added 2g Fermaid-O'

    def test_invalid_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'name', 'note': 'hacked'},
        )
        assert response.status_code == 400

    def test_other_user_cannot_update_note(self, client, other_user, batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': 'nope'},
        )
        assert response.status_code == 404

    def test_blank_note_clears_existing(self, auth_client, batch):
        batch.fo_24h_note = 'Old note'
        batch.save()
        auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': ''},
        )
        batch.refresh_from_db()
        assert batch.fo_24h_note == ''
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/batches/test_views.py::TestUpdateChecklistNote -v
```
Expected: 4 failures

- [ ] **Add `update_checklist_note` view to `apps/batches/views.py`**

Add the constant near `ALLOWED_CHECKLIST_FIELDS`:
```python
ALLOWED_NOTE_FIELDS = {
    'create_must_note', 'pitch_yeast_note', 'fo_24h_note',
    'fo_48h_note', 'fo_72h_note', 'fo_1_3_break_note',
    'rack_secondary_note', 'bottled_note',
}
```

Add the view function:
```python
@login_required
def update_checklist_note(request, pk):
    if request.method != 'POST':
        return HttpResponse(status=405)
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    field = request.POST.get('field', '')
    if field not in ALLOWED_NOTE_FIELDS:
        return HttpResponse(status=400)
    note = request.POST.get('note', '')
    setattr(batch, field, note)
    batch.save(update_fields=[field])
    return HttpResponse(status=204)
```

- [ ] **Add URL to `apps/batches/urls.py`**

```python
from .views import (
    BatchListView, BatchDetailView, BatchCreateView,
    BatchUpdateView, BatchDeleteView,
    toggle_visibility, update_checklist_item, update_checklist_note,
)

app_name = "batches"

urlpatterns = [
    path('<int:pk>/toggle/',           toggle_visibility,     name='toggle_visibility'),
    path('<int:pk>/update-checklist/', update_checklist_item, name='update_checklist'),
    path('<int:pk>/checklist-note/',   update_checklist_note, name='checklist_note'),

    path("",                BatchListView.as_view(),   name="index"),
    path("new/",            BatchCreateView.as_view(), name="create"),
    path("<int:pk>/",       BatchDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",  BatchUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/",BatchDeleteView.as_view(), name="delete"),
]
```

- [ ] **Run tests to confirm they pass**

```bash
pytest tests/apps/batches/test_views.py::TestUpdateChecklistNote -v
```
Expected: 4 passed

- [ ] **Commit**

```bash
git add apps/batches/views.py apps/batches/urls.py tests/apps/batches/test_views.py
git commit -m "feat: add checklist note save endpoint for inline step annotations"
```

---

## Task 12: HTMX-Compatible Batch and Recipe List Views

**Files:**
- Modify: `apps/batches/views.py`
- Modify: `apps/recipes/views.py`
- Create: `templates/batches/partials/batch_rows.html`
- Create: `templates/recipes/partials/recipe_rows.html`
- Modify: `tests/apps/batches/test_views.py`
- Modify: `tests/apps/recipes/test_views.py`

- [ ] **Create the partials directories and placeholder templates**

```bash
mkdir -p templates/batches/partials templates/recipes/partials
```

Create `templates/batches/partials/batch_rows.html`:
```html
{% for batch in batches %}
<div class="batch-row" data-stage="{{ batch.stage }}">
  <span>{{ batch.name }}</span>
  <span>{{ batch.stage }}</span>
  <span>{{ batch.checklist_progress }}%</span>
</div>
{% empty %}
<p>No batches found.</p>
{% endfor %}
```

Create `templates/recipes/partials/recipe_rows.html`:
```html
{% for recipe in recipes %}
<div class="recipe-row">
  <span>{{ recipe.name }}</span>
  <span>{{ recipe.batch_size }} gal</span>
</div>
{% empty %}
<p>No recipes found.</p>
{% endfor %}
```

- [ ] **Write HTMX partial tests** (add to `tests/apps/batches/test_views.py`)

```python
@pytest.mark.django_db
class TestBatchListHTMX:
    def test_htmx_request_returns_partial(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index'),
            HTTP_HX_REQUEST='true',
        )
        assert response.status_code == 200
        # Should use partial template (no full page nav)
        assert b'batch-row' in response.content

    def test_search_filters_by_name(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index') + '?q=Test',
            HTTP_HX_REQUEST='true',
        )
        assert response.status_code == 200
        assert b'Test Batch' in response.content

    def test_search_no_results(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index') + '?q=nonexistent',
            HTTP_HX_REQUEST='true',
        )
        assert b'No batches found' in response.content

    def test_stage_filter_active(self, auth_client, batch):
        batch.pitch_yeast_done = True
        batch.save()
        response = auth_client.get(
            reverse('batches:index') + '?stage=active',
            HTTP_HX_REQUEST='true',
        )
        assert b'Test Batch' in response.content

    def test_stage_filter_excludes_wrong_stage(self, auth_client, batch):
        # batch is 'planned', filter for 'bottled' should exclude it
        response = auth_client.get(
            reverse('batches:index') + '?stage=bottled',
            HTTP_HX_REQUEST='true',
        )
        assert b'Test Batch' not in response.content
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/batches/test_views.py::TestBatchListHTMX -v
```

- [ ] **Update `BatchListView` in `apps/batches/views.py`**

Replace the entire `BatchListView`:
```python
class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'batches/index.html'
    context_object_name = 'batches'

    def get_queryset(self):
        user = self.request.user
        qs = Batch.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).order_by('-primary_date')

        q = self.request.GET.get('q', '').strip()
        stage = self.request.GET.get('stage', '').strip()

        if q:
            qs = qs.filter(name__icontains=q)

        if stage == 'bottled':
            qs = qs.filter(bottled_done=True)
        elif stage == 'secondary':
            qs = qs.filter(rack_secondary_done=True, bottled_done=False)
        elif stage == 'active':
            qs = qs.filter(pitch_yeast_done=True, bottled_done=False,
                           rack_secondary_done=False)
        elif stage == 'planned':
            qs = qs.filter(pitch_yeast_done=False, bottled_done=False)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['stage'] = self.request.GET.get('stage', '')
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'batches/partials/batch_rows.html', context)
        return super().render_to_response(context, **response_kwargs)
```

Add `render` to imports at top of `apps/batches/views.py`:
```python
from django.shortcuts import get_object_or_404, redirect, render
```

- [ ] **Update `RecipeListView` in `apps/recipes/views.py`** similarly:

```python
class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/index.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        user = self.request.user
        qs = Recipe.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(user__isnull=True)
        ).distinct()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = ctx.get('recipes') or self.get_queryset()
        ctx['featured'] = random.choice(list(items)) if items else None
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'recipes/partials/recipe_rows.html', context)
        return super().render_to_response(context, **response_kwargs)
```

Add `render` to imports in `apps/recipes/views.py`:
```python
from django.shortcuts import get_object_or_404, redirect, render
```

- [ ] **Run all batch + recipe tests**

```bash
pytest tests/apps/batches/ tests/apps/recipes/ -v
```
Expected: all passing

- [ ] **Commit**

```bash
git add apps/batches/views.py apps/recipes/views.py \
    templates/batches/partials/ templates/recipes/partials/ \
    tests/apps/batches/test_views.py tests/apps/recipes/test_views.py
git commit -m "feat: HTMX partial responses for batch/recipe list with search and stage filter"
```

---

## Task 13: Dashboard Context + HomeView Stats

**Files:**
- Modify: `apps/accounts/views.py`
- Modify: `tests/apps/accounts/test_views.py`

- [ ] **Write dashboard context tests** (add to `tests/apps/accounts/test_views.py`)

```python
import datetime
from apps.batches.models import Batch
from apps.recipes.models import Recipe


@pytest.fixture
def user_with_data(db, user):
    """User with 2 batches (1 active, 1 bottled) and 1 recipe."""
    recipe = Recipe.objects.create(
        user=user, name='Test Recipe', batch_size='5.0',
        instructions='Test', is_public=False,
    )
    b1 = Batch.objects.create(
        user=user, name='Active Batch', batch_size='5.0',
        og='1.100', primary_date=datetime.date.today(),
        pitch_yeast_done=True,
    )
    b2 = Batch.objects.create(
        user=user, name='Bottled Batch', batch_size='5.0',
        og='1.110', fg='1.002', primary_date=datetime.date(2024, 8, 1),
        pitch_yeast_done=True, rack_secondary_done=True, bottled_done=True,
    )
    return user, recipe, b1, b2


@pytest.mark.django_db
class TestHomeViewContext:
    def test_home_requires_login(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_home_loads_for_authenticated(self, auth_client):
        response = auth_client.get(reverse('home'))
        assert response.status_code == 200

    def test_context_has_stats(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        ctx = response.context
        assert ctx['total_batches'] == 2
        assert ctx['active_count'] == 1
        assert ctx['total_recipes'] == 1

    def test_active_batches_excludes_bottled(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        active = list(response.context['active_batches'])
        names = [b.name for b in active]
        assert 'Active Batch' in names
        assert 'Bottled Batch' not in names

    def test_last_bottled_is_correct(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        assert response.context['last_bottled'].name == 'Bottled Batch'
```

- [ ] **Run tests to confirm they fail**

```bash
pytest tests/apps/accounts/test_views.py::TestHomeViewContext -v
```
Expected: failures — context keys don't exist yet

- [ ] **Update `HomeView` in `apps/accounts/views.py`**

Replace `HomeView`:
```python
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        user_batches = Batch.objects.filter(user=user)
        active_batches = user_batches.filter(bottled_done=False).order_by('-primary_date')

        # Average ABV from batches that have both OG and FG
        completed = user_batches.filter(fg__isnull=False)
        avg_abv = None
        if completed.exists():
            total_abv = sum(
                (76.08 * (float(b.og) - float(b.fg)) / (1.775 - float(b.og)))
                * (float(b.fg) / 0.794)
                for b in completed
            )
            avg_abv = round(total_abv / completed.count(), 1)

        ctx['active_batches'] = active_batches
        ctx['total_batches'] = user_batches.count()
        ctx['active_count'] = active_batches.count()
        ctx['avg_abv'] = avg_abv
        ctx['total_recipes'] = Recipe.objects.filter(user=user).count()
        ctx['last_bottled'] = (
            user_batches.filter(bottled_done=True).order_by('-bottled_date').first()
        )
        ctx['recent_images'] = (
            BatchImage.objects.filter(batch__user=user)
            .select_related('batch')
            .order_by('-id')[:10]
        )
        # Keep legacy context keys for any templates that still use them
        ctx['newest_recipe'] = Recipe.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(user__isnull=True)
        ).order_by('-pk').first()
        ctx['newest_batch'] = user_batches.order_by('-pk').first()

        return ctx
```

Add `BatchImage` to the import at the top of `apps/accounts/views.py`:
```python
from apps.batches.models import Batch, BatchImage
```

- [ ] **Run tests to confirm they pass**

```bash
pytest tests/apps/accounts/test_views.py -v
```
Expected: all passing

- [ ] **Run the full test suite to confirm nothing broken**

```bash
pytest -v
```
Expected: all tests pass

- [ ] **Commit**

```bash
git add apps/accounts/views.py tests/apps/accounts/test_views.py
git commit -m "feat: dashboard context — stats, active batches, photo strip, last bottled"
```

---

## Task 14: Django Messages Integration

**Files:**
- Modify: `apps/recipes/views.py`
- Modify: `apps/batches/views.py`
- Modify: `apps/accounts/views.py`
- Modify: `skal/settings.py`

- [ ] **Verify `django.contrib.messages` is already in INSTALLED_APPS and MIDDLEWARE** (it is by default — just confirm)

```bash
grep -n "messages" skal/settings.py
```
Expected: appears in INSTALLED_APPS and MIDDLEWARE

- [ ] **Add `messages` calls to recipe views in `apps/recipes/views.py`**

In `RecipeCreateView._save_and_redirect`, add before the return:
```python
from django.contrib import messages

# In _save_and_redirect, before the return:
messages.success(self.request, f'Recipe "{self.object.name}" created.')
```

In `RecipeUpdateView.post`, after `formset.save()`, before the return:
```python
messages.success(self.request, f'Recipe "{self.object.name}" updated.')
```

In `RecipeDeleteView`, add a `delete` override:
```python
def delete(self, request, *args, **kwargs):
    recipe = self.get_object()
    messages.success(request, f'Recipe "{recipe.name}" deleted.')
    return super().delete(request, *args, **kwargs)
```

In `toggle_visibility`:
```python
def toggle_visibility(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.is_public = not recipe.is_public
    recipe.save()
    state = 'public' if recipe.is_public else 'private'
    messages.success(request, f'"{recipe.name}" is now {state}.')
    return redirect('recipes:detail', pk=pk)
```

- [ ] **Add `messages` calls to batch views in `apps/batches/views.py`**

In `BatchCreateView.form_valid`, add after `response = super().form_valid(form)`:
```python
from django.contrib import messages

messages.success(self.request, f'Batch "{self.object.name}" created.')
```

In `BatchUpdateView.form_valid`, add after `response = super().form_valid(form)`:
```python
messages.success(self.request, f'Batch "{self.object.name}" saved.')
```

In `BatchDeleteView`, add a `delete` override:
```python
def delete(self, request, *args, **kwargs):
    batch = self.get_object()
    messages.success(request, f'Batch "{batch.name}" deleted.')
    return super().delete(request, *args, **kwargs)
```

In `toggle_visibility` for batches:
```python
def toggle_visibility(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    batch.is_public = not batch.is_public
    batch.save()
    state = 'public' if batch.is_public else 'private'
    messages.success(request, f'"{batch.name}" is now {state}.')
    return redirect('batches:detail', pk=pk)
```

- [ ] **Run full test suite to confirm nothing broken**

```bash
pytest -v
```
Expected: all tests pass

- [ ] **Commit**

```bash
git add apps/recipes/views.py apps/batches/views.py apps/accounts/views.py
git commit -m "feat: add Django messages calls throughout for success/error feedback"
```

---

## Final Verification

- [ ] **Run the full test suite one last time**

```bash
pytest -v --tb=short
```
Expected: all tests pass, no warnings about missing imports or migrations

- [ ] **Verify Django system check passes**

```bash
python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

- [ ] **Verify migrations are clean**

```bash
python manage.py migrate --run-syncdb 2>&1
```
Expected: no errors

- [ ] **Final commit if any loose files remain**

```bash
git status
```
If clean: done. If not, commit any remaining tracked changes.
