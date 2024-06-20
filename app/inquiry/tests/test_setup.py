# from unittest.mock import patch

import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from users.models import MMTUser, UserRecord


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.date = datetime.date(1997, 10, 19)
        self.text = " text goes here"
        self.email = "admin@example.com"
        self.uname = "username"
        self.user = MMTUser.objects.create_user(self.uname, "password")
        self.ur = UserRecord(user_profile=self.user, email=self.email)
        self.file_field = SimpleUploadedFile("best_file_eva.txt",
                                             b"file_content")

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
