import logging

from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, get_perms
from notifications.signals import notify

from academic_institute.models import AcademicInstitute
from users.models import MMTUser

from .models import Transcript, TranscriptStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transcript)
def set_permission(sender, instance, **kwargs):
    assign_perm("generate_transcript.view_transcript",
                instance.subject.user_profile, instance)
    notify.send(instance, recipient=instance.subject.user_profile,
                verb='transcript created', action_object=instance)


@receiver(post_save, sender=TranscriptStatus)
def set_permission(sender, instance, **kwargs):
    group = Group.objects.get(name='Navy Academy')
    notify.send(sender=instance.transcript.subject.user_profile,
                recipient=instance.transcript.subject.user_profile,
                verb='transcript status updated',
                status=instance.status)
    notify.send(sender=instance.transcript.subject.user_profile,
                recipient=instance.recipient,
                verb='transcript status updated',
                status=instance.status)
    notify.send(sender=instance.transcript.subject.user_profile,
                recipient=group,
                verb='transcript status',
                status=instance.status)


@receiver(m2m_changed, sender=TranscriptStatus)
def transcript_status_notify(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        recipient_group = AcademicInstitute.objects.get(
            institute=instance.academic_institute)
        # group_members = list(MMTUser.objects.filter(groups__name=instance.academic_institute.group).values_list('email', flat=True))
        notify.send(sender=instance.transcript.subject.user_profile,
                    recipient=instance.transcript.subject.user_profile,
                    verb='transcript status updated',
                    status=instance.status)
        notify.send(sender=instance.transcript.subject.user_profile,
                    recipient=instance.recipient,
                    verb='transcript status updated',
                    status=instance.status)
