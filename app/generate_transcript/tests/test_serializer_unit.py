from django.test import tag

from generate_transcript.serializers import AcademicCourseSerializer
from generate_transcript.models import AcademicCourse

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
