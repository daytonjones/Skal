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
