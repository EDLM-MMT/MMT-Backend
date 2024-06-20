from django.contrib.auth.models import Group
from django.db import models
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from users.models import MMTUser

# Create your models here.


class InquiryFAQ(StatusModel, TimeStampedModel):
    STATUS = Choices('Active', 'Inactive')
    id = models.BigAutoField(primary_key=True)
    issue = models.TextField(help_text="Set issue text")
    response = models.TextField(help_text="Set response text")
    default_assigned = models.ForeignKey(
        Group, related_name='inquiry_faqs', on_delete=models.SET_NULL,
        blank=True, null=True, help_text="Select default assigned group")

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.issue}'


class Inquiry(StatusModel, TimeStampedModel):
    STATUS = Choices('Open', 'Closed')
    id = models.BigAutoField(primary_key=True)
    owner = models.ForeignKey(MMTUser, related_name='owned_inquiries',
                              on_delete=models.CASCADE, blank=True, null=True,
                              help_text="Select inquiry owner")
    email = models.EmailField(max_length=200, blank=True,
                              help_text="Set owner email")
    name = models.CharField(max_length=200, blank=True,
                            help_text="Set owner name")
    subject = models.CharField(max_length=200, help_text="Set inquiry title")
    assigned = models.ForeignKey(MMTUser, related_name='assigned_inquiries',
                                 on_delete=models.SET_NULL, blank=True,
                                 null=True, help_text="Select assigned user")
    description = models.TextField(help_text="Set inquiry description")
    inquiry_type = models.ForeignKey(InquiryFAQ, related_name='inquiry',
                                     on_delete=models.SET_NULL, blank=True,
                                     null=True,
                                     help_text="Select inquiry type")
    file = models.FileField(blank=True, null=True, upload_to='inquiries/',
                            help_text="Upload necessary files")
    default_assigned = models.ForeignKey(
        Group, related_name='assigned_group', on_delete=models.SET_NULL,
        blank=True, null=True, help_text="Select default assigned group")


class InquiryComment(TimeStampedModel):
    comment = models.TextField(help_text="Set comment text")
    inquiry = models.ForeignKey(Inquiry, related_name='comments',
                                on_delete=models.CASCADE,
                                help_text="Select associated inquiry")
    poster = models.ForeignKey(MMTUser, related_name='inquiry_comments',
                               on_delete=models.SET_NULL, blank=True,
                               null=True, help_text="Select comment poster")

    def save(self, *args, **kwargs):
        """Block editing"""
        if self.pk:
            kwargs['update_fields'] = []

        super().save(*args, **kwargs)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.comment}'

    class Meta:
        ordering = ['-created',]
