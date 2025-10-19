from tests.test_setup import TestSetup


class UserTests(TestSetup):
    def test_profile(self):
        self.run_tests(func_name="test_user.test_profile")

    def test_update_profile(self):
        self.run_tests(func_name="test_user.test_update_profile")

    def test_reset_password(self):
        self.run_tests(func_name="test_user.test_reset_password")
