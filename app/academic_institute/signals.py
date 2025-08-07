import logging

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from guardian.models import GroupObjectPermission, UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm

from academic_institute.models import AcademicInstitute
from generate_transcript.models import TranscriptStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AcademicInstitute)
def create_groups(sender, instance, created, **kwargs):
    # if new
    if created:
        update = False
        # if no group set
        if instance.group is None:
            # get or create a group from the institute name
            group = Group.objects.get_or_create(
                name=instance.institute + " Members")[0]
            instance.group = group
            update = True
        # if no admin group set
        if instance.admins is None:
            # get or create a group from the institute name
            admins = Group.objects.get_or_create(
                name=instance.institute + " Admins")[0]
            instance.admins = admins
            update = True
        if update:
            instance.save()


@receiver(post_save, sender=AcademicInstitute)
def update_permissions(sender, instance, created, **kwargs):
    view_ai_perm = 'view_academicinstitute'
    change_ai_perm = 'change_academicinstitute'
    view_t_perm = 'generate_transcript.view_transcript'
    view_ts_perm = 'generate_transcript.view_transcriptstatus'
    change_ts_perm = 'generate_transcript.change_transcriptstatus'
    accepted_state = ['Delivered', 'Opened', 'Downloaded',]

    # add new permissions if new or changed
    if (created or instance.tracker.has_changed('group')) and instance.group:
        assign_perm(view_ai_perm, instance.group, instance)
        # add perms to associated Transcript Status objects
        for ts in TranscriptStatus.objects.filter(academic_institute=instance):
            assign_perm(view_ts_perm, instance.group, ts)
            assign_perm(change_ts_perm, instance.group, ts)
            # if Transcript Status in accepted state, give access to Transcript
            if ts.status in accepted_state:
                assign_perm(view_t_perm, instance.group, ts.transcript)

    # if not new and had prior and prior is not admin
    if not created and instance.tracker.previous('group') and\
            instance.admins.pk != instance.tracker.previous('group'):
        group = Group.objects.get(pk=instance.tracker.previous('group'))
        # remove view permission
        remove_perm(view_ai_perm, group, instance)
        # remove perms from associated Transcript Status objects
        for ts in TranscriptStatus.objects.filter(academic_institute=instance):
            remove_perm(view_ts_perm, group, ts)
            remove_perm(change_ts_perm, group, ts)
            # if Transcript Status in accepted state and access not granted
            # somewhere else, remove access to Transcript
            # complex query is:
            # check if there exists a TS where status is in accepted state,
            # AI group is this prior group, and it isn't for this AI.
            # if that does not exist, we need to revoke access to the
            # transcript
            if ts.status in accepted_state and not\
                    TranscriptStatus.objects.filter(
                        academic_institute__group=group,
                        status__in=accepted_state
                    ).exclude(academic_institute=instance).exists():
                remove_perm(view_t_perm, group, ts.transcript)

    if created or instance.tracker.has_changed('admins'):
        # add new permissions if new or changed
        assign_perm(view_ai_perm, instance.admins, instance)
        assign_perm(change_ai_perm, instance.admins, instance)
        # skip if new or no prior
        if not created and instance.tracker.previous('admins'):
            # else remove change permission
            remove_perm(change_ai_perm, Group.objects.get(
                pk=instance.tracker.previous('admins')), instance)
            # if prior is not members group remove view permission
            if instance.tracker.previous('admins') != instance.group.pk:
                remove_perm(view_ai_perm, Group.objects.get(
                    pk=instance.tracker.previous('admins')), instance)


@receiver(pre_delete, sender=AcademicInstitute)
def remove_obj_perms_connected_with_academic_institute(sender, instance,
                                                       **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()
