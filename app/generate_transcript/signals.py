import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.models import GroupObjectPermission, UserObjectPermission
from guardian.shortcuts import assign_perm
from notifications.signals import notify

from .models import Transcript, TranscriptStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transcript)
def set_permission(sender, instance, **kwargs):
    # assign view permissions to transcript subject
    assign_perm("generate_transcript.view_transcript",
                instance.subject.user_profile)
    assign_perm("generate_transcript.view_transcript",
                instance.subject.user_profile, instance)
    assign_perm("generate_transcript.view_transcriptstatus",
                instance.subject.user_profile)
    assign_perm("generate_transcript.change_transcriptstatus",
                instance.subject.user_profile)
    assign_perm("generate_transcript.add_transcriptstatus",
                instance.subject.user_profile)


@receiver(post_save, sender=TranscriptStatus)
def create_transcript(sender, instance, created, **kwargs):
    # if created:
    if instance.status != 'Delivered':
        notify.send(sender=instance.transcript.subject.user_profile,
                    recipient=instance.transcript.subject.user_profile,
                    verb='Transcript Opened',
                    status_val=instance.status)


@receiver(post_save, sender=UserObjectPermission)
def my_post_save_user_handler(sender, instance, created, **kwargs):
    if created:
        if instance.permission.codename == 'view_transcript':

            if instance.content_object.subject.user_profile != instance.user:

                transcript_obj, c = (
                    TranscriptStatus.objects.
                    update_or_create(transcript=instance.content_object,
                                     recipient=instance.user,
                                     defaults={"status": "Delivered"}))
                notify.send(sender=(instance.content_object.
                                    subject.user_profile),
                            recipient=(instance.content_object.
                                       subject.user_profile),
                            verb='Transcript Delivered',
                            status_val=transcript_obj.status)
                notify.send(sender=(instance.content_object.
                                    subject.user_profile),
                            recipient=instance.user,
                            verb='Transcript Delivered',
                            status_val=transcript_obj.status)


@receiver(post_save, sender=GroupObjectPermission)
def my_post_save_group_handler(sender, instance, created, **kwargs):
    if created:
        # new instance is created
        if instance.permission.codename == 'view_transcript':

            academic_group = (instance.group.academic_institutes.all().first()
                              if (instance.group.
                                  academic_institutes.all().first())
                              else (instance.group.
                                    managing.all().first()))

            transcript_obj, c = (TranscriptStatus.
                                 objects.
                                 update_or_create(
                                     transcript=instance.content_object,
                                     academic_institute=academic_group,
                                     defaults={"status": "Delivered"}))
            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.content_object.subject.user_profile,
                        verb='Transcript Delivered',
                        status_val=transcript_obj.status)

            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.group,
                        verb='Transcript Delivered',
                        status_val=transcript_obj.status)
