import pytest
from django.test import override_settings
from django.urls import reverse


@pytest.mark.django_db
class TestMobileAppDownloadView:
    def test_requires_login(self, client):
        response = client.get(reverse('accounts:mobile_app'))
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_no_apk_uploaded(self, auth_client, tmp_path):
        with override_settings(MEDIA_ROOT=tmp_path):
            response = auth_client.get(reverse('accounts:mobile_app'))
        assert response.status_code == 200
        assert response.context['apk_exists'] is False
        assert response.context['download_url'] is None
        assert response.context['qr_data_uri'] is None
        assert b'No build has been uploaded yet' in response.content

    def test_apk_uploaded(self, auth_client, tmp_path):
        downloads_dir = tmp_path / 'downloads'
        downloads_dir.mkdir(parents=True)
        apk_path = downloads_dir / 'skal-latest.apk'
        apk_path.write_bytes(b'fake apk contents')

        with override_settings(MEDIA_ROOT=tmp_path):
            response = auth_client.get(reverse('accounts:mobile_app'))

        assert response.status_code == 200
        assert response.context['apk_exists'] is True
        assert response.context['download_url'] is not None
        assert 'downloads/skal-latest.apk' in response.context['download_url']
        assert response.context['qr_data_uri'].startswith('data:image/png;base64,')
        assert response.context['file_size'] is not None
