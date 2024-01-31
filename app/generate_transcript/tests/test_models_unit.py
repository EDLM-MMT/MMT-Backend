from django.test import tag

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, AreasAndHour,
                                        Degree)

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_academic_course_area(self):
        course_area = AcademicCourseArea(course_area=self.c_area)
        self.assertEqual(self.c_area, course_area.course_area)

    def test_create_academic_course(self):
        course = AcademicCourse(name=self.course)
        self.assertEqual(self.course, course.name)

    def test_create_areas_and_hours(self):
        hour_val = 10
        acad_course_area = AcademicCourseArea(course_area=self.c_area)
        course_area = AcademicCourse(academic_course_area=acad_course_area)
        hours = AreasAndHour(hours=hour_val)
        self.assertEqual(hours.hours, hour_val)
        self.assertEqual(acad_course_area.course_area,
                         course_area.academic_course_area.course_area)

    def test_create_degree(self):
        degree = Degree(degree=self.c_degree, area_and_hours=self.a_and_h)
        self.assertEqual(degree.degree, self.c_degree)

    def test_create_academic_institue(self):
        institute = AcademicInstitute(institute=self.institute,)
        self.assertEqual(institute.institute, self.institute)
