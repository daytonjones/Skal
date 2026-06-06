from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_approved', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    theme = models.CharField(
        max_length=20,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="dark",
    )
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                previous = User.objects.get(pk=self.pk)
                if not previous.is_approved and self.is_approved:
                    self._send_approval_email()
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def _send_approval_email(self):
        if not self.email:
            return
        import logging
        from django.core.mail import send_mail
        from django.conf import settings
        logger = logging.getLogger(__name__)
        name = self.get_full_name() or self.username
        hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        host = next((h for h in hosts if h not in ('*', '', 'localhost', '127.0.0.1')), None)
        login_hint = f"http://{host}" if host else "your Skål instance"
        try:
            send_mail(
                subject="Your Skål account has been approved",
                message=(
                    f"Hi {name},\n\n"
                    f"Your Skål account has been approved — you can now log in at {login_hint}.\n\n"
                    f"Skål! 🍯"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
            )
        except Exception as exc:
            logger.error("Failed to send approval email to %s: %s", self.email, exc)

    def __str__(self):
        return self.username

