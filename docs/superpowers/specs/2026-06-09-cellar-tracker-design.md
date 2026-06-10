# Cellar Tracker — Design Spec
**Date:** 2026-06-09
**Branch:** v2_2
**Status:** Draft (pending user approval)

## Goal

After a batch is bottled, give the user a simple cellar inventory: how many bottles remain, where they're stored, and how old they are. Consumption events are recorded inline on the batch detail page. A dedicated `/cellar/` view surfaces all bottled batches at a glance with a last-bottle warning when only one bottle remains.

## Data Model

### Changes to `Batch`

Add two nullable/blank fields:

```python
bottle_count     = models.PositiveIntegerField(null=True, blank=True)
storage_location = models.CharField(max_length=200, blank=True)
```

Add a computed property:

```python
@property
def bottles_remaining(self):
    """Returns None if bottle_count is not set; otherwise bottle_count minus consumed."""
    if self.bottle_count is None:
        return None
    consumed = self.consumptions.aggregate(total=models.Sum('quantity'))['total'] or 0
    return self.bottle_count - consumed
```

### New model: `BottleConsumption`

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

No separate consumption history page. All consumption records are displayed inline on the batch detail page.

### Migration

One migration covering both the two new `Batch` fields and the new `BottleConsumption` model.

## Views and URLs

### `/cellar/` — `CellarView`

- `LoginRequiredMixin`, `ListView`
- Queryset: `Batch.objects.filter(user=request.user, bottled_done=True).order_by('-bottling_date').prefetch_related('consumptions')`
- Context extras: today's date (for computing days since bottling)
- Template: `batches/cellar.html`

### `POST /batches/<pk>/consume/` — `add_consumption`

- `@login_required` function-based view (matches the style of `update_checklist_item` and `update_checklist_note`)
- Ownership check via `get_object_or_404(Batch, pk=pk, user=request.user)`
- Accepts: `date`, `quantity`, `notes` from POST body
- On success: redirect to `batches:detail` with a `messages.success` flash (matches existing form-save pattern)
- On invalid data: redirect back with `messages.error`

### URL wiring

In `apps/batches/urls.py`:

```python
path('<int:pk>/consume/', add_consumption, name='add_consumption'),
```

In `skal/urls.py`:

```python
path('cellar/', include(('apps.batches.cellar_urls', 'cellar'), namespace='cellar')),
```

Actually simpler: add the cellar view directly to `skal/urls.py` as a top-level route, since it spans all bottled batches rather than a single batch:

```python
from apps.batches.views import CellarView
path('cellar/', CellarView.as_view(), name='cellar'),
```

`add_consumption` lives in the existing `batches/` namespace at `batches/<pk>/consume/`.

## UI / Template

### `templates/batches/cellar.html`

Extends `base.html`. Renders a table or card list of bottled batches. Each row/card shows:

| Field | Source |
|---|---|
| Batch name (link to detail) | `batch.name` |
| Bottles remaining | `batch.bottles_remaining` — show "—" if `None` |
| Storage location | `batch.storage_location` — show "—" if blank |
| Days since bottling | `(today - batch.bottling_date).days` — computed in template via a custom tag or passed in context |
| Last-bottle warning | Rendered when `batch.bottles_remaining == 1` |

Empty state: "No bottled batches yet." with a link to the batch list.

### Batch detail page (`templates/batches/detail.html`)

When `batch.bottled_done` is true, append a "Cellar" section after the checklist. It contains:

1. **Cellar stats strip** — bottles remaining, storage location (editable via the batch edit form), days since bottling. Only rendered when `batch.bottle_count` is set.
2. **Log consumption form** — a compact inline form (date defaulting to today, quantity, optional notes) that POSTs to `batches:add_consumption`. Shown only to the batch owner.
3. **Consumption history list** — ordered by date descending; each entry shows date, quantity, and notes. Rendered from `batch.consumptions.all`. Hidden (or shows "No bottles consumed yet.") when empty.

`bottle_count` and `storage_location` are edited via the existing batch edit form — no separate cellar-edit form needed.

### `BatchForm` updates

Add `bottle_count` and `storage_location` to `BatchForm.Meta.fields`. No special widget needed beyond the default.

## Files Changed / Created

| File | Change |
|---|---|
| `apps/batches/models.py` | Add `bottle_count`, `storage_location` to `Batch`; add `bottles_remaining` property; add `BottleConsumption` model |
| `apps/batches/forms.py` | Add `bottle_count` and `storage_location` to `BatchForm.Meta.fields` |
| `apps/batches/views.py` | Add `CellarView` (ListView); add `add_consumption` function view; import `BottleConsumption` |
| `apps/batches/urls.py` | Add `path('<int:pk>/consume/', ...)` |
| `skal/urls.py` | Add `path('cellar/', CellarView.as_view(), name='cellar')` |
| `apps/batches/migrations/XXXX_cellar_tracker.py` | New migration (auto-generated) |
| `templates/batches/cellar.html` | New template |
| `templates/batches/detail.html` | Add cellar section (stats strip + consumption form + history list) |

## Testing

### Model tests (`tests/apps/batches/test_models.py`)

- `bottles_remaining` returns `None` when `bottle_count` is not set
- `bottles_remaining` returns `bottle_count` when no consumptions exist
- `bottles_remaining` correctly subtracts the sum of all consumption quantities
- `bottles_remaining` can return 0 when all bottles are consumed

### View tests (`tests/apps/batches/test_views.py`)

- `GET /cellar/` requires login (redirects anonymous users)
- `GET /cellar/` returns only the logged-in user's bottled batches
- `GET /cellar/` excludes batches where `bottled_done=False`
- `POST /batches/<pk>/consume/` creates a `BottleConsumption` record and redirects to batch detail
- `POST /batches/<pk>/consume/` returns 404 when another user tries to log consumption against a batch they don't own
- `POST /batches/<pk>/consume/` with missing/invalid `quantity` re-renders with an error and does not create a record
