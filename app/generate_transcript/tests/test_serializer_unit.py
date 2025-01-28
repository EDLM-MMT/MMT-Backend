from django.test import tag

from generate_transcript.serializers import (AcademicCourseSerializer,
                                             MilitaryCourseSerializer)
from generate_transcript.models import AcademicCourse, MilitaryCourse

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
        Military_Course = MilitaryCourse(course_name=self.course)
        serialized_course = MilitaryCourseSerializer(Military_Course)

        self.assertEqual(
            self.course, serialized_course.data['course_name'])
