# from unittest.mock import patch

from rest_framework.test import APITestCase

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AreasAndHour, Degree)


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.c_area = "course_area_1"
        self.course = "course1"
        self.c_degree = "degree1"
        self.institute = "institue1"
        self.code = "1234"

        self.ac_course_area = AcademicCourseArea.objects.\
            create(course_area=self.c_area)
        self.ac_course = \
            AcademicCourse.objects.create(name=self.course, code=self.code,
                                          academic_course_area=self.
                                          ac_course_area)
        self.a_and_h = AreasAndHour.objects.create(hours=10,
                                                   academic_course_area=self.
                                                   ac_course_area)
        self.degree = Degree.objects.create(degree=self.c_degree,
                                            area_and_hours=self.a_and_h)

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
