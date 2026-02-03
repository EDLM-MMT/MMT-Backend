import datetime
from unittest.mock import Mock

from django.test import tag

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        ACEIdentifier, AreasAndHour,
                                        MilitaryCourse, MilitaryExperience,
                                        Transcript, TranscriptStatus)
from generate_transcript.serializers import (AcademicCourseSerializer,
                                             AreasAndHourSerializer,
                                             MilitaryCourseSerializer,
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

    def test_MilitaryCourse_serializer(self):
        Military_Course = MilitaryCourse(experience_name=self.course)
        serialized_course = MilitaryCourseSerializer(Military_Course)

        self.assertEqual(
            self.course, serialized_course.data['experience_name'])

    def test_create_status(self):
        self.ur.save()
        transcript = Transcript.objects.get(subject=self.ur)
        self.institute.save()

        mock = Mock()
        mock.user = self.user
        mock.data = {'transcript': transcript.pk}

        tss = TranscriptStatusSerializer(data={
            "transcript": transcript.pk,
            "academic_institute": self.institute.pk,
            "status": TranscriptStatus.STATUS.Pending
        }, context={'request': mock})
        tss.is_valid()
        tss.save()

        self.assertEqual(TranscriptStatus.objects.all().count(), 1)
        self.assertEqual(tss.instance.academic_institute, self.institute)
        self.assertEqual(tss.instance.transcript, transcript)

    def test_status_perms(self):
        self.ur.save()
        transcript = Transcript.objects.get(subject=self.ur)
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
        mock.data = {'transcript': transcript.pk}
        mock.academic_institute = self.institute
        mock.recipient = None

        tss = TranscriptStatusSerializer(data={
            "transcript": transcript.pk,
            "academic_institute": self.institute.pk,
            "status": TranscriptStatus.STATUS.Pending
        }, context={'request': mock})
        tss.instance = mock
        pm = tss.get_permissions_map(created=False)

        self.assertDictEqual(pm, expected_perms)

    def test_AreasAndHour_serializer_fields(self):
        aca = AcademicCourseArea.objects.create(course_area="Math")
        me = MilitaryExperience.objects.create(
            experience_name="Bootcamp", skill_level="Advanced")
        ace = ACEIdentifier.objects.create(ace_identifier="ACE123")
        area_hour = AreasAndHour.objects.create(
            hours=3,
            level="Upper",
            academic_course_area=aca,
            military_course=me,
            ace_identifier=ace,
            start_date="2023-01-01",
            end_date="2023-06-01",
            last_updated_on=datetime.datetime.now(),
            version="v1"
        )
        serializer = AreasAndHourSerializer(area_hour)
        data = serializer.data
        self.assertEqual(data['hours'], 3)
        self.assertEqual(data['level'], "Upper")
        self.assertEqual(data['version'], "v1")
        self.assertEqual(data['ace_identifier'], ace.ace_identifier)

    def test_AreasAndHour_serializer_validation(self):
        me = MilitaryExperience.objects.create(
            experience_name="Drill", skill_level="Basic")
        ace = ACEIdentifier.objects.create(ace_identifier="ACE456")
        serializer = AreasAndHourSerializer(data={
            "hours": 5,
            "level": "Lower",
            "academic_course_area": {
                "course_area": "management"
            },
            "military_course": me.pk,
            "ace_identifier": ace.pk,
            "start_date": "2023-02-01",
            "end_date": "2023-07-01",
            "last_updated_on": datetime.datetime.now(),
            "version": "v2"
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_AreasAndHour_serializer_create(self):
        me = MilitaryExperience.objects.create(
            experience_name="Field", skill_level="Intermediate")
        ace = ACEIdentifier.objects.create(ace_identifier="ACE789")
        serializer = AreasAndHourSerializer(data={
            "hours": 2,
            "level": "low",
            "academic_course_area": {
                "course_area": "management"
            },
            "military_course": me.pk,
            "ace_identifier": ace.pk,
            "start_date": "2023-03-01",
            "end_date": "2023-08-01",
            "last_updated_on": datetime.datetime.now(),
            "version": "v3"
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertIsInstance(instance, AreasAndHour)
        self.assertEqual(instance.hours, 2)
        self.assertEqual(instance.version, "v3")
