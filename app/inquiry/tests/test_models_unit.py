from django.test import tag
from inquiry.models import Inquiry, InquiryComment, InquiryFAQ

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_inquiry_FAQ(self):
        issue = InquiryFAQ(issue=self.text)
        response = InquiryFAQ(response=self.text)

        self.assertEqual(self.text, issue.issue)
        self.assertEqual(self.text, response.response)

    def test_create_inquiry(self):
        email = Inquiry(email=self.email)
        name = Inquiry(name=self.text)
        description = Inquiry(description=self.text)
        subject = Inquiry(subject=self.text)
        file = Inquiry(file=self.file_field)

        self.assertEqual(self.email, email.email)
        self.assertEqual(self.text, name.name)
        self.assertEqual(self.text, description.description)
        self.assertEqual(self.text, subject.subject)
        self.assertTrue(file.file)

    def test_inquiry_comment(self):
        comment = InquiryComment(comment=self.text)
        self.assertEqual(self.text, comment.comment)
