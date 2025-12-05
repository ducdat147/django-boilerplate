"""
Test mixins for reusable test functionality.
"""

from rest_framework import status


class APITestMixin:
    """Mixin for common API test assertions."""

    def assert_response_keys(self, response, expected_keys):
        """Assert response contains all expected keys."""
        for key in expected_keys:
            assert key in response.data, f"Key '{key}' not found in response data"

    def assert_response_excludes_keys(self, response, excluded_keys):
        """Assert response does not contain specified keys."""
        for key in excluded_keys:
            assert key not in response.data, f"Key '{key}' should not be in response data"

    def assert_paginated_response(self, response):
        """Assert response is properly paginated."""
        assert "count" in response.data, "Missing 'count' in paginated response"
        assert "next" in response.data, "Missing 'next' in paginated response"
        assert "previous" in response.data, "Missing 'previous' in paginated response"
        assert "results" in response.data, "Missing 'results' in paginated response"
        assert isinstance(response.data["results"], list), "'results' should be a list"

    def assert_validation_error(self, response, field=None):
        """Assert response is a validation error."""
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        if field:
            assert field in response.data, f"Field '{field}' not in error response"


class CRUDTestMixin(APITestMixin):
    """
    Mixin for testing CRUD operations.

    Subclasses should define:
    - model: The Django model class
    - factory: Factory class for creating test instances
    - list_url: URL for list endpoint
    - detail_url_name: URL name for detail endpoint
    - serializer_class: Serializer class for the model
    """

    model = None
    factory = None
    list_url = None
    detail_url_name = None
    serializer_class = None

    def get_detail_url(self, obj):
        """Get detail URL for an object."""
        from django.urls import reverse

        return reverse(self.detail_url_name, kwargs={"pk": obj.pk})

    def test_list_success(self, authenticated_client):
        """Test listing objects successfully."""
        # Create some test objects
        if self.factory:
            self.factory.create_batch(3)

        response = authenticated_client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        self.assert_paginated_response(response)
        assert len(response.data["results"]) >= 3

    def test_list_unauthenticated(self, api_client):
        """Test listing objects without authentication."""
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self, authenticated_client):
        """Test retrieving a single object successfully."""
        obj = self.factory()
        url = self.get_detail_url(obj)

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == obj.pk

    def test_retrieve_not_found(self, authenticated_client):
        """Test retrieving non-existent object returns 404."""
        from django.urls import reverse

        url = reverse(self.detail_url_name, kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_success(self, authenticated_client, valid_create_payload):
        """Test creating an object successfully."""
        initial_count = self.model.objects.count()

        response = authenticated_client.post(self.list_url, valid_create_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert self.model.objects.count() == initial_count + 1
        assert self.model.objects.filter(pk=response.data["id"]).exists()

    def test_create_invalid_data(self, authenticated_client, invalid_create_payload):
        """Test creating an object with invalid data."""
        initial_count = self.model.objects.count()

        response = authenticated_client.post(self.list_url, invalid_create_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.model.objects.count() == initial_count

    def test_update_success(self, authenticated_client, valid_update_payload):
        """Test updating an object successfully."""
        obj = self.factory()
        url = self.get_detail_url(obj)

        response = authenticated_client.put(url, valid_update_payload)

        assert response.status_code == status.HTTP_200_OK
        obj.refresh_from_db()

    def test_partial_update_success(self, authenticated_client, valid_partial_payload):
        """Test partially updating an object successfully."""
        obj = self.factory()
        url = self.get_detail_url(obj)

        response = authenticated_client.patch(url, valid_partial_payload)

        assert response.status_code == status.HTTP_200_OK

    def test_delete_success(self, authenticated_client):
        """Test deleting an object successfully."""
        obj = self.factory()
        url = self.get_detail_url(obj)

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not self.model.objects.filter(pk=obj.pk).exists()


class PermissionTestMixin:
    """Mixin for testing permissions."""

    def assert_requires_authentication(self, client, method, url, data=None):
        """Assert endpoint requires authentication."""
        request_method = getattr(client, method)
        response = request_method(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def assert_requires_admin(self, client, method, url, data=None):
        """Assert endpoint requires admin privileges."""
        request_method = getattr(client, method)
        response = request_method(url, data=data)
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ]


class PerformanceTestMixin:
    """Mixin for performance testing."""

    def assert_query_count(self, django_assert_num_queries, expected_count, callable):
        """Assert query count matches expected."""
        with django_assert_num_queries(expected_count):
            callable()

    def assert_max_query_count(self, django_assert_max_num_queries, max_count, callable):
        """Assert query count doesn't exceed maximum."""
        with django_assert_max_num_queries(max_count):
            callable()
