from unittest.mock import patch

from django.core.management import call_command
from django.test import tag
from .test_setup import TestSetUp


@tag('unit')
class CommandTests(TestSetUp):

    # Test cases for update_ai_admins
    def test_update_ai_admins(self):
        """Test that waiting for db when db is available"""
        with patch('academic_institute.management.'
                   'commands.update_ai_admins.Command') as gi:
            gi.return_value = gi
            gi.self.retrieve_admin_list.return_value = None
            call_command('update_ai_admins')
            self.assertEqual(gi.call_count, 1)

    def test_retrieve_admin_list(self):
        """Test that waiting for db when db is available"""
        with patch('academic_institute.management.'
                   'commands.update_ai_admins.'
                   'Command.retrieve_admin_list') as gi:
            gi.return_value = gi
            call_command('update_ai_admins')
            self.assertEqual(gi.call_count, 1)

    def test_format_admin_list(self):
        """Test that waiting for db when db is available"""
        with patch('academic_institute.management.'
                   'commands.update_ai_admins.Command.'
                   'format_admin_list') as gi:
            gi.return_value = gi
            call_command('update_ai_admins')
            self.assertEqual(gi.call_count, 1)
