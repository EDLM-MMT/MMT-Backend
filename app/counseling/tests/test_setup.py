# from unittest.mock import patch

import datetime

from counseling.models import CareerPlan
from generate_transcript.models import (AcademicCourseArea, AcademicInstitute,
                                        Degree)
from rest_framework.test import APITestCase
from users.models import MMTUser, UserRecord


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.date = datetime.date(1997, 10, 19)
        self.text = " text goes here"
        self.c_area = "course_area_1"
        self.c_degree = "degree1"
        self.c_institute = "institute1"
        self.uname = "username"
        self.user = MMTUser.objects.create_user(self.uname, "password")
        self.email = "test@test.com"
        self.ur = UserRecord(user_profile=self.user, email=self.email)
        self.hours = 5
        self.institute = AcademicInstitute(institute=self.c_institute)
        self.degree = Degree(degree=self.c_degree, institute=self.institute)
        self.ac_course_area = AcademicCourseArea(course_area=self.c_area)
        self.cp = CareerPlan(
            owner=self.ur, degree_start_date=self.date,
            expected_graduation_date=self.date)

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
