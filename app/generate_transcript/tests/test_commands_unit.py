from collections import namedtuple
from unittest.mock import MagicMock, patch

from django.test import tag

from generate_transcript.management.commands import load_elrr_records
from users.models import UserRecord

from .test_setup import TestSetUp


def patch_retrieve_persons_flow(test_func):
    patchers = [
        patch("generate_transcript.management.commands."
              "load_elrr_records.get_elrr_persons"),
        patch("generate_transcript.management.commands."
              "load_elrr_records.validate_person"),
        patch("generate_transcript.management.commands."
              "load_elrr_records.get_elrr_record"),
        patch.object(load_elrr_records.Command, "validate_record"),
        patch.object(load_elrr_records.Command, "load_person"),
        patch.object(load_elrr_records.Command, "load_occupations"),
        patch.object(load_elrr_records.Command, "load_courses"),
    ]

    def wrapper(self):
        with patchers[0] as p0, patchers[1] as p1, patchers[2] as p2, \
            patchers[3] as p3, patchers[4] as p4, patchers[5] as p5, \
                patchers[6] as p6:
            Mocks = namedtuple("Mocks", [
                "mock_get_elrr_persons",
                "mock_validate_person",
                "mock_get_elrr_record",
                "mock_validate_record",
                "mock_load_person",
                "mock_load_occupations",
                "mock_load_courses",
            ])
            mocks = Mocks(p0, p1, p2, p3, p4, p5, p6)
            test_func(self, mocks)
    return wrapper


@tag('unit')
class TestUpdateAcademicInstituteAdminsCommand(TestSetUp):

    def setUp(self):
        self.cmd = load_elrr_records.Command()

    @patch_retrieve_persons_flow
    def test_retrieve_persons_flow(self, mocks):
        # Setup mocks
        mocks.mock_get_elrr_persons.return_value = [{
            "id": "123",
            "firstName": "John",
            "lastName": "Doe",
            "birthdate": "1980-01-01"
        }]
        mocks.mock_validate_person.return_value = True
        mocks.mock_get_elrr_record.return_value = {
            "id": "123",
            "identity": [{}],
            "employment-record": [{}],
            "learning-record": [{}]
        }
        mocks.mock_validate_record.return_value = {
            "person": {"id": "123"},
            "identity": [{}],
            "employment-record": [{}],
            "learning-record": [{}]
        }
        mocks.mock_load_person.return_value = MagicMock(spec=UserRecord)
        mocks.mock_load_occupations.return_value = []
        mocks.mock_load_courses.return_value = []

        self.cmd.retrieve_persons()

        mocks.mock_get_elrr_persons.assert_called_once()
        mocks.mock_validate_person.assert_called_once()
        mocks.mock_get_elrr_record.assert_called_once_with("123")
        mocks.mock_validate_record.assert_called_once()
        mocks.mock_load_person.assert_called_once()
        mocks.mock_load_occupations.assert_called_once()
        mocks.mock_load_courses.assert_called_once()

    def test_validate_record_returns_false_for_invalid_identity(self):
        record = {"identity": '2#$In',
                  "employment-record": [], "learning-record": []}
        result = self.cmd.validate_record(record)
        self.assertFalse(result)

    @patch("generate_transcript.management.commands."
           "load_elrr_records.validate_identity")
    @patch("generate_transcript.management.commands."
           "load_elrr_records.validate_employment_record")
    @patch("generate_transcript.management.commands."
           "load_elrr_records.validate_learning_record")
    def test_validate_record_valid_flow(self, mock_validate_learning,
                                        mock_validate_employment,
                                        mock_validate_identity):
        mock_validate_identity.return_value = [{"name": "SSN",
                                                "homePage": "ssn"}]
        mock_validate_employment.return_value = (
            [{"employmentEndDate": None,
              "extensions": {"http://xapi.edlm/elrr/extensions/"
                             "employment/rank": "Sergeant"}}]
        )
        mock_validate_learning.return_value = (
            [{"learningResource": {"title": "Course",
                                   "description": "Desc",
                                   "number": "C1"},
              "enrollmentDate": "2020-01-01T00:00:00",
              "eventTime": "2020-01-02T00:00:00"}])

        record = {
            "identity": [{}],
            "employment-record": [{}],
            "learning-record": [{}]
        }
        result = self.cmd.validate_record(record)
        self.assertIsInstance(result, dict)
        self.assertIn("identity", result)
        self.assertIn("employment-record", result)
        self.assertIn("learning-record", result)

    @patch("users.models.UserRecord.objects.update_or_create")
    def test_load_person_creates_user_record(self, mock_update_or_create):
        record = {
            "person": {"id": "123", "firstName": "John",
                       "lastName": "Doe", "birthdate": "1980-01-01"},
            "identity": [{"name": "123-45-6789", "homePage": "ssn"}],
            "employment-record": [{"employmentEndDate": None,
                                   "extensions":
                                   {"http://xapi.edlm/elrr/extensions"
                                    "/employment/rank": "Sergeant"}}]
        }
        mock_update_or_create.return_value = (MagicMock(spec=UserRecord),
                                              True)
        ur = self.cmd.load_person(record)
        mock_update_or_create.assert_called_once()
        self.assertIsNotNone(ur)

    @patch("generate_transcript.models.MilitaryExperience."
           "objects.get_or_create")
    @patch("generate_transcript.models.MilitaryCourse_User."
           "objects.get_or_create")
    def test_load_occupations_creates_connections(self,
                                                  mock_mc_user_get_or_create,
                                                  mock_me_get_or_create):
        user = MagicMock(spec=UserRecord)
        record = {
            "employment-record": [{
                "positionTitle": "Engineer",
                "positionDescription": "Works on stuff",
                "employmentEndDate": "2021-01-01T00:00:00",
                "employmentStartDate": "2020-01-01T00:00:00",
                "extensions": {
                    "http://xapi.edlm/elrr/extensions/"
                    "employment/rank": "Sergeant",
                    "http://xapi.edlm/elrr/extensions/"
                    "employment/rankLevel": "E5",
                    "http://xapi.edlm/elrr/extensions/"
                    "employment/jobCode": "J123"
                }
            }]
        }
        mock_me = MagicMock()
        mock_me_get_or_create.return_value = (mock_me, True)
        mock_mc_user = MagicMock()
        mock_mc_user.end_date = None
        mock_mc_user_get_or_create.return_value = (mock_mc_user, True)

        ret = self.cmd.load_occupations(user, record)
        self.assertEqual(len(ret), 1)
        mock_me_get_or_create.assert_called_once()
        mock_mc_user_get_or_create.assert_called_once()

    @patch("generate_transcript.models.MilitaryCourse."
           "objects.get_or_create")
    @patch("generate_transcript.models.MilitaryCourse_User."
           "objects.get_or_create")
    def test_load_courses_creates_connections(self,
                                              mock_mc_user_get_or_create,
                                              mock_mc_get_or_create):
        user = MagicMock(spec=UserRecord)
        record = {
            "learning-record": [{
                "learningResource": {
                    "title": "Course 101",
                    "description": "Intro Course",
                    "number": "C101"
                },
                "enrollmentDate": "2022-01-01T00:00:00",
                "eventTime": "2022-01-02T00:00:00"
            }]
        }
        mock_course = MagicMock()
        mock_mc_get_or_create.return_value = (mock_course, True)
        mock_mc_user = MagicMock()
        mock_mc_user.end_date = None
        mock_mc_user_get_or_create.return_value = (mock_mc_user, True)

        ret = self.cmd.load_courses(user, record)
        self.assertEqual(len(ret), 1)
        mock_mc_get_or_create.assert_called_once()
        mock_mc_user_get_or_create.assert_called_once()

    @patch.object(load_elrr_records.Command, "retrieve_persons")
    def test_handle_calls_retrieve_persons(self, mock_retrieve_persons):
        self.cmd.handle()
        mock_retrieve_persons.assert_called_once()
