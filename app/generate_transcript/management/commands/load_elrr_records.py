import logging
from typing import Union

from django.core.management.base import BaseCommand

from generate_transcript.models import (MilitaryCourse, MilitaryCourse_User,
                                        MilitaryExperience)
from generate_transcript.utils.elrr_utils import (get_elrr_persons,
                                                  get_elrr_record,
                                                  validate_employment_record,
                                                  validate_identity,
                                                  validate_learning_record,
                                                  validate_person)
from users.models import UserRecord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django Command to update Academic Institute Admins
    """

    def retrieve_persons(self):
        """
        Get list of Persons
        """
        people = get_elrr_persons()
        for person in people:
            if validate_person(person):
                record = get_elrr_record(person['id'])
                record['person'] = person
                record = self.validate_record(record)
                if isinstance(record, bool):
                    break
                ur = self.load_person(record)
                occupations = self.load_occupations(ur, record)  # noqa E841
                courses = self.load_courses(ur, record)  # noqa E841

    def validate_record(self, record: dict) -> Union[dict, bool]:
        """
        validate the different components of the record

        only the records that pass validation are returned

        False is returned if there are no valid identity objects
        """

        record['identity'] = validate_identity(record['identity'])
        if not record['identity']:
            return False
        record['employment-record'] = validate_employment_record(
            record['employment-record'])
        record['learning-record'] = validate_learning_record(
            record['learning-record'])

        return record

    def load_person(self, record: dict) -> UserRecord:
        """
        Create or update UserRecord as needed based on the ELRR attributes

        Returns the UserRecord
        """
        person = record['person']
        status = 'Retired'
        rank = 'Veteran'
        defaults = {'elrr_id': person['id'],
                    'first_name': person['firstName'] if 'firstName' in
                    person and person['firstName'] else
                    person['name'].split()[0],
                    'last_name': person['lastName'] if 'lastName' in
                    person and person['lastName'] else
                    person['name'].split()[-1],
                    'branch': 'Coast Guard'}
        if 'birthdate' in person and person['birthdate']:
            defaults['dob'] = person['birthdate']
        for identity in record['identity']:
            if 'ssn' in identity['homePage'].lower():
                defaults['ssn'] = identity['name'].replace('-', '')
        for er in record['employment-record']:
            if not er['employmentEndDate']:
                rank = er['extensions']['http://xapi.edlm/elrr/extensions/employment/rank']  # noqa: E501
                status = 'Active'
                break
        defaults['rank'] = rank
        defaults['status'] = status
        ur, new = UserRecord.objects.update_or_create(
            elrr_id=person['id'], defaults=defaults)
        if new:
            logger.info("New User Record created %s", ur.elrr_id)
        return ur

    def load_occupations(self, user: UserRecord, records: dict) ->\
            list[MilitaryCourse_User]:
        """
        Extract Occupations from records and assign to user

        return list of MilitaryCourse_Users
        """
        ret = []
        for er in records['employment-record']:
            defaults = {
                "experience_name": er['positionTitle'],
                "rank": er['extensions']['http://xapi.edlm/elrr/extensions/employment/rank'],  # noqa: E501
                "rank_level": er['extensions']['http://xapi.edlm/elrr/extensions/employment/rankLevel'],  # noqa: E501
            }
            if 'positionDescription' in er:
                defaults["description"] = er['positionDescription']
            occupation, new = MilitaryExperience.objects.get_or_create(
                experience_id=er['extensions']['http://xapi.edlm/elrr/extensions/employment/jobCode'],  # noqa: E501
                defaults=defaults)
            if new:
                logger.info("New Experience created %s", occupation)
            connection, new = MilitaryCourse_User.objects.get_or_create(
                course_id=occupation, user_id=user,
                start_date=er['employmentStartDate'].split('T')[0]
            )
            if new:
                logger.info("New Military Course User created %s", connection)
            if er['employmentEndDate'] and\
                    connection.end_date !=\
                    er['employmentEndDate'].split('T')[0]:
                connection.end_date = er['employmentEndDate'].split('T')[0]
                connection.save()
            ret.append(connection)
        return ret

    def load_courses(self, user: UserRecord, records: dict) ->\
            list[MilitaryCourse_User]:
        """
        Extract Courses from records and assign to user

        return list of MilitaryCourse_Users
        """
        ret = []
        for lr in records['learning-record']:
            defaults = {
                "course_name": lr['learningResource']['title'],
            }
            if 'description' in lr['learningResource']:
                defaults["description"] = lr['learningResource']['description']
            course, new = MilitaryCourse.objects.get_or_create(
                experience_id=lr['learningResource']['number'],
                defaults=defaults)
            if new:
                logger.info("New Course created %s", course)
            connection, new = MilitaryCourse_User.objects.get_or_create(
                course_id=course, user_id=user,
                start_date=lr['enrollmentDate'].split('T')[0]
            )
            if new:
                logger.info("New Military Course User created %s", connection)
            if lr['eventTime'] and\
                    connection.end_date != lr['eventTime'].split('T')[0]:
                connection.end_date = lr['eventTime'].split('T')[0]
                connection.save()
            ret.append(connection)
        return ret

    def handle(self, *args, **options):
        self.retrieve_persons()
