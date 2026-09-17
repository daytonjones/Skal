from apps.yeast.views import YEASTS


class TestYeastApi:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/yeast/")
        assert r.status_code == 401

    def test_returns_full_list(self, auth_api_client):
        r = auth_api_client.get("/api/v1/yeast/")
        assert r.status_code == 200
        assert len(r.data) == len(YEASTS)
        assert r.data[0]["name"] == YEASTS[0]["name"]
