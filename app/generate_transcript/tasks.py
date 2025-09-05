import logging
from datetime import datetime

from celery import shared_task

from generate_transcript.management.commands.load_elrr_records import Command

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
