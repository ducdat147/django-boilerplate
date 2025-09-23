from tests.test_setup import TestSetup


class AuthTests(TestSetup):
    def test_register_user(self):
        self.run_tests(func_name="test_auth.test_register_user")

    def test_login(self):
        self.run_tests(func_name="test_auth.test_login")
