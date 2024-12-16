import logging

from celery import shared_task

from academic_institute.management.commands.update_ai_admins import Command

logger = logging.getLogger(__name__)


@shared_task(name="workflow_to_load_AI_admins")
def ai_admin_workflow():
    """AI automated workflow"""

    logger.info('STARTING DATA LOADING FOR AI ADMINS')

    update_ai_admins = Command()

    update_ai_admins.handle()

    logger.info('COMPLETED DATA LOADING FOR AI ADMINS')
