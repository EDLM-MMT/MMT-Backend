import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'mmt_backend_project.settings')

app = Celery('mmt_backend_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
