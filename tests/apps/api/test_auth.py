from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


class TestTokenObtain:
    def test_valid_credentials_returns_tokens(self, api_client, approved_user):
        r = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testbrewer", "password": "testpass123"},
        )
        assert r.status_code == 200
        assert "access" in r.data
        assert "refresh" in r.data

    def test_invalid_credentials_rejected(self, api_client, user):
        r = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testbrewer", "password": "wrongpass"},
        )
        assert r.status_code == 401

    def test_unapproved_user_cannot_obtain_token(self, api_client, user):
        # The shared `user` fixture is unapproved; the API must enforce the same
        # admin-approval gate the web login does (apps/accounts/views.py).
        assert user.is_approved is False
        r = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testbrewer", "password": "testpass123"},
        )
        assert r.status_code == 400
        assert "access" not in r.data

    def test_unapproved_user_cannot_use_api_even_when_authenticated(self, api_client, user):
        # Defense in depth: even with a session/token for an unapproved user,
        # resource endpoints must refuse.
        api_client.force_authenticate(user=user)
        r = api_client.get("/api/v1/recipes/")
        assert r.status_code == 403


class TestTokenRefreshAndLogout:
    """The global IsApproved default must not break simplejwt's own views."""

    def _refresh_token(self, api_client):
        r = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testbrewer", "password": "testpass123"},
        )
        assert r.status_code == 200
        return r.data["refresh"]

    def test_refresh_returns_new_access(self, api_client, approved_user):
        refresh = self._refresh_token(api_client)
        r = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh})
        assert r.status_code == 200
        assert "access" in r.data

    def test_logout_blacklists_refresh(self, api_client, approved_user):
        refresh = self._refresh_token(api_client)
        r = api_client.post("/api/v1/auth/token/logout/", {"refresh": refresh})
        assert r.status_code == 200
        # The blacklisted token can no longer be refreshed.
        r = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh})
        assert r.status_code == 401


class TestRegister:
    def test_register_creates_user(self, api_client, db):
        r = api_client.post(
            "/api/v1/auth/register/",
            {"username": "newbrewer", "email": "new@example.com", "password": "newpass123"},
        )
        assert r.status_code == 201
        user = User.objects.get(username="newbrewer")
        assert user.is_approved is False

    def test_register_rejects_short_password(self, api_client, db):
        r = api_client.post(
            "/api/v1/auth/register/",
            {"username": "newbrewer", "password": "short"},
        )
        assert r.status_code == 400

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ]
    )
    def test_register_rejects_common_password(self, api_client, db):
        # Django's password validators reject weak passwords (e.g., all numeric)
        r = api_client.post(
            "/api/v1/auth/register/",
            {"username": "newbrewer", "email": "new@example.com", "password": "12345678"},
        )
        assert r.status_code == 400
        assert "password" in r.data["password"][0].lower()

    def test_register_accepts_strong_password(self, api_client, db):
        # A strong, uncommon password should pass all validators
        r = api_client.post(
            "/api/v1/auth/register/",
            {"username": "newbrewer", "email": "new@example.com", "password": "MyStr0ng!Pwd"},
        )
        assert r.status_code == 201
        user = User.objects.get(username="newbrewer")
        assert user.is_approved is False


class TestMe:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/auth/me/")
        assert r.status_code == 401

    def test_returns_profile(self, auth_api_client, user):
        r = auth_api_client.get("/api/v1/auth/me/")
        assert r.status_code == 200
        assert r.data["username"] == "testbrewer"

    def test_updates_theme(self, auth_api_client, user):
        r = auth_api_client.patch("/api/v1/auth/me/", {"theme": "light"}, format="json")
        assert r.status_code == 200
        user.refresh_from_db()
        assert user.theme == "light"
