# from unittest.mock import patch
from pathlib import Path

from django.test import override_settings
from rest_framework.test import APITestCase

from academic_institute.models import AcademicInstitute
from users.models import MMTUser, UserRecord


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        # settings management
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

        self.c_institute = "institute1"
        self.uname = "username"
        self.email = "test@test.com"
        self.password = "password"
        self.user = MMTUser.objects.create_user(
            password=self.password, email=self.email)
        self.ur = UserRecord(user_profile=self.user, email=self.email)
        self.institute = AcademicInstitute(institute=self.c_institute)

        self.file = Path().joinpath("/tmp", "imports", "test.csv").absolute()
        self.file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.file, 'w', encoding="utf-8") as f:
            f.write("FirstName,LastName,Email,Name\n")
            f.write("John,Smith,js@example.com,Fake University\n")

        return super().setUp()

    def tearDown(self):
        """Remove temp file when completed"""
        self.file.unlink(missing_ok=True)
        return super().tearDown()
