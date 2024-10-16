from unittest.mock import Mock, patch

from django.contrib.auth.models import Group
from django.test import tag
from inquiry.models import Inquiry, InquiryComment, InquiryFAQ
from inquiry.serializer import (InquiryCommentSerializer, InquiryFAQSerializer,
                                InquirySerializer)

from .test_setup import TestSetUp


@tag('unit')
class SerializersTests(TestSetUp):
    def test_inquiry_FAQ_serializer(self):
        issue = InquiryFAQ(issue=self.text, response=self.text)
        serialized_faq = InquiryFAQSerializer(issue)

        self.assertEqual(
            self.text, serialized_faq.data['issue'])
        self.assertEqual(
            self.text, serialized_faq.data['response'])

    def test_create_serialize_faq(self):
        serialized_faq = InquiryFAQSerializer(data={
            'issue': self.text,
            'response': self.text,
        })
        serialized_faq.is_valid()
        serialized_faq.save()

        self.assertEqual(self.text.strip(), serialized_faq.instance.issue)
        self.assertEqual(self.text.strip(), serialized_faq.instance.response)

    def test_serialize_inquiry(self):
        inq = Inquiry(email=self.email, name=self.text,
                      description=self.text, subject=self.text,
                      file=self.file_field)
        serialized_inq = InquirySerializer(inq)

        self.assertEqual(self.email, serialized_inq.data['email'])
        self.assertEqual(self.text, serialized_inq.data['name'])
        self.assertEqual(self.text, serialized_inq.data['description'])
        self.assertEqual(self.text, serialized_inq.data['subject'])
        self.assertTrue(serialized_inq.data['file'])

    def test_serialize_inquiry_permissions(self):
        eso_group = Group.objects.create(name='ESO')
        eso_group.save()
        inq = Inquiry(owner=self.user, name=self.text,
                      description=self.text, subject=self.text,
                      file=self.file_field, default_assigned=eso_group,
                      assigned=self.user)
        inq.save()
        serialized_inq = InquirySerializer(inq)
        perms = serialized_inq.get_permissions_map(False)

        self.assertEqual(len(perms), 3)
        self.assertIn('view_inquiry', perms)
        self.assertIn('change_inquiry', perms)
        self.assertIn('delete_inquiry', perms)
        self.assertListEqual(perms['view_inquiry'], [
            self.user, self.user, eso_group])
        self.assertListEqual(perms['change_inquiry'], [self.user, self.user])
        self.assertListEqual(perms['delete_inquiry'], [self.user, self.user])

    def test_serialize_inquiry_comment(self):
        inq = Inquiry(email=self.email, name=self.text,
                      description=self.text, subject=self.text,
                      file=self.file_field)
        inq.save()
        comment = InquiryComment(
            comment=self.text, poster=self.user, inquiry=inq)
        comment.save()
        serialized_comm = InquiryCommentSerializer(comment)

        self.assertEqual(self.uname, serialized_comm.data['poster'])
        self.assertEqual(inq.pk, serialized_comm.data['inquiry'])
        self.assertEqual(self.text, serialized_comm.data['comment'])
        self.assertIn('created', serialized_comm.data)

    def test_serialize_inquiry_comment_permissions(self):
        inq = Inquiry(email=self.email, name=self.text,
                      description=self.text, subject=self.text,
                      file=self.file_field)
        inq.save()
        comment = InquiryComment(
            comment=self.text, poster=self.user, inquiry=inq)
        comment.save()
        serialized_comm = InquiryCommentSerializer(comment)
        eso_group = Group.objects.create(name='ESO')
        eso_group.save()
        with patch('inquiry.serializer.Inquiry.objects') \
                as inq_objs:
            mock = Mock()
            mock.data = {'inquiry': mock}
            inq_objs.get.return_value = mock
            mock.default_assigned = eso_group
            mock.assigned = self.user
            serialized_comm.context['request'] = mock
            perms = serialized_comm.get_permissions_map(False)

            self.assertEqual(len(perms), 1)
            self.assertIn('view_inquirycomment', perms)
            self.assertListEqual(perms['view_inquirycomment'], [
                self.user, eso_group, self.user])
