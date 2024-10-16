from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, AreasAndHour,
                                        Degree)
from rest_framework.test import APITestCase


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.c_area = "course_area_1"
        self.course = "course1"
        self.c_degree = "degree1"
        self.c_institute = "institute1"
        self.code = "1234"
        self.hours = 10

        self.ac_course_area = AcademicCourseArea(course_area=self.c_area)
        self.ac_course = \
            AcademicCourse(name=self.course, code=self.code,
                           course_area=self.c_area)
        self.institute = AcademicInstitute(institute=self.c_institute)
        self.degree = Degree(degree=self.c_degree, institute=self.institute)
        self.a_and_h = AreasAndHour(hours=self.hours, degree=self.degree,
                                    academic_course_area=self.ac_course_area)

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
