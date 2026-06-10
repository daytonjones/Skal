# Batch Email Notifications Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Send opt-in daily digest emails to users on the day each TOSNA nutrient addition, gravity check, rack-to-secondary, or bottling event is due across all their active batches.

**Architecture:** A new `UserNotificationPrefs` one-to-one model captures per-user opt-in flags; a pure `get_due_events(batch, prefs, today)` function in `apps/batches/notifications.py` computes due labels with no DB calls; a `send_batch_notifications` management command queries opted-in users, collects events, and sends one digest email per user. The profile page gains a second `NotificationPrefsForm` submitted via a separate `<form>` POST to a new `save_notification_prefs` view function, keeping the existing `ProfileUpdateView` untouched.

**Tech Stack:** Django 4.x, Python 3.12, pytest-django, `django.core.mail.send_mail`, Docker cron.

---

### Task 1: `UserNotificationPrefs` model + migration

**Files:**
- Modify: `apps/accounts/models.py`
- Create: `apps/accounts/migrations/0006_usernotificationprefs.py` (generated)
- Create: `tests/apps/accounts/test_notification_prefs.py`

- [ ] **Step 1: Write the failing test**

Create `tests/apps/accounts/test_notification_prefs.py`:

```python
import pytest
from django.contrib.auth import get_user_model
from apps.accounts.models import UserNotificationPrefs

User = get_user_model()


@pytest.mark.django_db
class TestUserNotificationPrefsModel:
    def test_prefs_created_with_defaults(self, user):
        prefs, created = UserNotificationPrefs.objects.get_or_create(user=user)
        assert created is True
        assert prefs.email_notifications is False
        assert prefs.notify_tosna is True
        assert prefs.notify_sg_check is True
        assert prefs.notify_rack is False
        assert prefs.notify_bottle is False

    def test_prefs_str(self, user):
        prefs = UserNotificationPrefs.objects.create(user=user)
        assert str(prefs) == f"Notification prefs for {user.username}"

    def test_one_to_one_uniqueness(self, user):
        from django.db import IntegrityError
        UserNotificationPrefs.objects.create(user=user)
        with pytest.raises(IntegrityError):
            UserNotificationPrefs.objects.create(user=user)

    def test_related_name(self, user):
        prefs = UserNotificationPrefs.objects.create(user=user)
        assert user.notification_prefs == prefs
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/apps/accounts/test_notification_prefs.py -v
```

Expected: `ImportError` or `FAILED` — `UserNotificationPrefs` does not exist yet.

- [ ] **Step 3: Add `UserNotificationPrefs` to `apps/accounts/models.py`**

Append after the `User` class:

```python
class UserNotificationPrefs(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_prefs',
    )
    email_notifications = models.BooleanField(default=False)
    notify_tosna        = models.BooleanField(default=True)
    notify_sg_check     = models.BooleanField(default=True)
    notify_rack         = models.BooleanField(default=False)
    notify_bottle       = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification prefs for {self.user.username}"
```

- [ ] **Step 4: Generate the migration**

```bash
python manage.py makemigrations accounts --name usernotificationprefs
```

Expected output: `Migrations for 'accounts': apps/accounts/migrations/0006_usernotificationprefs.py`

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/apps/accounts/test_notification_prefs.py -v
```

Expected: `4 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/accounts/models.py apps/accounts/migrations/0006_usernotificationprefs.py tests/apps/accounts/test_notification_prefs.py
git commit -m "feat: add UserNotificationPrefs model with opt-in email notification flags"
```

---

### Task 2: `NotificationPrefsForm` + profile view/template changes

**Files:**
- Modify: `apps/accounts/forms.py`
- Modify: `apps/accounts/views.py`
- Modify: `apps/accounts/urls.py`
- Modify: `templates/accounts/profile.html`
- Modify: `tests/apps/accounts/test_notification_prefs.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/apps/accounts/test_notification_prefs.py`:

```python
from django.urls import reverse


@pytest.mark.django_db
class TestNotificationPrefsForm:
    def test_form_renders_all_fields(self, auth_client):
        response = auth_client.get(reverse('accounts:profile'))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'email_notifications' in content
        assert 'notify_tosna' in content
        assert 'notify_sg_check' in content
        assert 'notify_rack' in content
        assert 'notify_bottle' in content

    def test_prefs_created_on_profile_get(self, auth_client, user):
        auth_client.get(reverse('accounts:profile'))
        assert UserNotificationPrefs.objects.filter(user=user).exists()

    def test_save_notification_prefs_turns_on_master(self, auth_client, user):
        response = auth_client.post(reverse('accounts:save_notification_prefs'), {
            'email_notifications': 'on',
            'notify_tosna': 'on',
            'notify_sg_check': 'on',
        })
        assert response.status_code == 302
        prefs = UserNotificationPrefs.objects.get(user=user)
        assert prefs.email_notifications is True
        assert prefs.notify_tosna is True
        assert prefs.notify_rack is False

    def test_save_notification_prefs_turns_off_master(self, auth_client, user):
        UserNotificationPrefs.objects.create(user=user, email_notifications=True)
        response = auth_client.post(reverse('accounts:save_notification_prefs'), {
            'notify_tosna': 'on',
        })
        assert response.status_code == 302
        prefs = UserNotificationPrefs.objects.get(user=user)
        assert prefs.email_notifications is False

    def test_save_notification_prefs_requires_login(self, client):
        response = client.post(reverse('accounts:save_notification_prefs'), {})
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/accounts/test_notification_prefs.py::TestNotificationPrefsForm -v
```

Expected: `NoReverseMatch` for `accounts:save_notification_prefs` and assertion failures.

- [ ] **Step 3: Add `NotificationPrefsForm` to `apps/accounts/forms.py`**

Replace the existing User-only import at the top:

```python
from .models import User, UserNotificationPrefs
```

Append this form class:

```python
class NotificationPrefsForm(forms.ModelForm):
    class Meta:
        model = UserNotificationPrefs
        fields = ('email_notifications', 'notify_tosna', 'notify_sg_check',
                  'notify_rack', 'notify_bottle')
        labels = {
            'email_notifications': 'Email me brewing reminders',
            'notify_tosna':        'Nutrient additions (TOSNA 24h / 48h / 72h)',
            'notify_sg_check':     'Gravity check reminder (~day 4)',
            'notify_rack':         'Rack to secondary',
            'notify_bottle':       'Bottling day',
        }
```

- [ ] **Step 4: Update `apps/accounts/views.py`**

**4a.** Update the `.forms` import to include `NotificationPrefsForm`:

```python
from .forms import SignUpForm, ProfileForm, CustomPasswordChangeForm, NotificationPrefsForm
```

**4b.** Update the `.models` import to include `UserNotificationPrefs`:

```python
from .models import User, UserNotificationPrefs
```

**4c.** Update `ProfileUpdateView.get_context_data` to create prefs and pass the form:

```python
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['password_form'] = CustomPasswordChangeForm(self.request.user)
        prefs, _ = UserNotificationPrefs.objects.get_or_create(user=self.request.user)
        ctx['notification_prefs_form'] = NotificationPrefsForm(instance=prefs)
        return ctx
```

**4d.** Add this new view function (before `CustomPasswordChangeView`):

```python
@login_required
@require_POST
def save_notification_prefs(request):
    prefs, _ = UserNotificationPrefs.objects.get_or_create(user=request.user)
    form = NotificationPrefsForm(request.POST, instance=prefs)
    if form.is_valid():
        form.save()
        messages.success(request, 'Notification preferences saved.')
    return redirect(reverse_lazy('accounts:profile'))
```

- [ ] **Step 5: Add URL to `apps/accounts/urls.py`**

Add `save_notification_prefs` to the imports from `.views`, then add to `urlpatterns`:

```python
path("profile/notifications/", save_notification_prefs, name="save_notification_prefs"),
```

- [ ] **Step 6: Update `templates/accounts/profile.html`**

Add the Notifications section after the profile `</form>` and before the Change Password `<hr>`:

```html
  <hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0;">
  <h2>Notifications</h2>
  <form method="post" action="{% url 'accounts:save_notification_prefs' %}">
    {% csrf_token %}
    <div class="form-group" style="display:flex;align-items:center;gap:0.5rem;">
      {{ notification_prefs_form.email_notifications }}
      <label for="{{ notification_prefs_form.email_notifications.id_for_label }}"
             style="text-transform:none;font-size:0.875rem;color:var(--brown-900);margin:0;">
        {{ notification_prefs_form.email_notifications.label }}
      </label>
    </div>
    <fieldset id="notification-sub-prefs" style="border:none;padding:0;margin:0.75rem 0 0 1.5rem;">
      <legend style="font-size:0.8rem;color:var(--brown-700);margin-bottom:0.5rem;">Notify me about:</legend>
      {% for field in notification_prefs_form %}
        {% if field.name != 'email_notifications' %}
          <div class="form-group" style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;">
            {{ field }}
            <label for="{{ field.id_for_label }}"
                   style="text-transform:none;font-size:0.875rem;color:var(--brown-900);margin:0;">
              {{ field.label }}
            </label>
          </div>
        {% endif %}
      {% endfor %}
    </fieldset>
    <button type="submit" class="btn btn-secondary" style="margin-top:0.75rem;">Save Notification Preferences</button>
  </form>
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest tests/apps/accounts/test_notification_prefs.py -v
```

Expected: `9 passed`

- [ ] **Step 8: Commit**

```bash
git add apps/accounts/forms.py apps/accounts/views.py apps/accounts/urls.py templates/accounts/profile.html tests/apps/accounts/test_notification_prefs.py
git commit -m "feat: add NotificationPrefsForm and profile Notifications section"
```

---

### Task 3: `get_due_events()` pure function

**Files:**
- Create: `apps/batches/notifications.py`
- Create: `tests/apps/batches/test_notifications.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/apps/batches/test_notifications.py`:

```python
import datetime
import pytest
from unittest.mock import MagicMock
from apps.batches.notifications import get_due_events


def make_prefs(
    notify_tosna=True,
    notify_sg_check=True,
    notify_rack=True,
    notify_bottle=True,
):
    prefs = MagicMock()
    prefs.notify_tosna = notify_tosna
    prefs.notify_sg_check = notify_sg_check
    prefs.notify_rack = notify_rack
    prefs.notify_bottle = notify_bottle
    return prefs


def make_batch(
    pitch_yeast_date=None,
    secondary_date=None,
    bottling_date=None,
    fo_24h_done=False,
    fo_48h_done=False,
    fo_72h_done=False,
    fo_1_3_break_done=False,
    rack_secondary_done=False,
    bottled_done=False,
):
    batch = MagicMock()
    batch.pitch_yeast_date = pitch_yeast_date
    batch.secondary_date = secondary_date
    batch.bottling_date = bottling_date
    batch.fo_24h_done = fo_24h_done
    batch.fo_48h_done = fo_48h_done
    batch.fo_72h_done = fo_72h_done
    batch.fo_1_3_break_done = fo_1_3_break_done
    batch.rack_secondary_done = rack_secondary_done
    batch.bottled_done = bottled_done
    batch.name = "Test Batch"
    return batch


BASE_DATE = datetime.date(2026, 6, 10)


class TestGetDueEventsTosna:
    def test_24h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 24h nutrient addition" in events

    def test_48h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 8))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 48h nutrient addition" in events

    def test_72h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 7))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 72h nutrient addition" in events

    def test_24h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9), fo_24h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 24h nutrient addition" not in events

    def test_48h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 8), fo_48h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 48h nutrient addition" not in events

    def test_72h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 7), fo_72h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 72h nutrient addition" not in events

    def test_tosna_skipped_when_no_pitch_date(self):
        batch = make_batch(pitch_yeast_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)

    def test_tosna_skipped_when_pref_off(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9))
        prefs = make_prefs(notify_tosna=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)

    def test_no_false_positive_on_wrong_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 5))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)


class TestGetDueEventsSgCheck:
    def test_sg_check_fires_on_day_4(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" in events

    def test_sg_check_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6), fo_1_3_break_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events

    def test_sg_check_skipped_when_no_pitch_date(self):
        batch = make_batch(pitch_yeast_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events

    def test_sg_check_skipped_when_pref_off(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6))
        prefs = make_prefs(notify_sg_check=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events


class TestGetDueEventsRack:
    def test_rack_fires_on_secondary_date(self):
        batch = make_batch(secondary_date=BASE_DATE)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" in events

    def test_rack_skipped_when_done(self):
        batch = make_batch(secondary_date=BASE_DATE, rack_secondary_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events

    def test_rack_skipped_when_no_secondary_date(self):
        batch = make_batch(secondary_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events

    def test_rack_skipped_when_pref_off(self):
        batch = make_batch(secondary_date=BASE_DATE)
        prefs = make_prefs(notify_rack=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events


class TestGetDueEventsBottle:
    def test_bottle_fires_on_bottling_date(self):
        batch = make_batch(bottling_date=BASE_DATE)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" in events

    def test_bottle_skipped_when_done(self):
        batch = make_batch(bottling_date=BASE_DATE, bottled_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events

    def test_bottle_skipped_when_no_bottling_date(self):
        batch = make_batch(bottling_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events

    def test_bottle_skipped_when_pref_off(self):
        batch = make_batch(bottling_date=BASE_DATE)
        prefs = make_prefs(notify_bottle=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events


class TestGetDueEventsEmpty:
    def test_returns_empty_list_when_nothing_due(self):
        batch = make_batch()
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert events == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_notifications.py -v
```

Expected: `ImportError` — `apps.batches.notifications` does not exist yet.

- [ ] **Step 3: Create `apps/batches/notifications.py`**

```python
import datetime


def get_due_events(batch, prefs, today: datetime.date) -> list[str]:
    """
    Pure function. Returns a list of human-readable event labels due
    today for `batch` given user notification `prefs`. No DB calls.
    """
    events: list[str] = []

    if prefs.notify_tosna and batch.pitch_yeast_date:
        if not batch.fo_24h_done and batch.pitch_yeast_date + datetime.timedelta(days=1) == today:
            events.append("TOSNA 24h nutrient addition")
        if not batch.fo_48h_done and batch.pitch_yeast_date + datetime.timedelta(days=2) == today:
            events.append("TOSNA 48h nutrient addition")
        if not batch.fo_72h_done and batch.pitch_yeast_date + datetime.timedelta(days=3) == today:
            events.append("TOSNA 72h nutrient addition")

    if prefs.notify_sg_check and batch.pitch_yeast_date:
        if not batch.fo_1_3_break_done and batch.pitch_yeast_date + datetime.timedelta(days=4) == today:
            events.append("1/3 sugar break gravity check")

    if prefs.notify_rack and batch.secondary_date:
        if not batch.rack_secondary_done and batch.secondary_date == today:
            events.append("Rack to secondary")

    if prefs.notify_bottle and batch.bottling_date:
        if not batch.bottled_done and batch.bottling_date == today:
            events.append("Bottling day")

    return events
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_notifications.py -v
```

Expected: `21 passed`

- [ ] **Step 5: Commit**

```bash
git add apps/batches/notifications.py tests/apps/batches/test_notifications.py
git commit -m "feat: add get_due_events() pure function for batch notification logic"
```

---

### Task 4: `send_batch_notifications` management command + email templates

**Files:**
- Create: `apps/batches/management/__init__.py`
- Create: `apps/batches/management/commands/__init__.py`
- Create: `apps/batches/management/commands/send_batch_notifications.py`
- Create: `templates/batches/email/batch_notifications.html`
- Create: `templates/batches/email/batch_notifications.txt`
- Modify: `tests/apps/batches/test_notifications.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/apps/batches/test_notifications.py`:

```python
import datetime
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from apps.accounts.models import UserNotificationPrefs
from apps.batches.models import Batch

User = get_user_model()

TODAY = datetime.date(2026, 6, 10)


@pytest.fixture
def opted_in_user(db):
    u = User.objects.create_user(
        username='brewer1', email='brewer1@example.com', password='pass',
        is_approved=True,
    )
    UserNotificationPrefs.objects.create(
        user=u,
        email_notifications=True,
        notify_tosna=True,
        notify_sg_check=True,
        notify_rack=True,
        notify_bottle=True,
    )
    return u


@pytest.fixture
def opted_out_user(db):
    u = User.objects.create_user(
        username='brewer2', email='brewer2@example.com', password='pass',
        is_approved=True,
    )
    UserNotificationPrefs.objects.create(user=u, email_notifications=False)
    return u


@pytest.fixture
def batch_with_24h_due(opted_in_user):
    return Batch.objects.create(
        user=opted_in_user,
        name='Wildflower Mead',
        batch_size='5.0',
        og='1.110',
        primary_date=datetime.date(2026, 6, 1),
        pitch_yeast_date=datetime.date(2026, 6, 9),  # +1 day = TODAY
    )


@pytest.mark.django_db
class TestSendBatchNotificationsCommand:
    def _call_command(self, today=TODAY):
        from django.core.management import call_command
        with patch('apps.batches.management.commands.send_batch_notifications.date') as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            call_command('send_batch_notifications')

    def test_sends_email_to_opted_in_user_with_due_events(
        self, opted_in_user, batch_with_24h_due
    ):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            assert mock_send.call_count == 1
            _, kwargs = mock_send.call_args
            assert opted_in_user.email in kwargs.get('recipient_list', [])

    def test_email_subject_contains_date(self, opted_in_user, batch_with_24h_due):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            _, kwargs = mock_send.call_args
            assert '2026-06-10' in kwargs.get('subject', '')

    def test_no_email_for_opted_out_user(self, opted_out_user):
        Batch.objects.create(
            user=opted_out_user,
            name='Opted Out Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_no_email_when_no_events_due(self, opted_in_user):
        Batch.objects.create(
            user=opted_in_user,
            name='Old Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 5, 1),
            pitch_yeast_date=datetime.date(2026, 5, 11),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_no_email_for_user_with_no_email_address(self, db):
        u = User.objects.create_user(
            username='noemail', email='', password='pass', is_approved=True,
        )
        UserNotificationPrefs.objects.create(user=u, email_notifications=True, notify_tosna=True)
        Batch.objects.create(
            user=u,
            name='No Email Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_send_error_is_logged_not_raised(self, opted_in_user, batch_with_24h_due):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail',
                   side_effect=Exception("SMTP down")):
            with patch('apps.batches.management.commands.send_batch_notifications.logger') as mock_logger:
                self._call_command()
                mock_logger.error.assert_called_once()

    def test_bottled_batch_excluded(self, opted_in_user):
        Batch.objects.create(
            user=opted_in_user,
            name='Bottled Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
            bottled_done=True,
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/apps/batches/test_notifications.py::TestSendBatchNotificationsCommand -v
```

Expected: `CommandError` or `ModuleNotFoundError` — command does not exist yet.

- [ ] **Step 3: Create `__init__.py` files**

Create two empty files:
- `apps/batches/management/__init__.py`
- `apps/batches/management/commands/__init__.py`

- [ ] **Step 4: Create `apps/batches/management/commands/send_batch_notifications.py`**

```python
import logging
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse

from apps.batches.notifications import get_due_events

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Send daily batch brewing reminder emails to opted-in users'

    def handle(self, *args, **options):
        today = date.today()
        subject = f"Skål — Brewing reminders for {today}"

        users = (
            User.objects
            .filter(notification_prefs__email_notifications=True)
            .exclude(email='')
            .select_related('notification_prefs')
        )

        for user in users:
            prefs = user.notification_prefs
            active_batches = user.batches.filter(bottled_done=False)

            batch_events = []
            for batch in active_batches:
                events = get_due_events(batch, prefs, today)
                if events:
                    batch_events.append({'batch': batch, 'events': events})

            if not batch_events:
                self.stdout.write(f'No events due for {user.username} — skipping.')
                continue

            hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            host = next((h for h in hosts if h not in ('*', '', 'localhost', '127.0.0.1')), None)
            profile_url = reverse('accounts:profile')
            profile_full_url = f"http://{host}{profile_url}" if host else profile_url

            context = {
                'user': user,
                'batch_events': batch_events,
                'today': today,
                'profile_url': profile_full_url,
            }
            html_body = render_to_string('batches/email/batch_notifications.html', context)
            text_body = render_to_string('batches/email/batch_notifications.txt', context)

            try:
                send_mail(
                    subject=subject,
                    message=text_body,
                    html_message=html_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                self.stdout.write(f'Sent brewing reminder to {user.email}')
                logger.info("Sent brewing reminder to %s", user.email)
            except Exception as exc:
                logger.error("Failed to send brewing reminder to %s: %s", user.email, exc)
                self.stdout.write(f'Failed to send reminder to {user.email}: {exc}')
```

- [ ] **Step 5: Create `templates/batches/email/batch_notifications.txt`**

(Create the `templates/batches/email/` directory first.)

```
Skål — Brewing reminders for {{ today }}
========================================

Hi {{ user.get_full_name|default:user.username }},

Here are your brewing tasks due today:

{% for item in batch_events %}
{{ item.batch.name }}
{% for event in item.events %}  • {{ event }}
{% endfor %}
{% endfor %}

Manage your notification preferences at {{ profile_url }}

Skål!
```

- [ ] **Step 6: Create `templates/batches/email/batch_notifications.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Skål — Brewing Reminders</title>
</head>
<body style="font-family:sans-serif;color:#3d2b1f;max-width:600px;margin:0 auto;padding:1.5rem;">
  <h2 style="color:#7c4a1e;">Skål — Brewing reminders for {{ today }}</h2>
  <p>Hi {{ user.get_full_name|default:user.username }},</p>
  <p>Here are your brewing tasks due today:</p>

  {% for item in batch_events %}
  <div style="margin:1rem 0;padding:1rem;border-left:4px solid #c4874a;background:#fdf6f0;">
    <strong style="font-size:1rem;">{{ item.batch.name }}</strong>
    <ul style="margin:0.5rem 0 0 0;padding-left:1.25rem;">
      {% for event in item.events %}
      <li>{{ event }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endfor %}

  <p style="margin-top:2rem;font-size:0.85rem;color:#7c5c3e;">
    Manage your notification preferences at
    <a href="{{ profile_url }}" style="color:#c4874a;">{{ profile_url }}</a>
  </p>
  <p style="font-size:1.1rem;">Skål!</p>
</body>
</html>
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest tests/apps/batches/test_notifications.py -v
```

Expected: `28 passed` (21 from Task 3 + 7 from this task)

- [ ] **Step 8: Commit**

```bash
git add apps/batches/management/ apps/batches/notifications.py templates/batches/email/ tests/apps/batches/test_notifications.py
git commit -m "feat: add send_batch_notifications management command and email templates"
```

---

### Task 5: Docker cron setup

**Files:**
- Create: `docker/skal-cron`
- Modify: `Dockerfile`
- Modify: `entrypoint.sh`

- [ ] **Step 1: Create `docker/skal-cron`**

```
0 7 * * * root cd /app && python manage.py send_batch_notifications >> /var/log/cron.log 2>&1
```

File must end with a newline (required by cron).

- [ ] **Step 2: Update `Dockerfile`**

Add `cron` to the `apt-get install` block:

```dockerfile
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    cron \
 && rm -rf /var/lib/apt/lists/*
```

After the `COPY . .` line, add:

```dockerfile
COPY docker/skal-cron /etc/cron.d/skal
RUN chmod 0644 /etc/cron.d/skal
```

- [ ] **Step 3: Update `entrypoint.sh`**

After the `mkdir -p /app/media` block, before the launch line, add:

```bash
echo "Starting cron daemon..."
service cron start
```

- [ ] **Step 4: Verify management command runs cleanly**

```bash
python manage.py send_batch_notifications
```

Expected: command completes with exit code 0, no tracebacks.

- [ ] **Step 5: Run full test suite**

```bash
pytest --tb=short -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add docker/skal-cron Dockerfile entrypoint.sh
git commit -m "feat: install cron in Docker and schedule daily batch notifications at 7am UTC"
```
