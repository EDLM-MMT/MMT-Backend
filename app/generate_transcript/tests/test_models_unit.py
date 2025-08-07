from django.test import tag

from generate_transcript.models import AcademicCourseArea, MilitaryExperience

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_academic_course_area(self):
        self.ac_course_area.save()
        self.assertEqual(self.c_area, self.ac_course_area.course_area)
        self.assertIn(self.c_area, str(self.ac_course_area))

    def test_create_academic_course(self):
        self.ac_course.save()
        self.assertEqual(self.course, self.ac_course.name)
        self.assertIn(self.c_area, str(self.ac_course))
        self.assertIn(self.course, str(self.ac_course))
        self.assertIn(self.code, str(self.ac_course))
        self.assertEqual(str(self.ac_course), str(
            AcademicCourseArea.objects.get(pk=self.ac_course.pk)))

    def test_create_areas_and_hours(self):
        self.institute.save()
        self.degree.save()
        self.ac_course_area.save()
        self.a_and_h.save()
        self.assertEqual(self.a_and_h.hours, self.hours)
        self.assertEqual(self.ac_course_area.course_area,
                         self.c_area)
        self.assertIn(str(self.ac_course_area), str(self.a_and_h))
        self.assertIn(str(self.hours), str(self.a_and_h))

    def test_create_degree(self):
        self.institute.save()
        self.degree.save()
        self.assertEqual(self.degree.degree, self.c_degree)
        self.assertIn(self.c_degree, str(self.degree))
        self.assertIn(str(self.institute), str(self.degree))

    def test_military_course(self):
        self.military_course.save()
        me = MilitaryExperience.objects.get(pk=self.military_course.pk)
        self.assertEqual(self.military_course.course_name, self.course)
        self.assertEqual(str(me), str(self.military_course))
        self.assertEqual(str(self.military_course.course_name),
                         str(self.military_course))
        self.assertEqual(self.military_course.determine_experience_type(),
                         "Course")

    def test_military_test_result(self):
        self.test_result.save()
        tr = MilitaryExperience.objects.get(pk=self.test_result.pk)
        self.assertEqual(tr.militarycourse.course_name, self.t_name)
        self.assertEqual(str(tr), str(self.test_result))
        self.assertEqual(
            tr.militarycourse.militarytestresult.test_type, self.test_type)
        self.assertIn(str(self.test_result.course_name),
                      str(tr))
        self.assertIn(str(self.test_result.test_type),
                      str(tr))
        self.assertEqual(tr.determine_experience_type(),
                         self.test_type)
