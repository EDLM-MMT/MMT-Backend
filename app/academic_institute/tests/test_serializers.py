from django.test import tag

from academic_institute.models import AcademicInstitute
from academic_institute.serializers import (AcademicInstituteSerializer,
                                            ManageAcademicInstituteSerializer)
from users.models import MMTUser
from users.serializers import MMTUserSerializer

from .test_setup import TestSetUp


@tag('unit')
class SerializersTests(TestSetUp):
    def test_serialize_academic_institute(self):
        self.ur.save()
        ai = AcademicInstitute(institute=self.c_institute)
        ai.save()
        serialized_ai = AcademicInstituteSerializer(ai)

        self.assertEqual(
            ai.pk, serialized_ai.data['id'])
        self.assertEqual(
            str(ai.institute), serialized_ai.data['institute'])

    def test_serialize_mmt_user(self):
        self.user.first_name = 'fname'
        self.user.last_name = 'lname'
        self.user.position = 'tester'
        self.user.save()
        serialized_mmt_user = MMTUserSerializer(self.user)

        self.assertEqual(
            str(self.user.email), serialized_mmt_user.data['email'])
        self.assertEqual(
            str(self.user.first_name), serialized_mmt_user.data['first_name'])
        self.assertEqual(
            str(self.user.last_name), serialized_mmt_user.data['last_name'])
        self.assertEqual(
            str(self.user.position), serialized_mmt_user.data['position'])

    def test_create_serialize_mmt_user(self):
        first_name = 'fname'
        last_name = 'lname'
        position = 'tester'
        email = 'createtest@test.com'
        serialized_mmt_user = MMTUserSerializer(data={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'position': position
        })
        serialized_mmt_user.is_valid()

        self.assertRaisesMessage(
            AssertionError,
            "`create()` did not return an object instance.",
            serialized_mmt_user.save)
        self.assertEqual(None, serialized_mmt_user.instance)
        self.assertEqual(MMTUser.objects.all().count(), 1)

    def test_update_serialize_manage_ai(self):
        self.ur.save()
        self.institute.save()
        serialized_ai = ManageAcademicInstituteSerializer(
            self.institute,
            data={
                'members': [
                    {
                        'email': self.ur.email,
                        'position': 'tester'
                    }
                ],
                'administrators': [
                    {
                        'email': self.ur.email
                    }
                ],
                'institute': 'abc'
            }, partial=True)
        serialized_ai.is_valid()
        serialized_ai.save()

        self.assertEqual(
            self.institute.pk, serialized_ai.instance.id)
        self.assertEqual(
            self.c_institute, serialized_ai.instance.institute)
        self.assertIn(self.user, serialized_ai.instance.group.user_set.all())
