import datetime

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from users.models import MMTUser, UserRecord
from inquiry.models import InquiryFAQ


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.date = datetime.date(1997, 10, 19)
        self.text = " text goes here"
        self.email = "admin@example.com"
        self.uname = "username"
        self.response = "response"
        self.status = "Active"
        self.user = MMTUser.objects.create_user(self.uname, "password")
        self.ur = UserRecord(user_profile=self.user, email=self.email)
        self.file_field = SimpleUploadedFile("best_file_eva.txt",
                                             b"file_content")
        self.group = Group.objects.create(name='Support')
        self.valid_text = "ValidText123"
        self.faq = InquiryFAQ.objects.create(
            issue=self.valid_text,
            response=self.valid_text,
            default_assigned=self.group,
            status='Active'
        )

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
