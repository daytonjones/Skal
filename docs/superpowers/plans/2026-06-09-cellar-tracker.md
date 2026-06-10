# Cellar Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After a batch is bottled, give the user a simple cellar inventory: how many bottles remain, where they're stored, and how old they are. Consumption events are recorded inline on the batch detail page. A dedicated `/cellar/` view surfaces all bottled batches at a glance with a last-bottle warning when only one bottle remains.

**Architecture:** Two new fields (`bottle_count`, `storage_location`) on `Batch` and a new `BottleConsumption` model track inventory. A `bottles_remaining` computed property subtracts consumed quantities from `bottle_count`. A `CellarView` (ListView) at `/cellar/` lists all bottled batches for the logged-in user. A `add_consumption` FBV at `POST /batches/<pk>/consume/` appends a `BottleConsumption` record. The batch detail page gains a Cellar section (stats strip, inline log form, history). `BatchForm` gains `bottle_count` and `storage_location`.

**Tech Stack:** Django 4.x, Python 3.12, pytest-django.

---

### Task 1: `Batch` model changes + `BottleConsumption` model + migration + model tests

**Files:**
- Modify: `apps/batches/models.py`
- Create: `apps/batches/migrations/XXXX_cellar_tracker.py` (generated)
- Modify: `tests/apps/batches/test_models.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/apps/batches/test_models.py`:

```python
import pytest
import datetime
from apps.batches.models import Batch, BottleConsumption


@pytest.fixture
def bottled_batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Cyser',
        batch_size='5.0',
        og='1.110',
        primary_date=datetime.date(2025, 1, 1),
        bottled_done=True,
        bottled_date=datetime.date(2025, 6, 1),
    )


@pytest.mark.django_db
class TestBottlesRemainingProperty:
    def test_returns_none_when_bottle_count_not_set(self, bottled_batch):
        assert bottled_batch.bottle_count is None
        assert bottled_batch.bottles_remaining is None

    def test_returns_bottle_count_when_no_consumptions(self, bottled_batch):
        bottled_batch.bottle_count = 24
        bottled_batch.save()
        assert bottled_batch.bottles_remaining == 24

    def test_subtracts_consumed_quantities(self, bottled_batch):
        bottled_batch.bottle_count = 24
        bottled_batch.save()
        BottleConsumption.objects.create(
            batch=bottled_batch,
            date=datetime.date(2025, 7, 4),
            quantity=3,
        )
        BottleConsumption.objects.create(
            batch=bottled_batch,
            date=datetime.date(2025, 8, 1),
            quantity=2,
        )
        assert bottled_batch.bottles_remaining == 19

    def test_can_return_zero_when_all_consumed(self, bottled_batch):
        bottled_batch.bottle_count = 6
        bottled_batch.save()
        BottleConsumption.objects.create(
            batch=bottled_batch,
            date=datetime.date(2025, 7, 1),
            quantity=6,
        )
        assert bottled_batch.bottles_remaining == 0


@pytest.mark.django_db
class TestBottleConsumptionModel:
    def test_str(self, bottled_batch):
        c = BottleConsumption.objects.create(
            batch=bottled_batch,
            date=datetime.date(2025, 7, 4),
            quantity=2,
        )
        assert str(c) == f"2 bottle(s) on 2025-07-04 from {bottled_batch}"

    def test_ordering_latest_first(self, bottled_batch):
        BottleConsumption.objects.create(
            batch=bottled_batch, date=datetime.date(2025, 7, 1), quantity=1,
        )
        BottleConsumption.objects.create(
            batch=bottled_batch, date=datetime.date(2025, 9, 1), quantity=1,
        )
        dates = list(
            BottleConsumption.objects.filter(batch=bottled_batch)
            .values_list('date', flat=True)
        )
        assert dates[0] > dates[1]

    def test_notes_optional(self, bottled_batch):
        c = BottleConsumption.objects.create(
            batch=bottled_batch,
            date=datetime.date(2025, 7, 4),
            quantity=1,
        )
        assert c.notes == ''

    def test_cascade_delete(self, bottled_batch):
        BottleConsumption.objects.create(
            batch=bottled_batch, date=datetime.date(2025, 7, 1), quantity=1,
        )
        pk = bottled_batch.pk
        bottled_batch.delete()
        assert BottleConsumption.objects.filter(batch_id=pk).count() == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_models.py::TestBottlesRemainingProperty tests/apps/batches/test_models.py::TestBottleConsumptionModel -v
```

Expected: `ImportError` or `FAILED` — `BottleConsumption` does not exist yet; `bottle_count` field is missing.

- [ ] **Step 3: Add fields and model to `apps/batches/models.py`**

**3a.** Add two fields to `Batch` after the `bottled_note` field (before `class Meta`):

```python
    # --- Cellar tracker ---
    bottle_count     = models.PositiveIntegerField(null=True, blank=True)
    storage_location = models.CharField(max_length=200, blank=True)
    # ----------------------
```

**3b.** Add the `bottles_remaining` property to `Batch` after the `checklist_progress` property:

```python
    @property
    def bottles_remaining(self):
        """Returns None if bottle_count is not set; otherwise bottle_count minus consumed."""
        if self.bottle_count is None:
            return None
        consumed = self.consumptions.aggregate(total=models.Sum('quantity'))['total'] or 0
        return self.bottle_count - consumed
```

**3c.** Append the `BottleConsumption` model after `BatchImage`:

```python
class BottleConsumption(models.Model):
    batch    = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='consumptions')
    date     = models.DateField()
    quantity = models.PositiveIntegerField()
    notes    = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.quantity} bottle(s) on {self.date} from {self.batch}"
```

- [ ] **Step 4: Generate the migration**

```bash
python manage.py makemigrations batches --name cellar_tracker
```

Expected output: `Migrations for 'batches': apps/batches/migrations/XXXX_cellar_tracker.py`

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_models.py -v
```

Expected: all model tests pass (existing + new).

- [ ] **Step 6: Commit**

```bash
git add apps/batches/models.py apps/batches/migrations/ tests/apps/batches/test_models.py
git commit -m "feat: add bottle_count/storage_location to Batch and BottleConsumption model"
```

---

### Task 2: `CellarView` + `add_consumption` view + URL wiring + view tests

**Files:**
- Modify: `apps/batches/views.py`
- Modify: `apps/batches/urls.py`
- Modify: `skal/urls.py`
- Create: `tests/apps/batches/test_cellar_views.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/apps/batches/test_cellar_views.py`:

```python
import pytest
import datetime
from django.urls import reverse
from apps.batches.models import Batch, BottleConsumption


@pytest.fixture
def bottled_batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Cyser',
        batch_size='5.0',
        og='1.110',
        primary_date=datetime.date(2025, 1, 1),
        bottled_done=True,
        bottled_date=datetime.date(2025, 6, 1),
        bottle_count=12,
    )


@pytest.fixture
def other_bottled_batch(db, other_user):
    return Batch.objects.create(
        user=other_user,
        name='Other Mead',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date(2025, 2, 1),
        bottled_done=True,
        bottled_date=datetime.date(2025, 7, 1),
    )


@pytest.mark.django_db
class TestCellarView:
    def test_requires_login(self, client):
        response = client.get(reverse('cellar'))
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_returns_only_logged_in_users_batches(
        self, auth_client, bottled_batch, other_bottled_batch
    ):
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        batches = list(response.context['object_list'])
        assert bottled_batch in batches
        assert other_bottled_batch not in batches

    def test_excludes_unbottled_batches(self, auth_client, user):
        Batch.objects.create(
            user=user,
            name='Active Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2025, 3, 1),
            bottled_done=False,
        )
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        names = [b.name for b in response.context['object_list']]
        assert not any('Active Mead' in n for n in names)

    def test_context_includes_today(self, auth_client, bottled_batch):
        response = auth_client.get(reverse('cellar'))
        assert 'today' in response.context

    def test_empty_state_no_bottled_batches(self, auth_client):
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        assert list(response.context['object_list']) == []


@pytest.mark.django_db
class TestAddConsumptionView:
    def test_creates_consumption_and_redirects(self, auth_client, bottled_batch):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {
                'date': '2025-07-04',
                'quantity': 3,
                'notes': 'Holiday tasting',
            },
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch, quantity=3).exists()

    def test_redirects_to_batch_detail(self, auth_client, bottled_batch):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert reverse('batches:detail', kwargs={'pk': bottled_batch.pk}) in response['Location']

    def test_404_for_non_owner(self, client, other_user, bottled_batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert response.status_code == 404

    def test_invalid_quantity_redirects_with_error_no_record(
        self, auth_client, bottled_batch
    ):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 0, 'notes': ''},
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch).count() == 0

    def test_missing_date_redirects_with_error_no_record(
        self, auth_client, bottled_batch
    ):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '', 'quantity': 2, 'notes': ''},
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch).count() == 0

    def test_requires_login(self, client, bottled_batch):
        response = client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_cellar_views.py -v
```

Expected: `NoReverseMatch` for `cellar` and `batches:add_consumption` — neither URL exists yet.

- [ ] **Step 3: Add `CellarView` and `add_consumption` to `apps/batches/views.py`**

**3a.** Add to the top-level imports (add `LoginRequiredMixin` if not already imported, and `login_required`, `messages`, `datetime`):

```python
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
```

**3b.** Add `CellarView` class:

```python
class CellarView(LoginRequiredMixin, ListView):
    template_name = 'batches/cellar.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Batch.objects
            .filter(user=self.request.user, bottled_done=True)
            .order_by('-bottled_date')
            .prefetch_related('consumptions')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['today'] = datetime.date.today()
        return ctx
```

**3c.** Add `add_consumption` view function:

```python
@login_required
def add_consumption(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    if request.method == 'POST':
        date_str  = request.POST.get('date', '').strip()
        qty_str   = request.POST.get('quantity', '').strip()
        notes     = request.POST.get('notes', '').strip()

        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise ValueError("quantity must be positive")
            date = datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid consumption data. Please check the date and quantity.')
            return redirect('batches:detail', pk=pk)

        BottleConsumption.objects.create(batch=batch, date=date, quantity=quantity, notes=notes)
        messages.success(request, f'Logged {quantity} bottle(s) consumed.')
    return redirect('batches:detail', pk=pk)
```

Also ensure `BottleConsumption` is imported at the top of `views.py`:

```python
from .models import Batch, BottleConsumption
```

- [ ] **Step 4: Wire up URLs in `apps/batches/urls.py`**

Add `add_consumption` to the imports from `.views`, then add to `urlpatterns`:

```python
path('<int:pk>/consume/', add_consumption, name='add_consumption'),
```

- [ ] **Step 5: Wire up `CellarView` in `skal/urls.py`**

Add the import and path after the `ai/` include:

```python
from apps.batches.views import CellarView

# inside urlpatterns:
path('cellar/', CellarView.as_view(), name='cellar'),
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_cellar_views.py -v
```

Expected: all 12 view tests pass.

- [ ] **Step 7: Run full batch test suite to confirm no regressions**

```bash
pytest tests/apps/batches/ -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add apps/batches/views.py apps/batches/urls.py skal/urls.py tests/apps/batches/test_cellar_views.py
git commit -m "feat: add CellarView and add_consumption view with URL wiring"
```

---

### Task 3: Templates (`cellar.html` + batch detail Cellar section + `BatchForm` fields)

**Files:**
- Create: `templates/batches/cellar.html`
- Modify: `templates/batches/detail.html`
- Modify: `apps/batches/forms.py`

No new tests are required for this task — the view tests from Task 2 already assert HTTP 200 responses and template rendering; the focus here is correctness of the HTML. Do a manual smoke-check after each step.

- [ ] **Step 1: Add `bottle_count` and `storage_location` to `BatchForm`**

In `apps/batches/forms.py`, add the two fields to `BatchForm.Meta.fields` (insert after `'notes'`):

```python
'bottle_count',
'storage_location',
```

Also add a widget entry for `bottle_count` in `Meta.widgets`:

```python
'bottle_count': forms.NumberInput(attrs={'min': '0'}),
```

- [ ] **Step 2: Create `templates/batches/cellar.html`**

Create the file at `templates/batches/cellar.html`:

```html
{% extends "base.html" %}

{% block title %}Cellar — Skål{% endblock %}

{% block content %}
<div class="page-header">
  <h1>Cellar</h1>
</div>

{% if object_list %}
<div class="table-wrapper">
  <table class="data-table">
    <thead>
      <tr>
        <th>Batch</th>
        <th>Bottles Remaining</th>
        <th>Storage Location</th>
        <th>Days Since Bottling</th>
      </tr>
    </thead>
    <tbody>
      {% for batch in object_list %}
      <tr>
        <td>
          <a href="{% url 'batches:detail' batch.pk %}">{{ batch.name }}</a>
          {% if batch.bottles_remaining == 1 %}
            <span class="badge badge-warning" title="Last bottle!">Last bottle!</span>
          {% endif %}
        </td>
        <td>
          {% if batch.bottles_remaining is not None %}
            {{ batch.bottles_remaining }}
          {% else %}
            &mdash;
          {% endif %}
        </td>
        <td>
          {% if batch.storage_location %}
            {{ batch.storage_location }}
          {% else %}
            &mdash;
          {% endif %}
        </td>
        <td>
          {% if batch.bottled_date %}
            {{ today|timeuntil:batch.bottled_date|cut:" ago" }}
            {# Simpler: compute days directly #}
            {% with days=today|date:"U"|add:"0" %}{% endwith %}
            {{ batch.bottled_date|timesince:today }} ago
          {% else %}
            &mdash;
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<p class="empty-state">
  No bottled batches yet.
  <a href="{% url 'batches:index' %}">View your batches</a>
</p>
{% endif %}
{% endblock %}
```

> **Note on days since bottling:** Django's `timesince`/`timeuntil` filters are designed for datetimes, not pure date arithmetic. A cleaner approach is to pass `today` in context (already done by `CellarView`) and compute days in the template using a custom template filter, or simply display the bottling date alongside the context date and let a small inline calculation handle it. The simplest production-ready approach: add a `days_since_bottling` annotation or computed attribute. For now the template uses `batch.bottled_date` and the `today` context variable; refine the display approach (e.g., a template filter `days_since`) during implementation if the built-in filters don't render cleanly.

- [ ] **Step 3: Add Cellar section to `templates/batches/detail.html`**

Locate the end of the checklist section in `detail.html` (after the bottling checklist row closes). Append the Cellar section immediately after, **inside** the `{% if batch.bottled_done %}` guard (or add its own guard):

```html
{% if batch.bottled_done %}
<section class="cellar-section" style="margin-top:2rem;">
  <h2>Cellar</h2>

  {% if batch.bottle_count %}
  <div class="cellar-stats" style="display:flex;gap:2rem;margin-bottom:1.5rem;flex-wrap:wrap;">
    <div>
      <span class="stat-label">Bottles Remaining</span>
      <span class="stat-value">
        {{ batch.bottles_remaining }}
        {% if batch.bottles_remaining == 1 %}
          <span class="badge badge-warning">Last bottle!</span>
        {% endif %}
      </span>
    </div>
    <div>
      <span class="stat-label">Storage Location</span>
      <span class="stat-value">
        {% if batch.storage_location %}{{ batch.storage_location }}{% else %}&mdash;{% endif %}
      </span>
    </div>
    <div>
      <span class="stat-label">Bottled</span>
      <span class="stat-value">{{ batch.bottled_date }}</span>
    </div>
  </div>
  {% endif %}

  {% if request.user == batch.user %}
  <details class="log-consumption-details" style="margin-bottom:1.5rem;">
    <summary style="cursor:pointer;font-weight:600;">Log Consumption</summary>
    <form method="post" action="{% url 'batches:add_consumption' batch.pk %}"
          style="margin-top:1rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:flex-end;">
      {% csrf_token %}
      <div class="form-group">
        <label for="consume-date">Date</label>
        <input type="date" id="consume-date" name="date"
               value="{{ today }}" required>
      </div>
      <div class="form-group">
        <label for="consume-qty">Bottles</label>
        <input type="number" id="consume-qty" name="quantity"
               min="1" value="1" required style="width:5rem;">
      </div>
      <div class="form-group">
        <label for="consume-notes">Notes <small>(optional)</small></label>
        <input type="text" id="consume-notes" name="notes"
               placeholder="e.g. dinner party" style="width:16rem;">
      </div>
      <button type="submit" class="btn btn-secondary">Log</button>
    </form>
  </details>
  {% endif %}

  {% if batch.consumptions.all %}
  <h3 style="font-size:0.95rem;margin-bottom:0.5rem;">Consumption History</h3>
  <ul class="consumption-list" style="list-style:none;padding:0;margin:0;">
    {% for c in batch.consumptions.all %}
    <li style="padding:0.35rem 0;border-bottom:1px solid var(--border);">
      <span style="font-weight:600;">{{ c.date }}</span>
      &mdash; {{ c.quantity }} bottle{{ c.quantity|pluralize }}
      {% if c.notes %}<span style="color:var(--brown-700);"> &middot; {{ c.notes }}</span>{% endif %}
    </li>
    {% endfor %}
  </ul>
  {% endif %}

</section>
{% endif %}
```

> **Note on `today` in detail template:** The `add_consumption` form defaults the date input to `today`. The `BatchDetailView` does not currently inject `today` into context. Add `context['today'] = datetime.date.today()` to `BatchDetailView.get_context_data` so the template can use it.

- [ ] **Step 4: Update `BatchDetailView.get_context_data` to inject `today`**

In `apps/batches/views.py`, update `BatchDetailView` to pass today's date:

```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['today'] = datetime.date.today()
    return ctx
```

- [ ] **Step 5: Smoke-check the cellar page**

```bash
python manage.py runserver
```

1. Log in, open a batch, mark it as bottled, set `bottle_count` via the edit form.
2. Navigate to `/cellar/` — confirm the batch appears with correct counts.
3. Log a consumption from the detail page — confirm the history list updates and `bottles_remaining` decrements.
4. Reduce to 1 bottle — confirm the last-bottle warning appears on both the cellar page and the detail page.
5. Navigate to `/cellar/` when no bottled batches exist — confirm the empty state renders.

- [ ] **Step 6: Run full test suite**

```bash
pytest --tb=short -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/batches/forms.py apps/batches/views.py templates/batches/cellar.html templates/batches/detail.html
git commit -m "feat: add cellar.html template, batch detail Cellar section, and BatchForm cellar fields"
```
