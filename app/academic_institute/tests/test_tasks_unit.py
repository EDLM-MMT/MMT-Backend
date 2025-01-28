
from unittest.mock import patch

from django.test import tag

from academic_institute.tasks import ai_admin_workflow

from .test_setup import TestSetUp


@tag('unit')
class TasksTests(TestSetUp):

    @patch("academic_institute.tasks.ai_admin_workflow.run")
    def test_ai_admin_workflow(self, mock_run):
        """Testing the working of xia workflow celery task queue"""

        self.assert_(ai_admin_workflow.run())

        self.assert_(ai_admin_workflow.run())
        self.assertEqual(mock_run.call_count, 2)

        self.assert_(ai_admin_workflow.run())
        self.assertEqual(mock_run.call_count, 3)

    def test_check_calls_ai_admin_workflow(self):
        """Testing the calls to commands from task list"""

        with patch('academic_institute.tasks.Command.handle') as mock_extract:

            ai_admin_workflow.run()

            self.assertEqual(mock_extract.call_count, 1)
