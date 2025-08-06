from rest_framework.test import APITestCase

from academic_institute.models import AcademicInstitute
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AreasAndHour, Degree, MilitaryCourse,
                                        MilitaryTestResult, Transcript)
from users.models import MMTUser, UserRecord


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
        self.email = "admin@example.com"
        self.uname = "username"
        self.test_type = "CLEP"
        self.t_name = "clep test"
        self.passing_score = 50

        self.user = MMTUser.objects.create_user(self.uname, "password")
        self.ur = UserRecord(user_profile=self.user, email=self.email)

        self.transcript = Transcript(subject=self.ur)

        self.ac_course_area = AcademicCourseArea(course_area=self.c_area)
        self.ac_course = \
            AcademicCourse(name=self.course, code=self.code,
                           course_area=self.c_area)
        self.institute = AcademicInstitute(institute=self.c_institute)
        self.degree = Degree(degree=self.c_degree, institute=self.institute)
        self.a_and_h = AreasAndHour(hours=self.hours, degree=self.degree,
                                    academic_course_area=self.ac_course_area)
        self.military_course = MilitaryCourse(course_name=self.course)
        self.test_result = MilitaryTestResult(
            test_type=self.test_type, course_name=self.t_name,
            passing=self.passing_score)

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
