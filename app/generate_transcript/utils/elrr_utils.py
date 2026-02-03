import requests
from requests.auth import AuthBase
from rest_framework import status
from rest_framework.response import Response

from configuration.models import MMTConfig

ACCEPTED_RECORD_STATUSES = ['PASSED', 'COMPLETED']


def validate_identity(identities: list[dict]) -> list[dict]:
    """
    This method takes in a list of Identities and validates that necessary
    fields are populated

    Only Identities that pass validation are returned
    """
    ret = []

    for identity in identities:
        if 'homePage' in identity and "ssn" in identity['homePage'].lower()\
                and 'name' in identity and identity['name']:
            ret.append(identity)

    return ret


def validate_learning_record(learning_records: list[dict]) -> list[dict]:
    """
    This method takes in a list of Learning Records and validates that
    necessary fields are populated

    Only Learning Records that pass validation are returned
    """
    ret = []

    for lr in learning_records:
        if 'learningResource' in lr and lr['learningResource'] and \
            'enrollmentDate' in lr and lr['enrollmentDate'] and \
                'eventTime' in lr and lr['eventTime'] and \
                'recordStatus' in lr and \
                lr['recordStatus'] in ACCEPTED_RECORD_STATUSES:
            res = lr['learningResource']
            if 'title' in res and res['title'] and\
                    'number' in res and res['number']:
                ret.append(lr)

    return ret


def validate_employment_record(employment_records: list[dict]) -> list[dict]:
    """
    This method takes in a list of Employment Records and validates that
    necessary fields are populated

    Only Employment Records that pass validation are returned
    """
    ret = []

    for er in employment_records:
        if 'positionTitle' in er and er['positionTitle'] and \
                'employmentStartDate' in er and er['employmentStartDate'] and \
                'extensions' in er:
            ext = er['extensions']
            if 'http://xapi.edlm/elrr/extensions/employment/rank' in ext and\
                    ext['http://xapi.edlm/elrr/extensions/employment/rank']\
                    and 'http://xapi.edlm/elrr/extensions/employment/jobCode'\
                    in ext and \
                    ext['http://xapi.edlm/elrr/extensions/employment/jobCode']\
                    and 'http://xapi.edlm/elrr/extensions/employment/'\
                        'rankLevel' in ext and\
                    ext['http://xapi.edlm/elrr/extensions/employment/'
                        'rankLevel']:
                ret.append(er)

    return ret


def validate_person(person: dict) -> bool:
    """
    This method takes in a Person record and validates that
    necessary fields are populated

    False is returned if any required fields are missing
    """
    if ('firstName' not in person or not person['firstName']) and \
            ('name' not in person or not person['name']):
        return False
    if ('lastName' not in person or not person['lastName']) and \
            ('name' not in person or not person['name']):
        return False

    return True


def get_elrr_api_url() -> str:
    """This method gets the elrr root api url"""
    elrr_api_url = MMTConfig.objects.first()\
        .elrr_services_api
    if elrr_api_url[-1] != '/':
        elrr_api_url += '/'
    if not elrr_api_url.endswith('api/'):
        elrr_api_url += 'api/'

    return elrr_api_url


def get_elrr_persons() -> list[dict]:
    """
    This method returns the list of Person objects from ELRR
    """
    return requests.get(get_elrr_api_url()+'person', auth=TokenAuth(),
                        timeout=3.0).json()


def get_elrr_record(person_uuid: str) -> dict:
    """
    This method returns the consolidation of a user's records from ELRR
    It currently gets Learning Record, Employment Record, and Identity
    """
    record = {}
    record['learning-record'] = requests.get(
        # TODO update with filter to only get passed courses
        get_elrr_api_url()+f'person/{person_uuid}/learningrecord',
        auth=TokenAuth(), timeout=3.0).json()
    record['identity'] = requests.get(
        get_elrr_api_url()+f'person/{person_uuid}/identity',
        auth=TokenAuth(), timeout=3.0).json()
    record['employment-record'] = requests.get(
        get_elrr_api_url()+f'person/{person_uuid}/employmentrecord',
        auth=TokenAuth(), timeout=3.0).json()
    return record


def handle_unauthenticated_user():
    """This method returns an HTTP response if user is not authenticated"""
    return Response({'Access Denied: Unauthenticated user.'},
                    status.HTTP_401_UNAUTHORIZED)


class TokenAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __init__(self, token=None):
        if token is None:
            token = MMTConfig.objects.first().elrr_api_key
        super().__init__()
        self.token = token

    def __call__(self, r, token_name='Bearer'):
        # modify and return the request

        r.headers['Authorization'] = token_name + ' ' + self.token
        return r
