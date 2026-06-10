# Tasting Log — Design Spec
**Date:** 2026-06-09
**Branch:** v2_2
**Status:** Draft (pending user approval)

---

## Goal

Let brewers record multiple dated tasting notes per batch to track how a mead evolves over time — e.g., entries at 3 months, 6 months, and 1 year post-bottling. Each entry captures aroma, flavor, overall impression, and a numeric score. Notes appear inline on the batch detail page; no separate page is needed.

---

## Data Model

New model `TastingNote` in `apps/batches/models.py`:

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

Key decisions:
- `aroma`, `flavor`, and `overall` are optional `TextField`s so a brewer can fill in whatever fields are useful at any given tasting.
- `score` is required (1–10). Enforced via `MinValueValidator`/`MaxValueValidator` on the model and validated in the form.
- Default ordering is newest-first (`-date`).
- Cascade delete: removing a batch removes all its tasting notes.

Migration: a single new migration in `apps/batches/migrations/`.

---

## Views and URLs

Four new view functions added to `apps/batches/views.py`. All are function-based (matching the existing AJAX-style views like `toggle_visibility`). All require `@login_required` and ownership checks via `get_object_or_404(Batch, pk=batch_pk, user=request.user)`.

| View | Method | Purpose |
|---|---|---|
| `tasting_note_create` | POST | Add a new note to a batch |
| `tasting_note_update` | POST | Edit an existing note |
| `tasting_note_delete` | POST | Delete a note |

All three redirect back to `batches:detail` on success. They do not return JSON — they use standard form POST + redirect, consistent with `toggle_visibility`.

New URL patterns appended to `apps/batches/urls.py`:

```python
path('<int:batch_pk>/tasting-notes/add/',           tasting_note_create, name='tasting_note_create'),
path('<int:batch_pk>/tasting-notes/<int:pk>/edit/',  tasting_note_update, name='tasting_note_update'),
path('<int:batch_pk>/tasting-notes/<int:pk>/delete/', tasting_note_delete, name='tasting_note_delete'),
```

`batch_pk` is used in all three so the view can scope both the ownership check (batch must belong to `request.user`) and the note lookup (`TastingNote` must belong to that batch).

### View sketches

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

---

## UI / Template

### Form

New `TastingNoteForm` in `apps/batches/forms.py`:

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

### New template: `templates/batches/tasting_note_form.html`

Standalone page (extends `base.html`) used for both add and edit. Shows the form with a "Save" button and a "Cancel" link back to the batch detail. The `<h1>` reads "Add Tasting Note" or "Edit Tasting Note" based on whether `note` is in context.

### Batch detail page (`templates/batches/detail.html`)

Add a **Tasting Notes** section between the existing Notes block and the action buttons. Visible to all users who can view the batch; add/edit/delete controls are gated on `request.user == batch.user`.

Layout of the section:

```
## Tasting Notes                            [+ Add Note]  (owner only)

┌─────────────────────────────────────────────────────┐
│  2026-03-15  ·  Score: 8/10                         │
│  Aroma:   Light honey, subtle floral notes          │
│  Flavor:  Clean, slightly sweet finish              │
│  Overall: Needs more time; promising start          │
│                              [Edit]  [Delete]       │  (owner only)
└─────────────────────────────────────────────────────┘
```

Each note renders as a `<div class="tasting-note-card">`. The delete button is a small inline `<form method="post">` (no JS required). The edit button is a plain `<a>` link to `tasting_note_update`.

If no notes exist, show:
- For the owner: "No tasting notes yet. Add the first one."
- For other viewers: nothing (the section is omitted entirely).

The "Add Note" button and the per-note controls are wrapped in `{% if request.user == batch.user %}`.

Context passed from `BatchDetailView.get_context_data`:

```python
ctx['tasting_notes'] = self.object.tasting_notes.all()  # already ordered -date by Meta
```

---

## Files Changed / Created

| File | Change |
|---|---|
| `apps/batches/models.py` | Add `TastingNote` model (import `MinValueValidator`, `MaxValueValidator`) |
| `apps/batches/migrations/XXXX_add_tasting_note.py` | New migration |
| `apps/batches/forms.py` | Add `TastingNoteForm` |
| `apps/batches/views.py` | Add `tasting_note_create`, `tasting_note_update`, `tasting_note_delete`; update `BatchDetailView.get_context_data` to include `tasting_notes` |
| `apps/batches/urls.py` | Add three new URL patterns; add three new view imports |
| `templates/batches/detail.html` | Add Tasting Notes section |
| `templates/batches/tasting_note_form.html` | New template (create/edit form) |
| `tests/apps/batches/test_models.py` | Add `TestTastingNoteModel` |
| `tests/apps/batches/test_views.py` | Add `TestTastingNoteViews` |

---

## Testing

### Model tests (`test_models.py` — `TestTastingNoteModel`)

- `test_tasting_note_str` — `__str__` returns expected format
- `test_score_below_minimum_raises` — score=0 fails validation
- `test_score_above_maximum_raises` — score=11 fails validation
- `test_score_boundary_values_valid` — scores 1 and 10 pass validation
- `test_cascade_delete_with_batch` — deleting a batch deletes its notes
- `test_ordering_newest_first` — two notes on different dates; `.all()` returns newer first
- `test_optional_text_fields` — note with only `score` and `date` saves without error

### View tests (`test_views.py` — `TestTastingNoteViews`)

**Create:**
- `test_owner_can_add_note` — POST valid data → 302, note exists in DB
- `test_invalid_score_rejected` — POST score=0 → re-renders form (200), no note created
- `test_other_user_cannot_add_note` — 404

**Update:**
- `test_owner_can_edit_note` — POST updated data → 302, DB reflects change
- `test_other_user_cannot_edit_note` — 404
- `test_note_from_different_batch_not_editable` — note belongs to another batch; 404

**Delete:**
- `test_owner_can_delete_note` — POST → 302, note gone from DB
- `test_other_user_cannot_delete_note` — 404
- `test_get_request_does_not_delete` — GET to delete URL redirects without deleting

**Detail context:**
- `test_tasting_notes_in_context` — `BatchDetailView` includes `tasting_notes` in context
- `test_tasting_notes_ordered_newest_first` — context queryset is ordered correctly
