from counseling.models import CareerPlan, Comment, CoursePlan, ESONote
from django.test import tag

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_career_plan(self):
        cp = CareerPlan(degree_start_date=self.date,
                        expected_graduation_date=self.date)
        self.assertEqual(self.date, cp.degree_start_date)
        self.assertEqual(self.date, cp.expected_graduation_date)

    def test_create_comment_plan(self):
        self.ur.save()
        self.cp.save()
        comment = Comment(comment=self.text, poster=self.user, plan=self.cp)
        comment.save()

        self.assertEqual(self.text, comment.comment)

    def test_update_comment_plan(self):
        self.ur.save()
        self.cp.save()
        new_text = "changing the comment text"
        comment = Comment(comment=self.text, poster=self.user, plan=self.cp)
        comment.save()

        self.assertIsNotNone(comment.pk)

        comment.comment = new_text
        comment.save()
        comment = Comment.objects.first()

        self.assertEqual(self.text, comment.comment)
        self.assertNotEqual(new_text, comment.comment)
        self.assertEqual(Comment.objects.all().count(), 1)

    def test_create_eso_note(self):
        self.ur.save()
        self.cp.save()
        purpose = ESONote.PURPOSE_CHOICES.Advised
        eso_note = ESONote(note=self.text, poster=self.user,
                           plan=self.cp, purpose=purpose)
        eso_note.save()

        self.assertEqual(self.text, eso_note.note)
        self.assertEqual(purpose, eso_note.purpose)

    def test_update_eso_note(self):
        self.ur.save()
        self.cp.save()
        purpose = ESONote.PURPOSE_CHOICES.Updated
        new_text = "changing the comment text"
        eso_note = ESONote(note=self.text, poster=self.user,
                           plan=self.cp, purpose=purpose)
        eso_note.save()

        self.assertIsNotNone(eso_note.pk)

        eso_note.comment = new_text
        eso_note.save()
        eso_note = ESONote.objects.first()

        self.assertEqual(self.text, eso_note.note)
        self.assertNotEqual(new_text, eso_note.note)
        self.assertEqual(ESONote.objects.all().count(), 1)

    def test_create_course_plan(self):
        required = CoursePlan(expected_semester=self.date)
        self.assertTrue(required.expected_semester)
