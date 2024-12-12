from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from users.models import MMTUser
from notifications.signals import notify
from guardian.shortcuts import assign_perm, get_perms
from guardian.models import GroupObjectPermission, UserObjectPermission, BaseObjectPermission
from django.shortcuts import get_object_or_404
import logging

from .models import AcademicInstitute, Transcript, TranscriptStatus

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transcript)
def set_permission(sender, instance, **kwargs):
    # assign view permissions to transcript subject 
    assign_perm("generate_transcript.view_transcript", instance.subject.user_profile, instance)

@receiver(post_save, sender=TranscriptStatus)
def create_transcript(sender, instance, created, **kwargs):
    # if created:
    if instance.status != 'Delivered':
        notify.send(sender=instance.transcript.subject.user_profile,
                    recipient=instance.transcript.subject.user_profile,
                    verb='Transcript Opened',
                    status_val=instance.status)
         

@receiver(post_save, sender=UserObjectPermission)
def my_post_save_handler(sender, instance, created, **kwargs):
       if created:
           if instance.permission.codename == 'view_transcript':
                
                if instance.content_object.subject.user_profile != instance.user:
                
                    transcript_obj, c = TranscriptStatus.objects.update_or_create(transcript=instance.content_object,
                                                                                  recipient=instance.user,
                                                                                  defaults = {"status":"Delivered"})
                    notify.send(sender=instance.content_object.subject.user_profile,
                                recipient=instance.content_object.subject.user_profile,
                                verb='Transcript Delivered',
                                status_val=transcript_obj.status)
                    notify.send(sender=instance.content_object.subject.user_profile,
                                recipient=instance.user,
                                verb='Transcript Delivered',
                                status_val=transcript_obj.status)

       else:
           # an existing instance is updated
           logger.info("Instance updated:", instance)

@receiver(post_save, sender=GroupObjectPermission)
def my_post_save_handler(sender, instance, created, **kwargs):
       if created:
           # new instance is created
           if instance.permission.codename == 'view_transcript':

            academic_group = (instance.group.academic_institutes.all().first() 
                              if instance.group.academic_institutes.all().first() 
                              else instance.group.managing.all().first())
            
            transcript_obj, c = TranscriptStatus.objects.update_or_create(transcript=instance.content_object,
                                                                    academic_institute=academic_group,
                                                                    defaults = {"status":"Delivered"})
            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.content_object.subject.user_profile,
                        verb='Transcript Delivered',
                        status_val=transcript_obj.status)

            notify.send(sender=instance.content_object.subject.user_profile,
                        recipient=instance.group,
                        verb='Transcript Delivered',
                        status_val=transcript_obj.status)

       else:
           # an existing instance is update
            logger.info("Instance updated:", instance)
