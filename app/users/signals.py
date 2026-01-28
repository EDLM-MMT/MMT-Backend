from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from generate_transcript.models import Transcript

from .models import UserRecord


@receiver(post_save, sender=UserRecord)
def create_transcript(sender, instance, created, **kwargs):
    if created:
        Transcript(subject=instance).save()


@receiver(post_migrate)
def create_default_roles(sender, verbosity, stdout, using, apps, **kwargs):
    dantes_admin, new = Group.objects.get_or_create(name='DANTES ADMIN')
    if new:
        for p in Permission.objects.filter(codename__in=[
            'view_mmtuser',
            'view_userrecord',
            'view_user_record_override',
            'view_militarytestresult',
            'view_militarycourse',
            'view_militaryexperience',
            'view_transcript',
            'view_transcript_override',
            'view_transcriptstatus',
            'view_transcript_status_override',
            'view_transcriptmetric',
            'view_transcript_metric_override',]
        ):
            dantes_admin.permissions.add(p)
        stdout.write(
            msg=f"Created Group: {dantes_admin.name}")
        stdout.flush()
    sma, new = Group.objects.get_or_create(name='SVC MEMBER ADVOCATE')
    if new:
        for p in Permission.objects.filter(codename__in=[
            'view_userrecord',
            'view_service_user_record_override',
            'view_militarytestresult',
            'view_militarycourse',
            'view_militaryexperience',
            'view_transcript',
            'view_service_transcript_override',
            'view_transcriptstatus',
            'view_service_transcript_status_override',
            'view_transcriptmetric',
            'view_service_transcript_metric_override',]
        ):
            sma.permissions.add(p)
        stdout.write(
            msg=f"Created Group: {sma.name}")
        stdout.flush()
