from counseling.models import CareerPlan, Comment, CoursePlan, ESONote
from counseling.serializers import (CareerPlanSerializer, CommentSerializer,
                                    CoursePlanSerializer, ESONoteSerializer)
from django.contrib.auth.models import Group
from django.test import tag

from .test_setup import TestSetUp


@tag('unit')
class SerializersTests(TestSetUp):
    def test_serialize_career_plan(self):
        cp = CareerPlan(degree_start_date=self.date,
                        expected_graduation_date=self.date)
        serialized_cp = CareerPlanSerializer(cp)

        self.assertEqual(
            str(self.date), serialized_cp.data['degree_start_date'])
        self.assertEqual(
            str(self.date), serialized_cp.data['expected_graduation_date'])

    def test_create_serialize_career_plan(self):
        self.ur.save()
        self.user.save()
        self.institute.save()
        self.degree.save()
        serialized_cp = CareerPlanSerializer(data={
            'degree_start_date': str(self.date),
            'expected_graduation_date': str(self.date),
            'owner': self.email,
            'eso': self.uname,
            'academic_institute': self.institute.institute,
            'degree': {
                'institute': self.institute.institute,
                'degree': self.degree.degree
            }
        })
        serialized_cp.is_valid()
        serialized_cp.save()

        self.assertEqual(
            self.date, serialized_cp.instance.degree_start_date)
        self.assertEqual(
            self.date, serialized_cp.instance.expected_graduation_date)
        self.assertEqual(self.ur, serialized_cp.instance.owner)
        self.assertEqual(self.user, serialized_cp.instance.eso)
        self.assertEqual(
            self.institute, serialized_cp.instance.academic_institute)
        self.assertEqual(self.degree, serialized_cp.instance.degree)

    def test_update_serialize_career_plan(self):
        self.ur.save()
        self.user.save()
        self.institute.save()
        self.degree.save()
        cp = CareerPlan(degree_start_date=self.date,
                        expected_graduation_date=self.date,
                        owner=self.ur, eso=self.user)
        cp.save()
        serialized_cp = CareerPlanSerializer(cp, data={
            'degree_start_date': str(self.date.today()),
            'expected_graduation_date': str(self.date.today()),
            'owner': self.email,
            'eso': self.uname,
            'academic_institute': self.institute.institute,
            'degree': {
                'institute': self.institute.institute,
                'degree': self.degree.degree
            }
        })
        serialized_cp.is_valid()
        serialized_cp.save()

        self.assertEqual(
            self.date, serialized_cp.instance.degree_start_date)
        self.assertEqual(
            self.date.today(), serialized_cp.instance.expected_graduation_date)
        self.assertEqual(self.ur, serialized_cp.instance.owner)
        self.assertEqual(self.user, serialized_cp.instance.eso)
        self.assertEqual(
            None, serialized_cp.instance.academic_institute)
        self.assertEqual(None, serialized_cp.instance.degree)

    def test_serialize_career_plan_permissions(self):
        cp = CareerPlan(degree_start_date=self.date,
                        expected_graduation_date=self.date)
        serialized_cp = CareerPlanSerializer(cp)
        serialized_cp.instance.owner = self.ur
        serialized_cp.instance.eso = self.user
        perms = serialized_cp.get_permissions_map(False)
        eso_group = Group.objects.all().get(name='ESO')

        self.assertEqual(len(perms), 2)
        self.assertIn('view_careerplan', perms)
        self.assertIn('change_careerplan', perms)
        self.assertListEqual(perms['view_careerplan'], [
                             self.ur.user_profile, self.user, eso_group])
        self.assertListEqual(perms['change_careerplan'], [
                             self.ur.user_profile, self.user, eso_group])

    def test_serialize_comment(self):
        self.ur.save()
        self.cp.save()
        comment = Comment(comment=self.text, poster=self.user, plan=self.cp)
        comment.save()
        serialized_comment = CommentSerializer(comment)

        self.assertEqual(
            str(self.text), serialized_comment.data['comment'])
        self.assertEqual(
            str(self.user), serialized_comment.data['poster'])
        self.assertEqual(
            self.cp.pk, serialized_comment.data['plan'])

    def test_serialize_comment_permissions(self):
        self.ur.save()
        self.cp.eso = self.user
        self.cp.save()
        comment = Comment(comment=self.text, poster=self.user, plan=self.cp)
        comment.save()
        serialized_comment = CommentSerializer(comment)
        perms = serialized_comment.get_permissions_map(False)
        eso_group = Group.objects.all().get(name='ESO')

        self.assertEqual(len(perms), 1)
        self.assertIn('view_comment', perms)
        self.assertListEqual(perms['view_comment'], [
                             self.ur.user_profile, self.user, eso_group])

    def test_serialize_eso_note(self):
        self.ur.save()
        self.cp.save()
        purpose = ESONote.PURPOSE_CHOICES.Advised
        eso_note = ESONote(note=self.text, poster=self.user,
                           plan=self.cp, purpose=purpose)
        eso_note.save()
        serialized_note = ESONoteSerializer(eso_note)

        self.assertEqual(
            str(self.text), serialized_note.data['note'])
        self.assertEqual(
            str(self.user), serialized_note.data['poster'])
        self.assertEqual(
            self.cp.pk, serialized_note.data['plan'])
        self.assertEqual(
            purpose, serialized_note.data['purpose'])

    def test_serialize_eso_note_permissions(self):
        self.ur.save()
        self.cp.eso = self.user
        self.cp.save()
        purpose = ESONote.PURPOSE_CHOICES.Advised
        eso_note = ESONote(note=self.text, poster=self.user,
                           plan=self.cp, purpose=purpose)
        eso_note.save()
        serialized_note = ESONoteSerializer(eso_note)
        perms = serialized_note.get_permissions_map(False)
        eso_group = Group.objects.all().get(name='ESO')

        self.assertEqual(len(perms), 1)
        self.assertIn('view_esonote', perms)
        self.assertListEqual(perms['view_esonote'], [self.user, eso_group])

    def test_serialize_course_plan(self):
        self.ur.save()
        self.cp.eso = self.user
        self.cp.save()
        self.ac_course_area.save()
        required = CoursePlan(expected_semester=self.date,
                              hours=self.hours, plan=self.cp,
                              course=self.ac_course_area)
        required.save()
        serialized_plan = CoursePlanSerializer(required)

        self.assertEqual(
            str(self.date), serialized_plan.data['expected_semester'])
        self.assertEqual(
            required.approved, serialized_plan.data['approved'])
        self.assertEqual(
            self.cp.pk, serialized_plan.data['plan'])
        self.assertEqual(
            self.ac_course_area.pk, serialized_plan.data['course'])
        self.assertEqual(
            self.hours, serialized_plan.data['hours'])

    def test_serialize_course_plan_permissions(self):
        self.ur.save()
        self.cp.eso = self.user
        self.cp.save()
        self.ac_course_area.save()
        required = CoursePlan(expected_semester=self.date,
                              hours=self.hours, plan=self.cp,
                              course=self.ac_course_area)
        required.save()
        serialized_plan = CoursePlanSerializer(required)
        perms = serialized_plan.get_permissions_map(False)
        eso_group = Group.objects.all().get(name='ESO')

        self.assertEqual(len(perms), 3)
        self.assertIn('view_courseplan', perms)
        self.assertIn('change_courseplan', perms)
        self.assertIn('delete_courseplan', perms)
        self.assertListEqual(perms['view_courseplan'], [
                             self.ur.user_profile, self.user, eso_group])
        self.assertListEqual(perms['change_courseplan'], [
                             self.ur.user_profile, self.user, eso_group])
        self.assertListEqual(perms['delete_courseplan'], [
                             self.ur.user_profile, self.user, eso_group])
