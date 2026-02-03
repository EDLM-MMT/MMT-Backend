import logging
from datetime import datetime

from celery import shared_task
from rest_framework import status
from rest_framework.response import Response

from configuration.models import MMTConfig
from generate_transcript.management.commands.load_elrr_records import Command
from generate_transcript.serializers import (ACEIdentifierSerializer,
                                             AreasAndHourSerializer,
                                             MilitaryCourseSerializer)
from generate_transcript.utils.ace_utils import (extract_fields,
                                                 fetch_ace_metadata,
                                                 save_serialized)

logger = logging.getLogger(__name__)


@shared_task(name="workflow_to_load_ELRR_data")
def ai_admin_workflow():
    """AI automated workflow"""

    logger.info('STARTING DATA LOADING FROM ELRR')
    start = datetime.now()

    load_elrr_records = Command()

    load_elrr_records.handle()

    logger.info('COMPLETED DATA LOADING FROM ELRR IN %s',
                datetime.now() - start)


logger = logging.getLogger(__name__)


@shared_task(name="workflow_to_load_ACE_Credits")
def ace_data_workflow():
    """ACE Credits data automated workflow"""
    logger.info('STARTING DATA LOADING FOR ACE Credits Data')
    headers = {'content-type': 'application/json'}
    config = MMTConfig.objects.first()
    if config.xis_api.endswith('/'):
        url = config.xis_api + 'api/metadata/' if config else None
    else:
        url = config.xis_api + '/api/metadata/' if config else None

    if not url:
        logger.error('ACE services API URL not configured.')
        return Response({'detail': 'Configuration error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    all_results = fetch_ace_metadata(url, headers)
    military_course, ace_identifier, area_hours_list = \
        extract_fields(all_results)

    save_serialized(MilitaryCourseSerializer, military_course,
                    'MilitaryCourse')
    save_serialized(ACEIdentifierSerializer, ace_identifier, 'ACEIdentifier')
    save_serialized(AreasAndHourSerializer, area_hours_list, 'AreasAndHour')

    logger.info('COMPLETED DATA LOADING FOR ACE Credits Data')
    return {'detail': 'Data Fetching Task Completed', 'status': 'success'}
