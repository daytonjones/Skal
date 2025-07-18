from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

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

