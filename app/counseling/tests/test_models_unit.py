from django.test import tag

from counseling.models import CareerPlan, Comment, CoursePlan

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_career_plan(self):
        degree_start_date = CareerPlan(degree_start_date=self.date)
        expected_graduation_date = CareerPlan(
            expected_graduation_date=self.date)
        self.assertEqual(self.date, degree_start_date.degree_start_date)
        self.assertEqual(self.date,
                         expected_graduation_date.expected_graduation_date)

    def test_create_comment_plan(self):
        comment = Comment(comment=self.text)
        self.assertEqual(self.text, comment.comment)

    def test_create_course_plan(self):
        required = CoursePlan(expected_semester=self.date)
        self.assertTrue(required.expected_semester)
