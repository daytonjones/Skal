# Tasting Log Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let brewers record multiple dated tasting notes per batch to track how a mead evolves over time. Each entry captures aroma, flavor, overall impression, and a numeric score (1–10). Notes appear inline on the batch detail page in newest-first order; no separate listing page is needed.

**Architecture:** A new `TastingNote` model in `apps/batches/models.py` with a `ForeignKey` to `Batch`; a `TastingNoteForm` ModelForm in `apps/batches/forms.py`; three FBV views (`tasting_note_create`, `tasting_note_update`, `tasting_note_delete`) added to `apps/batches/views.py`; three URL patterns added to `apps/batches/urls.py`; a new `templates/batches/tasting_note_form.html` template; and a Tasting Notes section injected into `templates/batches/detail.html`. All views enforce ownership with `get_object_or_404(Batch, pk=batch_pk, user=request.user)` and redirect to `batches:detail` on success.

**Tech Stack:** Django 4.x, Python 3.12, pytest-django, standard form POST + redirect (no AJAX/JSON).

---

### Task 1: `TastingNote` model + migration + model tests

**Files:**
- Modify: `apps/batches/models.py`
- Create: `apps/batches/migrations/XXXX_add_tasting_note.py` (generated)
- Modify: `tests/apps/batches/test_models.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/apps/batches/test_models.py`:

```python
import pytest
import datetime
from django.core.exceptions import ValidationError
from apps.batches.models import Batch, TastingNote


@pytest.fixture
def tasting_note(db, user):
    batch = Batch.objects.create(
        user=user, name='Tasting Batch', batch_size='5.0',
        og='1.100', primary_date=datetime.date(2025, 1, 1),
    )
    return TastingNote.objects.create(
        batch=batch,
        date=datetime.date(2025, 7, 1),
        score=8,
        aroma='Light honey',
        flavor='Clean finish',
        overall='Promising start',
    )


@pytest.mark.django_db
class TestTastingNoteModel:
    def test_tasting_note_str(self, tasting_note):
        assert str(tasting_note) == f"{tasting_note.batch.name} — 2025-07-01 (8/10)"

    def test_score_below_minimum_raises(self, tasting_note):
        tasting_note.score = 0
        with pytest.raises(ValidationError):
            tasting_note.full_clean()

    def test_score_above_maximum_raises(self, tasting_note):
        tasting_note.score = 11
        with pytest.raises(ValidationError):
            tasting_note.full_clean()

    def test_score_boundary_values_valid(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Boundary Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        for score in (1, 10):
            note = TastingNote(batch=batch, date=datetime.date(2025, 7, 1), score=score)
            note.full_clean()  # should not raise

    def test_cascade_delete_with_batch(self, tasting_note):
        batch_pk = tasting_note.batch.pk
        note_pk = tasting_note.pk
        tasting_note.batch.delete()
        assert not TastingNote.objects.filter(pk=note_pk).exists()

    def test_ordering_newest_first(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Order Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 3, 1), score=7)
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 9, 1), score=9)
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 6, 1), score=8)
        dates = list(batch.tasting_notes.values_list('date', flat=True))
        assert dates == sorted(dates, reverse=True)

    def test_optional_text_fields(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Sparse Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        note = TastingNote.objects.create(
            batch=batch, date=datetime.date(2025, 7, 1), score=5
        )
        assert note.aroma == ''
        assert note.flavor == ''
        assert note.overall == ''
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_models.py::TestTastingNoteModel -v
```

Expected: `ImportError` or `FAILED` — `TastingNote` does not exist yet.

- [ ] **Step 3: Add `TastingNote` to `apps/batches/models.py`**

Add `MinValueValidator, MaxValueValidator` to the Django validators import at the top of the file:

```python
from django.core.validators import MinValueValidator, MaxValueValidator
```

Append after the `BatchImage` class:

```python
class TastingNote(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="tasting_notes"
    )
    date = models.DateField()
    aroma = models.TextField(blank=True)
    flavor = models.TextField(blank=True)
    overall = models.TextField(blank=True)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.batch.name} — {self.date} ({self.score}/10)"
```

- [ ] **Step 4: Generate the migration**

```bash
python manage.py makemigrations batches --name add_tasting_note
```

Expected output: `Migrations for 'batches': apps/batches/migrations/XXXX_add_tasting_note.py`

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_models.py::TestTastingNoteModel -v
```

Expected: `7 passed`

- [ ] **Step 6: Run the full model test suite to check for regressions**

```bash
pytest tests/apps/batches/test_models.py -v
```

Expected: all previously passing tests still pass.

- [ ] **Step 7: Commit**

```bash
git add apps/batches/models.py apps/batches/migrations/ tests/apps/batches/test_models.py
git commit -m "feat: add TastingNote model with score validation and cascade delete"
```

---

### Task 2: `TastingNoteForm` + views + URL patterns + view tests

**Files:**
- Modify: `apps/batches/forms.py`
- Modify: `apps/batches/views.py`
- Modify: `apps/batches/urls.py`
- Modify: `tests/apps/batches/test_views.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/apps/batches/test_views.py`:

```python
import datetime
import pytest
from django.urls import reverse
from apps.batches.models import Batch, TastingNote


@pytest.fixture
def note_batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Note Batch',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date(2025, 1, 1),
    )


@pytest.fixture
def tasting_note(db, note_batch):
    return TastingNote.objects.create(
        batch=note_batch,
        date=datetime.date(2025, 7, 1),
        score=8,
        aroma='Floral',
        flavor='Sweet',
        overall='Good',
    )


@pytest.mark.django_db
class TestTastingNoteCreate:
    def test_owner_can_add_note(self, auth_client, note_batch):
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 8,
            'aroma': 'Honey',
            'flavor': 'Crisp',
            'overall': 'Excellent',
        })
        assert response.status_code == 302
        assert TastingNote.objects.filter(batch=note_batch).count() == 1

    def test_invalid_score_rejected(self, auth_client, note_batch):
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 11,
        })
        assert response.status_code == 200  # re-renders form with errors
        assert TastingNote.objects.filter(batch=note_batch).count() == 0

    def test_other_user_cannot_add_note(self, client, other_user, note_batch):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = client.post(url, {
            'date': '2025-07-01',
            'score': 7,
        })
        assert response.status_code == 404


@pytest.mark.django_db
class TestTastingNoteUpdate:
    def test_owner_can_edit_note(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 9,
            'aroma': 'Updated aroma',
            'flavor': 'Updated flavor',
            'overall': 'Even better',
        })
        assert response.status_code == 302
        tasting_note.refresh_from_db()
        assert tasting_note.score == 9

    def test_other_user_cannot_edit_note(self, client, other_user, note_batch, tasting_note):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = client.post(url, {'date': '2025-07-01', 'score': 9})
        assert response.status_code == 404

    def test_note_from_different_batch_not_editable(self, auth_client, db, user, tasting_note):
        other_batch = Batch.objects.create(
            user=user, name='Other', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 2, 1),
        )
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': other_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url, {'date': '2025-07-01', 'score': 9})
        assert response.status_code == 404


@pytest.mark.django_db
class TestTastingNoteDelete:
    def test_owner_can_delete_note(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url)
        assert response.status_code == 302
        assert not TastingNote.objects.filter(pk=tasting_note.pk).exists()

    def test_other_user_cannot_delete_note(self, client, other_user, note_batch, tasting_note):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = client.post(url)
        assert response.status_code == 404
        assert TastingNote.objects.filter(pk=tasting_note.pk).exists()

    def test_get_request_does_not_delete(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        auth_client.get(url)
        assert TastingNote.objects.filter(pk=tasting_note.pk).exists()


@pytest.mark.django_db
class TestTastingNoteContext:
    def test_tasting_notes_in_context(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:detail', kwargs={'pk': note_batch.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert tasting_note in response.context['tasting_notes']

    def test_tasting_notes_ordered_newest_first(self, auth_client, db, user, note_batch):
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 3, 1), score=6)
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 9, 1), score=9)
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 6, 1), score=7)
        url = reverse('batches:detail', kwargs={'pk': note_batch.pk})
        response = auth_client.get(url)
        dates = [n.date for n in response.context['tasting_notes']]
        assert dates == sorted(dates, reverse=True)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_views.py::TestTastingNoteCreate tests/apps/batches/test_views.py::TestTastingNoteUpdate tests/apps/batches/test_views.py::TestTastingNoteDelete tests/apps/batches/test_views.py::TestTastingNoteContext -v
```

Expected: `NoReverseMatch` for `batches:tasting_note_create` — URLs do not exist yet.

- [ ] **Step 3: Add `TastingNoteForm` to `apps/batches/forms.py`**

Update the models import at the top:

```python
from .models import Batch, TastingNote
```

Append after `BatchForm`:

```python
class TastingNoteForm(forms.ModelForm):
    class Meta:
        model = TastingNote
        fields = ['date', 'score', 'aroma', 'flavor', 'overall']
        widgets = {
            'date':    forms.DateInput(attrs={'type': 'date'}),
            'score':   forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'aroma':   forms.Textarea(attrs={'rows': 3}),
            'flavor':  forms.Textarea(attrs={'rows': 3}),
            'overall': forms.Textarea(attrs={'rows': 3}),
        }
```

- [ ] **Step 4: Add three FBVs to `apps/batches/views.py`**

**4a.** Update the `.models` import line to include `TastingNote`:

```python
from .models import Batch, BatchImage, TastingNote
```

**4b.** Update the `.forms` import line to include `TastingNoteForm`:

```python
from .forms import BatchForm, TastingNoteForm
```

**4c.** Add the `date` import at the top of the file (already present as `from datetime import date` — confirm it's there; if not, add it).

**4d.** Append the three view functions before the end of the file:

```python
@login_required
def tasting_note_create(request, batch_pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    if request.method == 'POST':
        form = TastingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.batch = batch
            note.save()
            messages.success(request, 'Tasting note added.')
            return redirect('batches:detail', pk=batch_pk)
    else:
        form = TastingNoteForm(initial={'date': date.today()})
    return render(request, 'batches/tasting_note_form.html', {'form': form, 'batch': batch})


@login_required
def tasting_note_update(request, batch_pk, pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    note = get_object_or_404(TastingNote, pk=pk, batch=batch)
    if request.method == 'POST':
        form = TastingNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tasting note updated.')
            return redirect('batches:detail', pk=batch_pk)
    else:
        form = TastingNoteForm(instance=note)
    return render(request, 'batches/tasting_note_form.html', {'form': form, 'batch': batch, 'note': note})


@login_required
def tasting_note_delete(request, batch_pk, pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    note = get_object_or_404(TastingNote, pk=pk, batch=batch)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Tasting note deleted.')
    return redirect('batches:detail', pk=batch_pk)
```

- [ ] **Step 5: Add URL patterns to `apps/batches/urls.py`**

Update the imports from `.views` to include the three new functions:

```python
from .views import (
    BatchListView,
    BatchDetailView,
    BatchCreateView,
    BatchUpdateView,
    BatchDeleteView,
    toggle_visibility,
    update_checklist_item,
    update_checklist_note,
    tasting_note_create,
    tasting_note_update,
    tasting_note_delete,
)
```

Add the three URL patterns (before the generic CRUD lines is fine):

```python
path('<int:batch_pk>/tasting-notes/add/',            tasting_note_create, name='tasting_note_create'),
path('<int:batch_pk>/tasting-notes/<int:pk>/edit/',   tasting_note_update, name='tasting_note_update'),
path('<int:batch_pk>/tasting-notes/<int:pk>/delete/', tasting_note_delete, name='tasting_note_delete'),
```

- [ ] **Step 6: Add tasting_notes to `BatchDetailView.get_context_data`**

Locate `BatchDetailView` in `apps/batches/views.py`. Add or update `get_context_data` to include tasting notes:

```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['tasting_notes'] = self.object.tasting_notes.all()
    return ctx
```

If `get_context_data` already exists on `BatchDetailView`, add the `tasting_notes` line to it rather than replacing the whole method.

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_views.py::TestTastingNoteCreate tests/apps/batches/test_views.py::TestTastingNoteUpdate tests/apps/batches/test_views.py::TestTastingNoteDelete tests/apps/batches/test_views.py::TestTastingNoteContext -v
```

Expected: `12 passed`

- [ ] **Step 8: Run the full view test suite to check for regressions**

```bash
pytest tests/apps/batches/test_views.py -v
```

Expected: all previously passing tests still pass.

- [ ] **Step 9: Commit**

```bash
git add apps/batches/forms.py apps/batches/views.py apps/batches/urls.py tests/apps/batches/test_views.py
git commit -m "feat: add TastingNoteForm, create/update/delete views, and URL patterns"
```

---

### Task 3: Templates — `tasting_note_form.html` + detail page section

**Files:**
- Create: `templates/batches/tasting_note_form.html`
- Modify: `templates/batches/detail.html`

There are no pure-logic tests for templates; verification is done by running the full test suite (which exercises view rendering) and a smoke-check of the batch detail page.

- [ ] **Step 1: Create `templates/batches/tasting_note_form.html`**

```html
{% extends "base.html" %}

{% block title %}{% if note %}Edit Tasting Note{% else %}Add Tasting Note{% endif %} — {{ batch.name }}{% endblock %}

{% block content %}
<div class="container" style="max-width:640px;margin:2rem auto;">
  <h1>{% if note %}Edit Tasting Note{% else %}Add Tasting Note{% endif %}</h1>
  <p style="color:var(--brown-700);margin-bottom:1.5rem;">{{ batch.name }}</p>

  <form method="post">
    {% csrf_token %}
    {% for field in form %}
      <div class="form-group">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}
          <ul class="errorlist">
            {% for error in field.errors %}
              <li>{{ error }}</li>
            {% endfor %}
          </ul>
        {% endif %}
      </div>
    {% endfor %}
    <div style="display:flex;gap:1rem;margin-top:1.5rem;">
      <button type="submit" class="btn btn-primary">
        {% if note %}Save Changes{% else %}Add Note{% endif %}
      </button>
      <a href="{% url 'batches:detail' pk=batch.pk %}" class="btn btn-secondary">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 2: Add Tasting Notes section to `templates/batches/detail.html`**

Locate the Notes block (the `<section>` or `<div>` that renders `{{ batch.notes }}`). Insert the Tasting Notes section immediately after it, before the action buttons block.

```html
<!-- Tasting Notes -->
<section class="tasting-notes" style="margin:2rem 0;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
    <h2 style="margin:0;">Tasting Notes</h2>
    {% if request.user == batch.user %}
      <a href="{% url 'batches:tasting_note_create' batch_pk=batch.pk %}" class="btn btn-secondary btn-sm">+ Add Note</a>
    {% endif %}
  </div>

  {% if tasting_notes %}
    {% for note in tasting_notes %}
      <div class="tasting-note-card" style="border:1px solid var(--border);border-radius:0.5rem;padding:1rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.5rem;">
          <strong>{{ note.date }}</strong>
          <span style="color:var(--brown-700);font-size:0.9rem;">Score: {{ note.score }}/10</span>
        </div>
        {% if note.aroma %}
          <p style="margin:0.25rem 0;"><span style="font-weight:600;">Aroma:</span> {{ note.aroma }}</p>
        {% endif %}
        {% if note.flavor %}
          <p style="margin:0.25rem 0;"><span style="font-weight:600;">Flavor:</span> {{ note.flavor }}</p>
        {% endif %}
        {% if note.overall %}
          <p style="margin:0.25rem 0;"><span style="font-weight:600;">Overall:</span> {{ note.overall }}</p>
        {% endif %}
        {% if request.user == batch.user %}
          <div style="margin-top:0.75rem;display:flex;gap:0.75rem;">
            <a href="{% url 'batches:tasting_note_update' batch_pk=batch.pk pk=note.pk %}"
               class="btn btn-secondary btn-sm">Edit</a>
            <form method="post"
                  action="{% url 'batches:tasting_note_delete' batch_pk=batch.pk pk=note.pk %}"
                  style="display:inline;">
              {% csrf_token %}
              <button type="submit" class="btn btn-danger btn-sm"
                      onclick="return confirm('Delete this tasting note?')">Delete</button>
            </form>
          </div>
        {% endif %}
      </div>
    {% endfor %}
  {% else %}
    {% if request.user == batch.user %}
      <p style="color:var(--brown-600);font-style:italic;">
        No tasting notes yet.
        <a href="{% url 'batches:tasting_note_create' batch_pk=batch.pk %}">Add the first one.</a>
      </p>
    {% endif %}
  {% endif %}
</section>
```

- [ ] **Step 3: Run the full test suite**

```bash
pytest --tb=short -q
```

Expected: all tests pass (no template rendering errors from the new sections).

- [ ] **Step 4: Smoke-check the detail page renders**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
git add templates/batches/tasting_note_form.html templates/batches/detail.html
git commit -m "feat: add tasting note form template and detail page section"
```
