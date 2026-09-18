import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_api_client(api_client, user):
    # The shared `user` fixture is created unapproved (User.is_approved defaults
    # to False). The API enforces the same admin-approval gate as the web app,
    # so an API-authenticated actor must be approved.
    user.is_approved = True
    user.save()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def approved_user(user):
    """The shared `user` fixture, approved — for tests that log in via /auth/token/."""
    user.is_approved = True
    user.save()
    return user
