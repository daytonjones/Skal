# Batch Notifications — Design Spec
**Date:** 2026-06-09
**Branch:** v2_2
**Status:** Approved

## Goal

Send opt-in email reminders to users on the day a brewing event is due — TOSNA nutrient additions, a 1/3 sugar break gravity check prompt, racking to secondary, and bottling. One daily digest email per user covers all due events across all active batches.

## Approach

Management command (`send_batch_notifications`) run via cron in the Docker container, firing at 7am UTC daily. Matches the existing `send_ai_report.py` pattern. Zero new dependencies.

---

## User Preferences

New model `UserNotificationPrefs` in `apps/accounts/models.py` — one-to-one with `User`, created on demand via `get_or_create`.

```python
class UserNotificationPrefs(models.Model):
    user                = OneToOneField(User, on_delete=CASCADE, related_name='notification_prefs')
    email_notifications = BooleanField(default=False)   # master switch — fully opt-in
    notify_tosna        = BooleanField(default=True)    # 24h / 48h / 72h additions
    notify_sg_check     = BooleanField(default=True)    # 1/3 sugar break gravity reminder
    notify_rack         = BooleanField(default=False)   # rack to secondary
    notify_bottle       = BooleanField(default=False)   # bottling day
```

`email_notifications=False` by default — users must explicitly opt in. Per-event fields default to True (for TOSNA/SG) or False (for rack/bottle) so that a new opt-in user gets sensible defaults.

### Profile UI

The existing profile page (`/accounts/profile/`) gains a **Notifications** section:
- Master toggle: "Email me brewing reminders"
- Four per-event checkboxes, only active when master toggle is on:
  - Nutrient additions (TOSNA 24h / 48h / 72h)
  - Gravity check reminder (~day 4)
  - Rack to secondary (requires target date set on batch)
  - Bottling day (requires target date set on batch)

The profile view handles two forms: the existing `ProfileForm` (User fields) and a new `NotificationPrefsForm` (ModelForm for `UserNotificationPrefs`). The view calls `get_or_create` on `UserNotificationPrefs` for the current user before rendering, so the prefs object always exists.

---

## Notification Event Logic

Events are computed for each active batch (where `bottled_done=False`). Implemented as a standalone function `get_due_events(batch, prefs, today)` → `list[str]` of human-readable event labels. Pure function — no DB calls — makes it fully unit-testable.

| Event | Condition | Due date | Skip when |
|---|---|---|---|
| TOSNA 24h addition | `notify_tosna=True` and `pitch_yeast_date` set | `pitch_yeast_date + 1 day` | `fo_24h_done` |
| TOSNA 48h addition | `notify_tosna=True` and `pitch_yeast_date` set | `pitch_yeast_date + 2 days` | `fo_48h_done` |
| TOSNA 72h addition | `notify_tosna=True` and `pitch_yeast_date` set | `pitch_yeast_date + 3 days` | `fo_72h_done` |
| SG check (1/3 break) | `notify_sg_check=True` and `pitch_yeast_date` set | `pitch_yeast_date + 4 days` | `fo_1_3_break_done` |
| Rack to secondary | `notify_rack=True` and `secondary_date` set | `secondary_date` | `rack_secondary_done` |
| Bottling day | `notify_bottle=True` and `bottling_date` set | `bottling_date` | `bottled_done` |

Batches with no `pitch_yeast_date` are skipped for TOSNA/SG events. Rack/bottle events only fire if the respective target date is set on the batch.

---

## Management Command

**Location:** `apps/batches/management/commands/send_batch_notifications.py`

**Logic:**
1. Query users where `notification_prefs__email_notifications=True` and `email` non-empty
2. For each user, get active batches (`bottled_done=False`)
3. For each batch, call `get_due_events(batch, prefs, today)`
4. If any events are due across any batches, send one digest email
5. Log each send and each skip; swallow send errors with `logger.error` (same pattern as `send_ai_report.py`)

**Email:**
- Subject: `Skål — Brewing reminders for [date]`
- Body: plain-text + HTML template at `templates/batches/email/batch_notifications.html`
- Lists each batch with due events as a simple grouped list
- Footer: "Manage your notification preferences at [profile URL]"

---

## Docker Cron Setup

**Dockerfile** — install `cron`, copy crontab file:
```dockerfile
RUN apt-get install -y cron
COPY docker/skal-cron /etc/cron.d/skal
RUN chmod 0644 /etc/cron.d/skal
```

**`docker/skal-cron`:**
```
0 7 * * * root cd /app && python manage.py send_batch_notifications >> /var/log/cron.log 2>&1
```

**`entrypoint.sh`** — start cron before gunicorn:
```bash
service cron start
```

---

## Files Changed / Created

| File | Action |
|---|---|
| `apps/accounts/models.py` | Add `UserNotificationPrefs` model |
| `apps/accounts/migrations/` | New migration |
| `apps/accounts/forms.py` | Extend profile form with notification prefs fields |
| `apps/accounts/views.py` | Handle `UserNotificationPrefs` get_or_create on profile save |
| `templates/accounts/profile.html` | Add Notifications section |
| `apps/batches/management/commands/send_batch_notifications.py` | New management command |
| `apps/batches/notifications.py` | `get_due_events()` pure function |
| `templates/batches/email/batch_notifications.html` | Email template |
| `templates/batches/email/batch_notifications.txt` | Plain-text email template |
| `docker/skal-cron` | Crontab file |
| `Dockerfile` | Install cron, copy crontab |
| `entrypoint.sh` | Start cron service |
| `tests/apps/accounts/test_notification_prefs.py` | Model + form tests |
| `tests/apps/batches/test_notifications.py` | `get_due_events()` unit tests + command tests |

---

## Testing

### `get_due_events()` (pure function — no DB)
- Each event type fires on the correct date
- Each event type is skipped when `_done=True`
- TOSNA/SG events skipped when `pitch_yeast_date=None`
- Rack/bottle events skipped when target date not set
- Per-event prefs respected (e.g., `notify_rack=False` suppresses rack event)

### Management command (mocked `send_mail`)
- User with `email_notifications=True` and due events → email sent
- User with `email_notifications=False` → no email
- User with no email address → skipped
- User with no due events today → no email
- `send_mail` exception → logged, does not crash command

### Profile form
- `UserNotificationPrefs` created with defaults on first profile save
- Saving form with `email_notifications=False` persists correctly
- Per-event fields save and render correctly
