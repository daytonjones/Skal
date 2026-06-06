import logging
from collections import defaultdict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.ai.models import AIUsage

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Send weekly Bjorn AI usage report to admin users'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7,
                            help='Number of days to include in the report (default: 7)')

    def handle(self, *args, **options):
        days = options['days']
        since = timezone.now() - timedelta(days=days)

        usages = AIUsage.objects.filter(created_at__gte=since).select_related('user')
        if not usages.exists():
            self.stdout.write(f'No Bjorn AI usage in the past {days} days — skipping report.')
            return

        stats = defaultdict(lambda: {'messages': 0, 'input_tokens': 0, 'output_tokens': 0})
        provider = ''
        model = ''
        for u in usages:
            stats[u.user.username]['messages'] += 1
            stats[u.user.username]['input_tokens'] += u.input_tokens
            stats[u.user.username]['output_tokens'] += u.output_tokens
            provider = u.provider
            model = u.model

        total_msg = sum(s['messages'] for s in stats.values())
        total_in = sum(s['input_tokens'] for s in stats.values())
        total_out = sum(s['output_tokens'] for s in stats.values())

        date_from = since.strftime('%b %-d')
        date_to = timezone.now().strftime('%b %-d, %Y')

        rows = '\n'.join(
            f"  {uname:<20} {s['messages']:>8}   {s['input_tokens']:>10,}   {s['output_tokens']:>10,}"
            for uname, s in sorted(stats.items(), key=lambda x: -x[1]['messages'])
        )

        body = (
            f"Bjorn AI Usage Report — {date_from}–{date_to}\n"
            f"{'─' * 62}\n\n"
            f"  {'User':<20} {'Messages':>8}   {'Tokens In':>10}   {'Tokens Out':>10}\n"
            f"  {'─' * 20} {'─' * 8}   {'─' * 10}   {'─' * 10}\n"
            f"{rows}\n"
            f"  {'─' * 20} {'─' * 8}   {'─' * 10}   {'─' * 10}\n"
            f"  {'Total':<20} {total_msg:>8}   {total_in:>10,}   {total_out:>10,}\n\n"
            f"Provider: {provider} ({model})\n\n"
            f"Skål! 🍯"
        )

        admin_emails = list(
            User.objects.filter(is_staff=True)
            .exclude(email='')
            .values_list('email', flat=True)
        )
        if not admin_emails:
            self.stdout.write('No admin emails configured — skipping report.')
            return

        try:
            send_mail(
                subject=f"Skål — Bjorn AI usage ({date_from}–{date_to})",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
            )
            self.stdout.write(f'AI usage report sent to: {", ".join(admin_emails)}')
        except Exception as exc:
            logger.error("Failed to send AI usage report: %s", exc)
            self.stdout.write(f'Failed to send report: {exc}')
