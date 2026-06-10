from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, UserNotificationPrefs

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First name")
    last_name = forms.CharField(max_length=150, required=True, label="Last name")
    email = forms.EmailField(required=True, label="Email address")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "theme")
        widgets = {
            "theme": forms.RadioSelect(choices=User._meta.get_field("theme").choices)
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    # inherits old_password, new_password1, new_password2
    pass


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

