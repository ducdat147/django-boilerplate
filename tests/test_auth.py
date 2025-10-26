from rest_framework import status

from tests.test_setup import TestSetup


class AuthTests(TestSetup):
    app_name = "auth"

    def test_register_user(self):
        self.run_tests(func_name=self.f_name)
        self.run_test(
            path=None,
            path_name="auth:token_obtain_pair",
            method="post",
            status_code=status.HTTP_200_OK,
            format="json",
            fields=["access", "refresh"],
            request_body={"username": "newusertest2", "password": "1StrongPassword!"},
            is_authenticated=False,
            is_detail=True,
        )

    def test_login(self):
        self.run_tests(func_name=self.f_name)

    def test_refresh_token(self):
        self.run_test(
            path=None,
            path_name="auth:token_refresh",
            method="post",
            status_code=status.HTTP_200_OK,
            format="json",
            fields=["access", "refresh"],
            request_body={"refresh": str(self.refresh_token)},
            is_authenticated=False,
            is_detail=True,
        )
        self.run_tests(func_name=self.f_name)
