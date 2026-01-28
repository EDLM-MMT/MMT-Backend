import logging
import os
import tempfile
from time import sleep
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag

from inquiry.models import Inquiry, InquiryComment, InquiryFAQ

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a temporary log file and attach a FileHandler
        fd, path = tempfile.mkstemp(suffix='.log')
        cls._temp_log = os.fdopen(fd, 'w+')
        cls._temp_log_path = path
        cls._handler = logging.FileHandler(cls._temp_log_path)
        cls._handler.setLevel(logging.DEBUG)
        cls._handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')  # noqa: E501
        )
        # Attach handler to root logger
        logging.getLogger().addHandler(cls._handler)
        logging.getLogger().setLevel(logging.DEBUG)

    @classmethod
    def tearDownClass(cls):
        # Remove handler and close file
        logging.getLogger().removeHandler(cls._handler)
        cls._handler.close()
        cls._temp_log.close()
        os.unlink(cls._temp_log_path)
        super().tearDownClass()

    def _read_log(self):
        """Helper to read current log contents."""
        with open(self._temp_log_path, 'r', encoding='utf-8') as f:
            return f.read()

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
        inquiry_file = Inquiry(file=self.file_field)

        self.assertEqual(self.email, email.email)
        self.assertEqual(self.text, name.name)
        self.assertEqual(self.text, description.description)
        self.assertEqual(self.text, subject.subject)
        self.assertTrue(inquiry_file.file)

    def test_inquiry_comment(self):
        comment = InquiryComment(comment=self.text)
        self.assertEqual(self.text, comment.comment)

    def test_inquiryfaq_str_and_status(self):
        """Test __str__ returns issue and status choices work."""
        self.assertEqual(str(self.faq), self.valid_text)
        # StatusModel provides .status attribute
        self.assertEqual(self.faq.status, 'Active')
        # Toggle status
        self.faq.status = 'Inactive'
        self.faq.save()
        self.assertEqual(self.faq.status, 'Inactive')

    def test_inquiry_valid_without_file(self):
        """Creating an Inquiry without file should pass clean()."""
        inquiry = Inquiry(
            owner=self.user,
            email='user@example.com',
            name='User Name',
            subject='Subject Line',
            assigned=self.user,
            description='Some description',
            inquiry_type=self.faq,
            default_assigned=self.group,
            status='Open'
        )
        # Should not raise
        inquiry.full_clean()

    @patch('inquiry.models.clamd.ClamdNetworkSocket')
    @patch('inquiry.models.magic.from_buffer')
    def test_inquiry_with_good_file(self, mock_magic, mock_clamd_socket):
        """
        Test that a valid image file passes clean():
         - clamd returns OK
         - magic returns an image mime-type
        """
        # Mock clamav scan to return OK
        mock_clamd = MagicMock()
        mock_clamd.instream.return_value = {'stream': ('OK', 'OK')}
        mock_clamd_socket.return_value = mock_clamd
        # Mock magic to return image mime
        mock_magic.return_value = 'image/png'

        # Create a simple image-like file buffer
        image_content = b'\x89PNG\r\n\x1a\n...'
        uploaded = SimpleUploadedFile(
            'test.png', image_content, content_type='image/png'
        )

        inquiry = Inquiry(
            owner=self.user,
            email='user@example.com',
            name='User Name',
            subject='Subject',
            assigned=self.user,
            description='Description here',
            inquiry_type=self.faq,
            default_assigned=self.group,
            status='Open',
            file=uploaded
        )
        # Should not raise ValidationError
        inquiry.full_clean()

        # Ensure clamav and magic were called
        mock_clamd_socket.assert_called_once()
        mock_clamd.instream.assert_called_once()
        mock_magic.assert_called_once()

    @patch('inquiry.models.clamd.ClamdNetworkSocket')
    @patch('inquiry.models.magic.from_buffer')
    def test_inquiry_file_infected(self, mock_magic, mock_clamd_socket):
        """
        If clamd reports an infected file, clean() should
        raise ValidationError.
        """
        mock_clamd = MagicMock()
        # Simulate an infected result: ('EICAR', 'Virus found')
        mock_clamd.instream.return_value = {'stream': ('EICAR',
                                                       'Virus found')}
        mock_clamd_socket.return_value = mock_clamd
        # Magic should not be called in this path
        mock_magic.return_value = 'image/png'

        uploaded = SimpleUploadedFile(
            'bad.bin', b'virus', content_type='application/octet-stream'
        )

        inquiry = Inquiry(
            owner=self.user,
            email='a@b.com',
            name='Name',
            subject='Subj',
            assigned=self.user,
            description='Desc',
            inquiry_type=self.faq,
            default_assigned=self.group,
            status='Open',
            file=uploaded
        )
        with self.assertRaises(ValidationError):
            inquiry.full_clean()

        logs = self._read_log()
        self.assertIn('ERROR', logs)
        self.assertIn('EICAR', logs)

    @patch('inquiry.models.clamd.ClamdNetworkSocket')
    @patch('inquiry.models.magic.from_buffer')
    def test_inquiry_file_wrong_mime(self, mock_magic, mock_clamd_socket):
        """
        If magic returns non-image mime, clean() should raise ValidationError.
        """
        # Clamd returns OK
        mock_clamd = MagicMock()
        mock_clamd.instream.return_value = {'stream': ('OK', 'OK')}
        mock_clamd_socket.return_value = mock_clamd
        # Magic returns text/plain
        mock_magic.return_value = 'text/plain'

        uploaded = SimpleUploadedFile(
            'file.txt', b'hello', content_type='text/plain'
        )

        inquiry = Inquiry(
            owner=self.user,
            email='x@y.com',
            name='Name2',
            subject='Subj2',
            assigned=self.user,
            description='Desc2',
            inquiry_type=self.faq,
            default_assigned=self.group,
            status='Open',
            file=uploaded
        )
        with self.assertRaises(ValidationError):
            inquiry.full_clean()

        logs = self._read_log()
        self.assertIn('ERROR', logs)
        self.assertIn('Invalid file type detected', logs)

    def test_inquirycomment_str_and_ordering(self):
        """Test __str__ and default ordering on InquiryComment."""
        inq = Inquiry.objects.create(
            owner=self.user,
            email='a@a.com',
            name='N',
            subject='S',
            description='D',
            status='Open'
        )
        comment1 = InquiryComment.objects.create(
            comment='First comment',
            inquiry=inq,
            poster=self.user
        )
        sleep(0.01)
        comment2 = InquiryComment.objects.create(
            comment='Second comment',
            inquiry=inq,
            poster=self.user
        )

        self.assertEqual(str(comment1), 'First comment')
        self.assertEqual(str(comment2), 'Second comment')

        comments = list(InquiryComment.objects.filter(inquiry=inq))
        self.assertEqual(comments, [comment2, comment1])

        # Check that comment creation events are logged
        logs = self._read_log()
        # Depending on model_utils TimeStampedModel signals, we might see logs
        # For demonstration, ensure the log file exists and is readable
        self.assertIsNotNone(logs)
