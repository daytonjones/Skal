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
