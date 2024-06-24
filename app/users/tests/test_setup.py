from rest_framework.test import APITestCase

from users.models import MMTUser


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # create user, save user, login using client
        self.auth_email = "test_auth@test.com"
        self.auth_password = "test_auth1234"
        self.auth_first_name = "first_name_auth"
        self.auth_last_name = "last_name_auth"

        MMTUser.objects.create_user(self.auth_email,
                                    self.auth_password,
                                    first_name=self.auth_first_name,
                                    last_name=self.auth_last_name,
                                    is_superuser=True)
        self.auth_user = MMTUser.objects.get(email=self.auth_email)

        self.email = "test@test.com"
        self.password = "test1234"
        self.first_name = "Jill"
        self.last_name = "doe"
        self.userDict = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
        self.userDict_login = {
            "username": self.email,
            "password": self.password
        }

        self.userDict_login_fail = {
            "username": "test@test.com",
            "password": "test"
        }

        self.userDict_login_fail_no_username = {
            "password": "test"
        }

        self.userDict_login_fail_no_password = {
            "username": "test@test.com"
        }

        self.user_1_email = "test3@test.com"
        self.user_1_password = "1234"

        self.user_1 = MMTUser.objects.create_user(self.user_1_email,
                                                  self.user_1_password,
                                                  first_name="john",
                                                  last_name="doe")
        self.user_2 = MMTUser.objects.create_user('test2@test.com',
                                                  'test1234',
                                                  first_name='Jane',
                                                  last_name='doe')

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
