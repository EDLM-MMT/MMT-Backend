# from unittest.mock import patch

import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.date = datetime.date(1997, 10, 19)
        self.text = " text goes here"
        self.email = "admin@example.com"
        self.file_field = SimpleUploadedFile("best_file_eva.txt",
                                             b"file_content")

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
