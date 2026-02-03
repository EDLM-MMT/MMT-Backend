from unittest.mock import MagicMock, patch

from django.contrib.auth.models import Group
from django.test import tag

from academic_institute.models import AcademicInstitute
from academic_institute.signals import (
    create_groups, remove_obj_perms_connected_with_academic_institute)

from .test_setup import TestSetUp


@tag('unit')
class TestAcademicInstituteSignals(TestSetUp):

    def setUp(self):
        super().setUp()
        # Use the real AcademicInstitute instance from setup
        self.instance = self.institute
        self.instance.save()  # Ensure it's in the DB

        # Simulate tracker for signals
        self.instance.tracker = MagicMock()
        self.instance.tracker.has_changed.side_effect = (
            lambda field: field in ("group", "admins")
        )
        self.instance.tracker.previous.side_effect = lambda field: None

    @patch("django.contrib.auth.models.Group.objects.get_or_create")
    def test_create_groups_signal_creates_groups(self, mock_get_or_create):
        mock_group = Group.objects.create(name="TestGroup")
        mock_get_or_create.return_value = (mock_group, True)
        self.instance.group = None
        self.instance.admins = None

        create_groups(sender=AcademicInstitute, instance=self.instance,
                      created=True)

        self.assertEqual(self.instance.group, mock_group)
        self.assertEqual(self.instance.admins, mock_group)
        # Confirm the instance was saved
        self.instance.refresh_from_db()
        self.assertIsNotNone(self.instance.group)
        self.assertIsNotNone(self.instance.admins)

    @patch("django.contrib.contenttypes.models."
           "ContentType.objects.get_for_model")
    @patch("guardian.models.UserObjectPermission.objects.filter")
    @patch("guardian.models.GroupObjectPermission.objects.filter")
    def test_remove_obj_perms_con_with_academic_institute(self,
                                                          mock_gop_filter,
                                                          mock_uop_filter,
                                                          mock_get_for_model):
        mock_get_for_model.return_value = MagicMock()
        self.instance.pk = self.instance.pk

        remove_obj_perms_connected_with_academic_institute(sender=AcademicInstitute, instance=self.instance)  # noqa: E501

        self.assertTrue(mock_uop_filter.called)
        self.assertTrue(mock_gop_filter.called)
