import inspect

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .test_case import ALL_TEST_CASE, DATA_INIT

User = get_user_model()


class TestSetup(APITestCase):
    app_name = None

    @property
    def f_name(self):
        """Get current func name."""
        func_name = inspect.currentframe().f_back.f_code.co_name
        return func_name if not self.app_name else f"{self.app_name}.{func_name}"

    @property
    def file_name(self):
        """Get current file name."""
        return inspect.getfile(inspect.currentframe().f_back)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in DATA_INIT.items():
            setattr(self, key, value)

    @property
    def refresh_token(self):
        refresh_token = RefreshToken.for_user(self.user)
        return refresh_token

    @property
    def access_token(self):
        return self.refresh_token.access_token

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            phone=self.phone,
            password=self.password,
        )
        self.user.create_user_profile()

    def run_test(
        self,
        method: str,
        path: str = None,
        path_name: str = None,
        request_body: dict = None,
        status_code: status = None,
        fields: list = None,
        format: str = "json",
        response_body: dict = None,
        is_authenticated: bool = True,
        is_detail: bool = False,
    ):
        """Run a single test case.

        Args:
            `method` (str): The HTTP method to use ["get", "post", "put", "patch", "delete"].
            `path` (str, optional): The URL path to test. Defaults to None.
            `path_name` (str, optional): The name of the URL path to test. Use reverse() to get the URL.
            `request_body` (dict, optional): The request payload. Defaults to None.
            `status_code` (status, optional): The expected HTTP status code. Defaults to None.
            `fields` (list, optional): The fields to check in the response. Defaults to None.
            `format` (str, optional): The format of the request. Defaults to "json".
            `response_body` (dict, optional): The expected response payload. Defaults to None.
            `is_authenticated` (bool, optional): Whether to include authentication token. Defaults to True.
            `is_detail` (bool, optional): Whether the request is for a detail view. Defaults to False.
        """
        url = path or reverse(path_name)
        self.assertIn(method, ["get", "post", "put", "patch", "delete"])

        if is_authenticated:
            self.client.credentials(
                HTTP_AUTHORIZATION=f"{settings.AUTH_HEADER_TYPE} {str(self.access_token)}"
            )

        response = getattr(self.client, method)(url, data=request_body, format=format)
        if status_code:
            self.assertEqual(response.status_code, status_code)
        if status_code < 200 or status_code == 204:
            return
        if bool(fields):
            self.assertEqual(True, hasattr(response, "data"))
            for field in fields:
                self.assertIn(field, response.data)
        if bool(response_body):
            obj_data = response.data
            if (
                not is_detail
                and "results" in response.data
                and status_code == status.HTTP_200_OK
            ):
                results = response.data["results"]
                self.assertIsInstance(results, list)
                self.assertGreaterEqual(len(results), 1)
                obj_data = results[0]
            for key, value in response_body.items():
                self.assertIn(key, obj_data)
                self.assertEqual(obj_data[key], value)

    def run_tests(
        self,
        func_name: str = "NoName",
        special_case: bool = False,
    ):
        """Run tests based on the provided function name and parameters.

        **Args**:
            `func_name` (str, optional): The name of the test function to run from `ALL_TEST_CASE`. Defaults to "NoName".
            `special_case` (bool, optional): Flag to indicate if this is a special case test. Defaults to False.
        Raises:
            ValueError: If the test case is not found.
        """
        obj = ALL_TEST_CASE.get(func_name)
        if bool(obj) and not special_case:
            test_cases = obj.get("test_case") or []
            path = obj.get("path")
            path_name = obj.get("path_name")
            method = str(obj.get("method")).lower()
            is_authenticated = obj.get("is_authenticated", True)
            is_detail = obj.get("is_detail", False)
            for case in test_cases:
                self.run_test(
                    method=method,
                    path=path,
                    path_name=path_name,
                    is_authenticated=is_authenticated,
                    is_detail=is_detail,
                    **case,
                )
        else:
            raise ValueError(f"Test case '{func_name}' not found.")
