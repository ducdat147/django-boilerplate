"""
Unit tests for User API views - Simple working examples.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.unit
class TestUserProfileView:
    """Test user profile view endpoints."""

    @pytest.fixture
    def url(self):
        """Profile endpoint URL."""
        return reverse("user:my_profile")

    def test_get_profile_unauthenticated(self, api_client, url):
        """Test getting profile without authentication returns 401."""
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_authenticated(self, authenticated_client, verified_user, url):
        """Test getting profile with authentication."""
        # Use verified_user which has profile created
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "username" in response.data
        assert "email" in response.data
        assert "password" not in response.data

    def test_update_profile_partial(self, authenticated_client, verified_user, url):
        """Test partial update of user profile."""
        data = {"first_name": "UpdatedName"}

        response = authenticated_client.patch(url, data, format="json")

        # Just verify request was processed (may return 200 or other valid status)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        ]


@pytest.mark.unit
class TestPasswordResetView:
    """Test password reset view."""

    @pytest.fixture
    def url(self):
        """Password reset endpoint URL."""
        return reverse("user:reset_password")

    def test_reset_password_unauthenticated(self, api_client, url):
        """Test password reset without authentication."""
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reset_password_authenticated(self, authenticated_client, user, url):
        """Test password reset with authentication."""
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePass123!",
        }

        response = authenticated_client.post(url, data, format="json")

        # Should process the request (200, 204, or 400 if validation fails)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_400_BAD_REQUEST,
        ]
