from django.test import tag

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_academic_course_area(self):
        self.ac_course_area.save()
        self.assertEqual(self.c_area, self.ac_course_area.course_area)

    def test_create_academic_course(self):
        self.ac_course.save()
        self.assertEqual(self.course, self.ac_course.name)

    def test_create_areas_and_hours(self):
        self.institute.save()
        self.degree.save()
        self.ac_course_area.save()
        self.a_and_h.save()
        self.assertEqual(self.a_and_h.hours, self.hours)
        self.assertEqual(self.ac_course_area.course_area,
                         self.c_area)

    def test_create_degree(self):
        self.institute.save()
        self.degree.save()
        self.assertEqual(self.degree.degree, self.c_degree)

    def test_create_academic_institute(self):
        self.institute.save()
        self.assertEqual(self.institute.institute, self.c_institute)
