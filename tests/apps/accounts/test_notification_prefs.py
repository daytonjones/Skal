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
