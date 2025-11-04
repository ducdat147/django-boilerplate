"""
Pytest configuration and shared fixtures.
"""

import os

import django
import pytest

# Setup Django settings before any tests run
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configurations.settings.local")
django.setup()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user(db):
    """Create a basic user for testing."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        phone="+84369000000",
        password="testpass123",
    )


@pytest.fixture
def verified_user(user):
    """Create a verified user with profile."""
    user.is_email_verified = True
    user.is_phone_verified = True
    user.save()
    user.create_user_profile()
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated admin client."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests automatically."""
    pass


@pytest.fixture
def mock_celery(mocker):
    """Mock Celery tasks to prevent actual task execution in tests."""
    return mocker.patch("celery.app.task.Task.apply_async")


@pytest.fixture
def mock_email(mocker):
    """Mock email sending."""
    return mocker.patch("django.core.mail.send_mail")
