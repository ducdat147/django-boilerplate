from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from tests.test_setup import TestSetup


class AuthTests(TestSetup):
    def test_register_user(self):
        self.run_tests(func_name="test_auth.test_register_user")
        self.run_tests(func_name="test_auth.test_register_user__login")

    def test_login(self):
        self.run_tests(func_name="test_auth.test_login")

    def test_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.run_tests(
            special_case=True,
            path_name="token-refresh",
            method="post",
            status_code=status.HTTP_200_OK,
            format="json",
            fields=["access", "refresh"],
            request_body={"refresh": str(refresh)},
        )
        self.run_tests("test_auth.test_refresh_token__invalid")

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)
        self.run_tests(
            special_case=True,
            path_name="auth-logout",
            method="post",
            status_code=status.HTTP_204_NO_CONTENT,
            format="json",
            request_body={"refresh": str(refresh)},
        )
        self.run_tests(
            special_case=True,
            path_name="auth-logout",
            method="post",
            status_code=status.HTTP_400_BAD_REQUEST,
            format="json",
            request_body={"refresh": str(refresh)},
        )
