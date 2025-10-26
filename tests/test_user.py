from tests.test_setup import TestSetup


class UserTests(TestSetup):
    app_name = "user"

    def test_profile(self):
        self.run_tests(func_name=self.f_name)

    def test_update_profile(self):
        self.run_tests(func_name=self.f_name)

    def test_reset_password(self):
        self.run_tests(func_name=self.f_name)
