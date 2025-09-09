from unittest.mock import MagicMock, patch

from django.test import tag

from generate_transcript.tasks import workflow_to_load_ELRR_data

from .test_setup import TestSetUp


@tag('unit')
class TestAIAdminWorkflowTask(TestSetUp):

    @patch('generate_transcript.tasks.Command')
    @patch('generate_transcript.tasks.logger')
    def test_workflow_to_load_ELRR_data_runs_command(self, mock_logger,
                                                     mock_command):
        # Arrange
        mock_handle = MagicMock()
        mock_command.return_value.handle = mock_handle

        # Act
        workflow_to_load_ELRR_data()

        # Assert
        mock_logger.info.assert_any_call('STARTING DATA LOADING FROM ELRR')
        mock_command.return_value.handle.assert_called_once()
        # Check that the completion log was called with something
        # containing 'COMPLETED DATA LOADING'
        completion_calls = [
            call for call in mock_logger.info.call_args_list
            if 'COMPLETED DATA LOADING FROM ELRR IN' in str(call)
        ]
        self.assertTrue(completion_calls)
