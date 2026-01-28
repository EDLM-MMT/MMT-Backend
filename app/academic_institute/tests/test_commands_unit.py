from django.core.management import call_command
from django.test import tag

from academic_institute.models import AcademicInstitute

from .test_setup import TestSetUp


@tag('unit')
class CommandTests(TestSetUp):

    # Test cases for update_ai_admins

    def test_full_update_ai_admins(self):
        """Test full update ai admins command"""
        call_command("update_ai_admins")

        self.assertEqual(AcademicInstitute.objects.all().count(), 1)
        self.assertEqual(
            AcademicInstitute.objects.first().institute, "Fake University")
