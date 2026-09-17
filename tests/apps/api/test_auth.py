from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


class TestTokenObtain:
    def test_valid_credentials_returns_tokens(self, api_client, user):
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
