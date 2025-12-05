"""
Integration tests for authentication flow.

These tests verify the complete authentication workflow.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_complete_registration_login_flow(self, api_client, db):
        """Test user can register and then login successfully."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Step 1: Register a new user
        register_url = reverse("auth:register")
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "phone": "+84369000001",
        }

        register_response = api_client.post(register_url, register_data, format="json")

        assert register_response.status_code == status.HTTP_201_CREATED
        assert "access" in register_response.data
        assert "refresh" in register_response.data

        # Verify user was created
        assert User.objects.filter(username="newuser").exists()
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@example.com"

        # Step 2: Login with the created credentials
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": "newuser", "password": "SecurePass123!"}

        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data
        assert "refresh" in login_response.data

        # Step 3: Access protected resource with token
        access_token = login_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        profile_url = reverse("user:my_profile")
        profile_response = api_client.get(profile_url)

        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data["username"] == "newuser"
        assert profile_response.data["email"] == "newuser@example.com"

    def test_token_refresh_flow(self, api_client, verified_user):
        """Test token refresh functionality."""
        # Step 1: Get initial tokens via login
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": verified_user.username, "password": "testpass123"}

        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data["refresh"]
        old_access_token = login_response.data["access"]

        # Step 2: Refresh the access token
        refresh_url = reverse("auth:token_refresh")
        refresh_data = {"refresh": refresh_token}

        refresh_response = api_client.post(refresh_url, refresh_data, format="json")

        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access" in refresh_response.data
        new_access_token = refresh_response.data["access"]

        # Verify we got a different access token
        assert new_access_token != old_access_token

        # Step 3: Use new access token to access protected resource
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")

        profile_url = reverse("user:my_profile")
        profile_response = api_client.get(profile_url)

        assert profile_response.status_code == status.HTTP_200_OK

    def test_invalid_credentials_flow(self, api_client, user):
        """Test login with invalid credentials."""
        login_url = reverse("auth:token_obtain_pair")

        # Wrong password
        login_data = {"username": user.username, "password": "wrongpassword"}
        response = api_client.post(login_url, login_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Wrong username
        login_data = {"username": "nonexistent", "password": "testpass123"}
        response = api_client.post(login_url, login_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_registration_validation_flow(self, api_client, db):
        """Test registration with invalid data."""
        register_url = reverse("auth:register")

        # Weak password
        weak_pass_data = {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "weak",
            "phone": "+84369000002",
        }
        response = api_client.post(register_url, weak_pass_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Invalid email
        invalid_email_data = {
            "username": "testuser2",
            "email": "invalid-email",
            "password": "SecurePass123!",
            "phone": "+84369000003",
        }
        response = api_client.post(register_url, invalid_email_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
class TestUserProfileFlow:
    """Test complete user profile management flow."""

    def test_profile_update_and_retrieval_flow(self, authenticated_client, verified_user):
        """Test updating profile and retrieving updated data."""
        profile_url = reverse("user:my_profile")

        # Step 1: Get initial profile
        initial_response = authenticated_client.get(profile_url)
        assert initial_response.status_code == status.HTTP_200_OK
        initial_email = initial_response.data["email"]

        # Step 2: Update profile
        update_data = {
            "email": "updated@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone": "+84369000100",
        }

        update_response = authenticated_client.put(profile_url, update_data, format="json")
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["email"] == "updated@example.com"
        assert update_response.data["first_name"] == "Updated"

        # Step 3: Retrieve updated profile
        final_response = authenticated_client.get(profile_url)
        assert final_response.status_code == status.HTTP_200_OK
        assert final_response.data["email"] == "updated@example.com"
        assert final_response.data["email"] != initial_email

    def test_password_reset_and_login_flow(self, api_client, user):
        """Test password reset and login with new password."""
        # Step 1: Login with old password
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": user.username, "password": "testpass123"}

        login_response = api_client.post(login_url, login_data, format="json")
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data["access"]

        # Step 2: Reset password
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        reset_url = reverse("user:reset_password")
        reset_data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePass123!",
        }

        reset_response = api_client.post(reset_url, reset_data, format="json")
        assert reset_response.status_code == status.HTTP_204_NO_CONTENT

        # Step 3: Cannot login with old password
        api_client.credentials()  # Clear credentials
        old_login_response = api_client.post(login_url, login_data, format="json")
        assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED

        # Step 4: Login with new password
        new_login_data = {"username": user.username, "password": "NewSecurePass123!"}
        new_login_response = api_client.post(login_url, new_login_data, format="json")
        assert new_login_response.status_code == status.HTTP_200_OK
        assert "access" in new_login_response.data


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteUserJourney:
    """Test complete user journey from registration to profile management."""

    def test_full_user_journey(self, api_client, db):
        """Test complete user journey."""
        # Step 1: Register
        register_url = reverse("auth:register")
        register_data = {
            "username": "journeyuser",
            "email": "journey@example.com",
            "password": "SecurePass123!",
            "phone": "+84369000200",
        }
        register_response = api_client.post(register_url, register_data, format="json")
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": "journeyuser", "password": "SecurePass123!"}
        login_response = api_client.post(login_url, login_data, format="json")
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data["access"]

        # Step 3: View profile
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_url = reverse("user:my_profile")
        profile_response = api_client.get(profile_url)
        assert profile_response.status_code == status.HTTP_200_OK

        # Step 4: Update profile
        update_data = {
            "first_name": "Journey",
            "last_name": "User",
            "phone": "+84369000201",
        }
        update_response = api_client.patch(profile_url, update_data, format="json")
        assert update_response.status_code == status.HTTP_200_OK

        # Step 5: Change password
        reset_url = reverse("user:reset_password")
        reset_data = {
            "old_password": "SecurePass123!",
            "new_password": "NewJourneyPass123!",
        }
        reset_response = api_client.post(reset_url, reset_data, format="json")
        assert reset_response.status_code == status.HTTP_204_NO_CONTENT

        # Step 6: Login with new password
        api_client.credentials()
        new_login_data = {"username": "journeyuser", "password": "NewJourneyPass123!"}
        final_login_response = api_client.post(login_url, new_login_data, format="json")
        assert final_login_response.status_code == status.HTTP_200_OK
