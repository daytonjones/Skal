from django.conf import settings


class TestVersionApi:
    def test_returns_version_with_no_auth(self, api_client):
        r = api_client.get("/api/v1/version/")
        assert r.status_code == 200
        assert r.data == {"version": settings.APP_VERSION}

    def test_also_works_with_valid_credentials(self, auth_api_client):
        r = auth_api_client.get("/api/v1/version/")
        assert r.status_code == 200
        assert r.data == {"version": settings.APP_VERSION}
