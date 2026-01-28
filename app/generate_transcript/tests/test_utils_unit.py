from unittest.mock import MagicMock, patch

from django.test import tag

from configuration.models import MMTConfig
from generate_transcript.utils import ace_utils
from generate_transcript.utils.elrr_utils import (get_elrr_api_url,
                                                  validate_employment_record,
                                                  validate_identity,
                                                  validate_learning_record,
                                                  validate_person)

from .test_setup import TestSetUp


@tag('unit')
class UtilsTests(TestSetUp):
    # pylint: disable=too-many-public-methods
    def test_validate_identity_empty(self):
        arg = [{}]
        ret = validate_identity(arg)

        self.assertListEqual(ret, [])

    def test_validate_identity_one(self):
        ids = {'homePage': 'ssn', 'name': '123'}
        arg = [ids]
        ret = validate_identity(arg)

        self.assertListEqual(ret, arg)

    def test_validate_identity_multiple(self):
        ids = {'homePage': 'ssn', 'name': '123'}
        arg = [ids, ids]
        ret = validate_identity(arg)

        self.assertListEqual(ret, arg)

    def test_validate_identity_mix(self):
        ids = {'homePage': 'ssn', 'name': '123'}
        bad = {'homePage': 'ssn'}
        bad2 = {'homePage': 'no', 'name': '123'}
        arg = [ids, bad, bad2]
        ret = validate_identity(arg)

        self.assertListEqual(ret, [ids,])

    def test_validate_learning_record_empty(self):
        arg = [{}]
        ret = validate_learning_record(arg)

        self.assertListEqual(ret, [])

    def test_validate_learning_record_one(self):
        lr = {'enrollmentDate': '2025-06-06', 'eventTime': '2025-08-06',
              'recordStatus': 'PASSED',
              'learningResource': {
                  'title': 'course title', 'description': 'course desc',
                  'number': 'abc123'}}
        arg = [lr]
        ret = validate_learning_record(arg)

        self.assertEqual(len(ret), 1)
        self.assertDictEqual(ret[0], lr)

    def test_validate_learning_record_multiple(self):
        lr = {'enrollmentDate': '2025-06-06', 'eventTime': '2025-08-06',
              'recordStatus': 'PASSED',
              'learningResource': {
                  'title': 'course title', 'description': 'course desc',
                  'number': 'abc123'}}
        arg = [lr, lr]
        ret = validate_learning_record(arg)

        self.assertEqual(len(ret), 2)
        self.assertDictEqual(ret[0], lr)
        self.assertDictEqual(ret[1], lr)

    def test_validate_learning_record_mix(self):
        lr = {'enrollmentDate': '2025-06-06', 'eventTime': '2025-08-06',
              'recordStatus': 'PASSED',
              'learningResource': {
                  'title': 'course title', 'description': 'course desc',
                  'number': 'abc123'}}
        bad = {'enrollmentDate': '2025-06-06', 'eventTime': '2025-08-06',
               'recordStatus': 'PASSED',
               'learningResource': {
                   'title': 'course title', 'description': 'course desc', }}
        bad2 = {'enrollmentDate': '2025-06-06',
                'recordStatus': 'PASSED',
                'learningResource': {
                    'title': 'course title', 'description': 'course desc',
                    'number': 'abc123'}}
        bad3 = {'enrollmentDate': '2025-06-06', 'eventTime': '2025-08-06',
                'recordStatus': 'FAILED',
                'learningResource': {
                    'title': 'course title', 'description': 'course desc',
                    'number': 'abc123'}}
        arg = [lr, bad, bad2, bad3]
        ret = validate_learning_record(arg)

        self.assertEqual(len(ret), 1)
        self.assertDictEqual(ret[0], lr)

    def test_validate_employment_record_empty(self):
        arg = [{}]
        ret = validate_employment_record(arg)

        self.assertListEqual(ret, [])

    def test_validate_employment_record_one(self):
        er = {'positionTitle': 'job title',
              'employmentStartDate': '2025-08-06',
              'positionDescription': 'job desc',
              'extensions': {
                  'http://xapi.edlm/elrr/extensions/employment/rank': 'ssgt',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/rankLevel': 'e4',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/jobCode': 'abc123'}}  # noqa: E501
        arg = [er]
        ret = validate_employment_record(arg)

        self.assertEqual(len(ret), 1)
        self.assertDictEqual(ret[0], er)

    def test_validate_employment_record_multiple(self):
        er = {'positionTitle': 'job title',
              'employmentStartDate': '2025-08-06',
              'positionDescription': 'job desc',
              'extensions': {
                  'http://xapi.edlm/elrr/extensions/employment/rank': 'ssgt',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/rankLevel': 'e4',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/jobCode': 'abc123'}}  # noqa: E501
        arg = [er, er]
        ret = validate_employment_record(arg)

        self.assertEqual(len(ret), 2)
        self.assertDictEqual(ret[0], er)
        self.assertDictEqual(ret[1], er)

    def test_validate_employment_record_mix(self):
        # Update these extensions
        er = {'positionTitle': 'job title',
              'employmentStartDate': '2025-08-06',
              'positionDescription': 'job desc',
              'extensions': {
                  'http://xapi.edlm/elrr/extensions/employment/rank': 'ssgt',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/rankLevel': 'e4',  # noqa: E501
                  'http://xapi.edlm/elrr/extensions/employment/jobCode': 'abc123'}}  # noqa: E501
        bad = {'positionTitle': 'job title',
               'employmentStartDate': '2025-08-06',
               'positionDescription': 'job desc',
               'extensions': {
                   'http://xapi.edlm/elrr/extensions/employment/rank': 'ssgt',  # noqa: E501
                   'http://xapi.edlm/elrr/extensions/employment/rankLevel': 'e4'}}  # noqa: E501
        bad2 = {'employmentStartDate': '2025-08-06',
                'positionDescription': 'job desc',
                'extensions': {
                    'http://xapi.edlm/elrr/extensions/employment/rank': 'ssgt',  # noqa: E501
                    'http://xapi.edlm/elrr/extensions/employment/rankLevel': 'e4',  # noqa: E501
                    'http://xapi.edlm/elrr/extensions/employment/jobCode': 'abc123'}}  # noqa: E501
        arg = [er, bad, bad2]
        ret = validate_employment_record(arg)

        self.assertEqual(len(ret), 1)
        self.assertDictEqual(ret[0], er)

    def test_validate_person_empty(self):
        arg = {}
        ret = validate_person(arg)

        self.assertFalse(ret)

    def test_validate_person_missing_last_name(self):
        person = {'firstName': 'joe',
                  'whatever': '2025-08-06'}
        ret = validate_person(person)

        self.assertFalse(ret)

    def test_validate_person_missing_birthdate(self):
        person = {'firstName': 'joe',
                  'lastName': '2025-08-06'}
        ret = validate_person(person)

        self.assertTrue(ret)

    def test_validate_person_correct(self):
        person = {'firstName': 'joe', 'lastName': 'shmo',
                  'birthdate': '2025-08-06'}
        ret = validate_person(person)

        self.assertTrue(ret)

    def test_get_elrr_api_url(self):
        base = 'some-url'
        expected = base + '/api/'
        MMTConfig(elrr_services_api=base,
                  elrr_api_key='abc', xis_api='abc').save()

        self.assertEqual(expected, get_elrr_api_url())

    def test_extract_fields_returns_expected_lists(self):
        data = [
            {
                'metadata': {
                    'Metadata_Ledger': {
                        'military_course': {'id': 1},
                        'ace_identifier': {'id': 2},
                        'areaandhour': {'areaandhour': [{'hours': 3}]}
                    }
                }
            }
        ]
        military_course, ace_identifier, area_hours_list = \
            ace_utils.extract_fields(
                data)
        assert military_course == [{'id': 1}]
        assert ace_identifier == [{'id': 2}]
        assert area_hours_list == [{'hours': 3}]

    def test_save_serialized_success(self):
        serializer_class = MagicMock()
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.data = [{'id': 1}]
        serializer_class.return_value = serializer

        ace_utils.save_serialized(serializer_class, [{'id': 1}], 'TestLabel')
        serializer.save.assert_called_once()

    def test_save_serialized_failure(self):
        serializer_class = MagicMock()
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {'error': 'invalid'}
        serializer_class.return_value = serializer

        ace_utils.save_serialized(serializer_class, [{'id': 1}], 'TestLabel')
        serializer.save.assert_not_called()

    def test_fetch_ace_metadata_success(self):
        with patch('generate_transcript.utils.ace_utils.requests.get') as \
                mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = [
                {'results': [{'a': 1}], 'next': 'next_url'},
                {'results': [{'b': 2}], 'next': None}
            ]
            mock_get.return_value = mock_response

            url = 'http://test-url'
            headers = {'Authorization': 'Token test'}
            results = ace_utils.fetch_ace_metadata(url, headers)
            self.assertEqual(results, [{'a': 1}, {'b': 2}])
            self.assertEqual(mock_get.call_count, 2)

    def test_fetch_ace_metadata_failure(self):
        with patch('generate_transcript.utils.ace_utils.requests.get') \
                as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            url = 'http://test-url'
            headers = {}
            results = ace_utils.fetch_ace_metadata(url, headers)
            self.assertEqual(results, [])
