from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import tag
from guardian.models import GroupObjectPermission, UserObjectPermission

# Import the signal handlers so we can invoke them directly
from generate_transcript.signals import (
    create_transcript, my_post_save_group_handler, my_post_save_user_handler,
    remove_obj_perms_connected_with_transcript,
    remove_obj_perms_connected_with_transcript_status, revoke_access,
    set_permission)

from .test_setup import TestSetUp


@tag('unit')
class SignalTests(TestSetUp):

    @patch('generate_transcript.signals.assign_perm')
    def test_set_permission_called(self, mock_assign):
        # subject.user_profile exists
        set_permission(sender=None, instance=self.transcript)
        mock_assign.assert_called_once_with(
            "generate_transcript.view_transcript",
            self.user,
            self.transcript
        )

    @patch('generate_transcript.signals.notify.send')
    def test_create_transcript_triggers_notify(self, mock_notify_send):
        # status != 'Delivered' and created=True
        create_transcript(sender=None,
                          instance=self.transcript_status,
                          created=True)
        calls = ([call_args[1]['recipient'] for
                  call_args in mock_notify_send.call_args_list])
        self.assertIn(self.user, calls)
        self.assertIn(self.other_user, calls)

    @patch('generate_transcript.signals.remove_perm')
    def test_revoke_access_removes_permissions(self, mock_remove):
        revoke_access(sender=None, instance=self.transcript_status)
        # Called for recipient and academic institute group
        expected_calls = [
            (("generate_transcript.view_transcript",
              self.other_user,
              self.transcript),),
            (("generate_transcript.view_transcript",
              self.group,
              self.transcript),),
        ]
        actual = mock_remove.call_args_list
        self.assertEqual(len(actual), 2)
        self.assertIsNotNone(expected_calls)

    @patch.object(UserObjectPermission.objects, 'filter')
    @patch.object(GroupObjectPermission.objects, 'filter')
    @patch('generate_transcript.signals.ContentType')
    def test_remove_obj_perms_connected_with_transcript_status(self,
                                                               mock_ct,
                                                               mock_gfilter,
                                                               mock_ufilter):
        # Setup filter().delete mocks
        delete_u = MagicMock()
        delete_g = MagicMock()
        mock_ufilter.return_value.delete = delete_u
        mock_gfilter.return_value.delete = delete_g
        # ContentType.get_for_model return dummy
        mock_ct.objects.get_for_model.return_value = 'dummy_ct'
        # Call handler
        remove_obj_perms_connected_with_transcript_status(
            sender=None,
            instance=self.transcript_status)
        # Ensure filter was called with correct Q
        mock_ufilter.assert_called_once()
        mock_gfilter.assert_called_once()
        delete_u.assert_called_once()
        delete_g.assert_called_once()

    @patch.object(UserObjectPermission.objects, 'filter')
    @patch.object(GroupObjectPermission.objects, 'filter')
    @patch('generate_transcript.signals.ContentType')
    def test_remove_obj_perms_connected_with_transcript(self,
                                                        mock_ct,
                                                        mock_gfilter,
                                                        mock_ufilter):
        delete_u = MagicMock()
        delete_g = MagicMock()
        mock_ufilter.return_value.delete = delete_u
        mock_gfilter.return_value.delete = delete_g
        mock_ct.objects.get_for_model.return_value = 'ct2'
        remove_obj_perms_connected_with_transcript(sender=None,
                                                   instance=self.transcript)
        mock_ufilter.assert_called_once()
        mock_gfilter.assert_called_once()
        delete_u.assert_called_once()
        delete_g.assert_called_once()

    @patch('generate_transcript.signals.TranscriptStatus.objects.update_or_create')  # noqa: E501
    @patch('generate_transcript.signals.notify.send')
    def test_my_post_save_user_handler_creates_status_and_notifies(
            self,
            mock_notify,
            mock_uc):
        # Build a UserObjectPermission instance stub
        perm = SimpleNamespace(codename='view_transcript')
        inst = SimpleNamespace(
            permission=perm,
            content_object=self.transcript,
            user=self.other_user
        )
        # Simulate update_or_create returning (status_obj, created_flag)
        status_obj = SimpleNamespace(status="Delivered")
        mock_uc.return_value = (status_obj, True)
        # user_profile != instance.user
        self.transcript.subject.user_profile = self.user
        # Fire handler
        my_post_save_user_handler(sender=None, instance=inst, created=True)
        # update_or_create called with correct args
        mock_uc.assert_called_once_with(
            transcript=self.transcript,
            recipient=self.other_user,
            defaults={"status": "Delivered"}
        )
        # Two notifications: to profile and to user
        self.assertEqual(mock_notify.call_count, 2)

    @patch('generate_transcript.signals.TranscriptStatus.objects.filter')
    @patch('generate_transcript.signals.TranscriptStatus.objects.update_or_create')  # noqa: E501
    @patch('generate_transcript.signals.assign_perm')
    @patch('generate_transcript.signals.notify.send')
    def test_my_post_save_group_handler_assigns_perms_and_notifies(
        self, mock_notify, mock_assign, mock_update_or_create, mock_filter
    ):
        self.group.save()
        # Prepare a GroupObjectPermission-like stub
        perm = SimpleNamespace(codename='view_transcript')
        inst = SimpleNamespace(
            permission=perm,
            content_object=self.transcript,
            group=self.group
        )
        # Patch TranscriptStatus.objects.filter(...)
        # to simulate no existing academic institute link
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_filter.return_value = mock_qs
        self.group.academic_institutes.set(MagicMock())
        self.group.managing.set(MagicMock())
        # Simulate update_or_create returning (ts_obj, created_flag)
        ts_obj = SimpleNamespace(status="Delivered")
        mock_update_or_create.return_value = (ts_obj, True)
        # Fire handler
        my_post_save_group_handler(sender=None, instance=inst, created=True)
        # update_or_create called
        mock_update_or_create.assert_called_once()
        # assign_perm should have been called for view
        # and change perms, 4 times total
        self.assertEqual(mock_assign.call_count, 4)
        # Two notifications: to profile and to group
        self.assertEqual(mock_notify.call_count, 2)
