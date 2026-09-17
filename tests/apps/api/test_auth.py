from django.contrib.auth import get_user_model

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
