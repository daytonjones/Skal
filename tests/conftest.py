import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testbrewer',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Brewer',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otherbrewer',
        email='other@example.com',
        password='testpass123',
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username='testbrewer', password='testpass123')
    return client
