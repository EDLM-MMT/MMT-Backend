import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from guardian.models import GroupObjectPermission, UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm
from notifications.signals import notify

from .models import Transcript, TranscriptStatus

logger = logging.getLogger(__name__)

TRANS_DELIVERED = 'Transcript Delivered'
VIEW_TR = "generate_transcript.view_transcript"
VIEW_TS = "generate_transcript.view_transcriptstatus"
CHANGE_TS = "generate_transcript.change_transcriptstatus"


@receiver(post_save, sender=Transcript)
def set_permission(sender, instance, **kwargs):
    if instance.subject.user_profile:
        assign_perm(VIEW_TR,
                    instance.subject.user_profile, instance)


@receiver(post_save, sender=TranscriptStatus)
def create_transcript(sender, instance, created, **kwargs):
    if instance.status and instance.status != 'Delivered' and instance.transcript.subject.user_profile:

        notify.send(sender=instance.transcript.subject.user_profile,
                    recipient=instance.transcript.subject.user_profile,
                    verb=instance.status,
                    status_val=instance.status)
        if instance.academic_institute and instance.academic_institute.group:
            notify.send(sender=instance.transcript.subject.user_profile,
                        recipient=instance.academic_institute.group,
                        verb=instance.status,
                        status_val=instance.status)
        if instance.recipient:
            notify.send(sender=instance.transcript.subject.user_profile,
                        recipient=instance.recipient,
                        verb=instance.status,
                        status_val=instance.status)


@receiver(post_delete, sender=TranscriptStatus)
def revoke_access(sender, instance, **kwargs):
    if instance.recipient:
        remove_perm(VIEW_TR,
                    instance.recipient, instance.transcript)
    if instance.academic_institute:
        remove_perm(VIEW_TR,
                    instance.academic_institute.group, instance.transcript)


@receiver(pre_delete, sender=TranscriptStatus)
def remove_obj_perms_connected_with_transcript_status(sender, instance,
                                                      **kwargs):
    # remove orphaned permissions
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()


@receiver(pre_delete, sender=Transcript)
def remove_obj_perms_connected_with_transcript(sender, instance,
                                               **kwargs):
    # remove orphaned permissions
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()


@receiver(post_save, sender=UserObjectPermission)
def my_post_save_user_handler(sender, instance, created, **kwargs):
    if created and instance.permission.codename == 'view_transcript':
        if instance.content_object.subject.user_profile != instance.user:

            transcript_obj = (
                TranscriptStatus.objects.
                update_or_create(transcript=instance.content_object,
                                 recipient=instance.user,
                                 defaults={"status": "Delivered"}))[0]
            notify.send(sender=(instance.content_object.
                                subject.user_profile),
                        recipient=(instance.content_object.
                                   subject.user_profile),
                        verb=TRANS_DELIVERED,
                        status_val=transcript_obj.status)
            notify.send(sender=(instance.content_object.
                                subject.user_profile),
                        recipient=instance.user,
                        verb=TRANS_DELIVERED,
                        status_val=transcript_obj.status)


@receiver(post_save, sender=GroupObjectPermission)
def my_post_save_group_handler(sender, instance, created, **kwargs):
    if created:
        # new instance is created
        if instance.permission.codename == 'view_transcript':

            academic_group = None
            # find academic institute
            # WILL have issues if groups are reused
            if TranscriptStatus.objects.filter(
                    academic_institute__in=instance.group.
                    academic_institutes.all()).exists():
                academic_group = TranscriptStatus.objects.filter(
                    academic_institute__in=instance.group.
                    academic_institutes.all()).first().academic_institute
            elif instance.group.academic_institutes.all().exists():
                academic_group = instance.group.academic_institutes.all().\
                    first()
            else:
                academic_group = instance.group.managing.all().first()

            # get or create transcript status
            transcript_obj, c = (TranscriptStatus.
                                 objects.
                                 update_or_create(
                                     transcript=instance.content_object,
                                     academic_institute=academic_group,
                                     defaults={"status": "Delivered"}))
            # if new, set permissions
            if c:
                assign_perm(VIEW_TS, instance.group, transcript_obj)
                assign_perm(
                    VIEW_TS,
                    instance.content_object.subject.user_profile,
                    transcript_obj)
                assign_perm(CHANGE_TS, instance.group, transcript_obj)
                assign_perm(
                    CHANGE_TS,
                    instance.content_object.subject.user_profile,
                    transcript_obj)

            # send notifications
            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.content_object.subject.user_profile,
                        verb=TRANS_DELIVERED,
                        status_val=transcript_obj.status)

            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.group,
                        verb=TRANS_DELIVERED,
                        status_val=transcript_obj.status)
