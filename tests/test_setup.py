from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from core.user.models import User
from .test_case import ALL_TEST_CASE, DATA_INIT


class TestSetup(APITestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in DATA_INIT.items():
            setattr(self, key, value)

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def _run_test(
        self,
        method: str,
        url: str,
        request_body: dict = None,
        status_code: status = None,
        fields: list = None,
        format: str = "json",
        response_body: dict = None,
    ):
        self.assertIn(method, ["get", "post", "put", "patch", "delete"])
        response = getattr(self.client, method)(url, data=request_body, format=format)
        if status_code:
            self.assertEqual(response.status_code, status_code)
        if status_code < 200 or status_code >= 300:
            return
        if bool(fields):
            self.assertEqual(True, hasattr(response, "data"))
            for field in fields:
                self.assertIn(field, response.data)
        if bool(response_body):
            for key, value in response_body.items():
                self.assertIn(key, response.data)
                self.assertEqual(response.data[key], value)

    def run_tests(self, func_name: str):
        obj = ALL_TEST_CASE.get(func_name)
        if not obj:
            raise ValueError(f"Test case '{func_name}' not found.")
        test_cases = obj.get("test_case") or []
        path_name = obj.get("path_name")
        method = obj.get("method")
        for case in test_cases:
            self._run_test(
                method=method,
                url=str(path_name).lower(),
                request_body=case.get("request_body"),
                status_code=case.get("status_code"),
                fields=case.get("fields") or [],
                format=case.get("format") or "json",
                response_body=case.get("response_body") or {},
            )
