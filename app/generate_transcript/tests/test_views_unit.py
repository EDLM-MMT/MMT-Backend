from datetime import date

from django.test import tag

from generate_transcript.views import set_areas_hours

from .test_setup import TestSetUp


@tag('unit')
class ViewsTests(TestSetUp):

    def test_set_areas_hours(self):
        area_obj = "Math"
        ace_id = "ACE123"
        ah_obj = self.DummyObj(area_obj, 3, "Upper", date(2023, 1, 1),
                               date(2023, 6, 1), ace_id)
        course = self.DummyCourse(date(2023, 2, 1), date(2023, 5, 1))
        qs = self.DummyQS([ah_obj])
        area, hours, level, returned_ace_id = \
            set_areas_hours(qs, course, [], [], [])
        self.assertEqual(area, [area_obj])
        self.assertEqual(hours, [3])
        self.assertEqual(level, ["Upper"])
        self.assertEqual(returned_ace_id, ace_id)
