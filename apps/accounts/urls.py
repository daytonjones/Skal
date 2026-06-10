# apps/accounts/urls.py
from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    SignUpView,
    ProfileUpdateView,
    CustomPasswordChangeView,
    export_user_data,
    toggle_theme,
    save_notification_prefs,
)

app_name = "accounts"

urlpatterns = [
    path("login/",  CustomLoginView.as_view(),          name="login"),
    path("logout/", CustomLogoutView.as_view(),         name="logout"),
    path("signup/", SignUpView.as_view(),               name="signup"),
    path("profile/", ProfileUpdateView.as_view(),       name="profile"),
    path("password/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("export/", export_user_data,                   name="export_user_data"),
    path("theme/toggle/", toggle_theme,                 name="toggle_theme"),
    path("profile/notifications/", save_notification_prefs, name="save_notification_prefs"),
]

