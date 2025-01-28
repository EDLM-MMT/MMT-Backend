import logging

from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import (assign_perm, get_groups_with_perms, get_perms,
                                remove_perm)

from academic_institute.models import AcademicInstitute

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
def update_permissions(sender, instance, update_fields, **kwargs):
    view_perm = 'view_academicinstitute'
    change_perm = 'change_academicinstitute'
    # get groups with permissions on object
    existing = get_groups_with_perms(instance)
    # cycle through existing permissions to remove old
    for group in existing:
        # if admin skip
        if group == instance.admins:
            continue
        # else remove change permission
        remove_perm(change_perm, group, instance)
        # if not assigned remove view permission
        if group != instance.group:
            remove_perm(view_perm, group, instance)
    # add new permissions if missing
    if instance.group and not (
            get_perms(instance.group, instance)
            and view_perm in get_perms(instance.group, instance)):
        assign_perm(view_perm, instance.group, instance)
    if instance.admins and not (
            get_perms(instance.admins, instance)
            and view_perm in get_perms(instance.admins, instance)
            and change_perm in get_perms(instance.admins, instance)):
        assign_perm(view_perm, instance.admins, instance)
        assign_perm(change_perm, instance.admins, instance)
