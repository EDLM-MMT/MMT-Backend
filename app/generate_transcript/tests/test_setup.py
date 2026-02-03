from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from academic_institute.models import AcademicInstitute
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        ACEIdentifier, AreasAndHour, Degree,
                                        MilitaryCourse, MilitaryTestResult,
                                        Transcript, TranscriptStatus)
from users.models import MMTUser, UserRecord


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in generate_transcript"""

    class DummyObj:
        def __init__(self, area, hours, level,  # pylint: disable=too-many-positional-arguments disable=too-many-arguments
                     start_date, end_date, ace_identifier):
            self.academic_course_area = area
            self.hours = hours
            self.level = level
            self.start_date = start_date
            self.end_date = end_date
            self.ace_identifier = ace_identifier

    class DummyCourse:
        def __init__(self, start_date, end_date):
            self.start_date = start_date
            self.end_date = end_date

    class DummyQS(list):
        def first(self):
            return self[0] if self else None

        def exists(self):
            return bool(self)

    def setUp(self):
        """Function to set up necessary data for testing"""
        self.c_area = "course_area_1"
        self.c_area_bad = "bad course 123#@"
        self.course = "course1"
        self.c_degree = "degree1"
        self.c_institute = "institute1"
        self.code = "1234"
        self.hours = 10
        self.ace_id = "ACE-123"
        self.email = "admin@example.com"
        self.uname = "username"
        self.test_type = "CLEP"
        self.t_name = "clep test"
        self.passing_score = 50
        self.group = Group(name='TestGroup')
        self.group.save()

        self.user = MMTUser.objects.create_user(self.uname, "password")
        self.ur = UserRecord(user_profile=self.user, email=self.email)

        self.ac_course_area = AcademicCourseArea(course_area=self.c_area)
        self.ac_course = \
            AcademicCourse(name=self.course, code=self.code,
                           course_area=self.c_area)
        self.ac_bad_course_area = AcademicCourseArea(
            course_area=self.c_area_bad)
        self.institute = AcademicInstitute(institute=self.c_institute,
                                           group=self.group)
        self.degree = Degree(degree=self.c_degree,
                             institute=self.institute)
        self.ace = ACEIdentifier(ace_identifier=self.ace_id)
        self.a_and_h = AreasAndHour(hours=self.hours,
                                    degree=self.degree,
                                    academic_course_area=self.ac_course_area,
                                    ace_identifier=self.ace)
        self.military_course = MilitaryCourse(experience_name=self.course)
        self.test_result = MilitaryTestResult(
            test_type=self.test_type,
            experience_id=self.t_name,
            experience_name=self.t_name,
            passing=self.passing_score, version="1")

        self.other_user = MMTUser.objects.create_user("other", "password")
        self.transcript = Transcript(subject=self.ur)
        self.transcript_status = TranscriptStatus(
            status="Pending",
            transcript=self.transcript,
            recipient=self.other_user,
            academic_institute=self.institute)

        return super().setUp()

    def tearDown(self):

        return super().tearDown()
