from django.db.models.signals import post_save
from django.dispatch import receiver

from generate_transcript.models import Transcript

from .models import UserRecord


@receiver(post_save, sender=UserRecord)
def create_transcript(sender, instance, created, **kwargs):
    if created:
        Transcript(subject=instance).save()
