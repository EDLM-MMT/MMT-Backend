from unittest.mock import Mock

from django.test import tag

from generate_transcript.models import (ACEIdentifier, AcademicCourse,
                                        MilitaryCourse, MilitaryExperience,
                                        TranscriptStatus)
from generate_transcript.serializers import (ACEIdentifierSerializer,
                                             AcademicCourseSerializer,
                                             MilitaryCourseSerializer,
                                             MilitaryExperienceSerializer,
                                             TranscriptStatusSerializer)

from .test_setup import TestSetUp


@tag('unit')
class SerializersTests(TestSetUp):
    def test_AcademicCourse_serializer(self):
        academic_Course = AcademicCourse(course_area=self.ac_course,
                                         name=self.course,
                                         code=self.code)
        serialized_course = AcademicCourseSerializer(academic_Course)

        self.assertEqual(
            self.code, serialized_course.data['code'])
        self.assertEqual(
            self.course, serialized_course.data['name'])

    def test_AceIdentifier_serializer(self):
        ace_identifier = ACEIdentifier(ace_identifier=self.ace_id)
        serialized_course = ACEIdentifierSerializer(ace_identifier)

        self.assertEqual(
            self.ace_id, serialized_course.data['ace_identifier'])

    def test_MilitaryCourse_serializer(self):
        Military_Course = MilitaryCourse(experience_id=self.code)
        serialized_course = MilitaryCourseSerializer(Military_Course)

        self.assertEqual(
            self.code, serialized_course.data['experience_id'])

    def test_MilitaryExperience_serializer(self):
        Military_Experience = MilitaryExperience(experience_id=self.code)
        serialized_course = MilitaryExperienceSerializer(Military_Experience)

        self.assertEqual(
            self.code, serialized_course.data['experience_id'])

    def test_create_status(self):
        self.ur.save()
        self.transcript.save()
        self.institute.save()

        mock = Mock()
        mock.user = self.user
        mock.data = {'transcript': self.transcript.pk}

        tss = TranscriptStatusSerializer(data={
            "transcript": self.transcript.pk,
            "academic_institute": self.institute.pk,
            "status": TranscriptStatus.STATUS.Pending
        }, context={'request': mock})
        tss.is_valid()
        tss.save()

        self.assertEqual(TranscriptStatus.objects.all().count(), 1)
        self.assertEqual(tss.instance.academic_institute, self.institute)
        self.assertEqual(tss.instance.transcript, self.transcript)

    def test_status_perms(self):
        self.ur.save()
        self.transcript.save()
        self.institute.save()
        self.institute.refresh_from_db()
        expected_perms = {
            'view_transcriptstatus': [self.user,
                                      self.institute.group],
            'change_transcriptstatus': [self.user,
                                        self.institute.group],
        }

        mock = Mock()
        mock.user = self.user
        mock.data = {'transcript': self.transcript.pk}
        mock.academic_institute = self.institute
        mock.recipient = None

        tss = TranscriptStatusSerializer(data={
            "transcript": self.transcript.pk,
            "academic_institute": self.institute.pk,
            "status": TranscriptStatus.STATUS.Pending
        }, context={'request': mock})
        tss.instance = mock
        pm = tss.get_permissions_map(created=False)

        self.assertDictEqual(pm, expected_perms)
