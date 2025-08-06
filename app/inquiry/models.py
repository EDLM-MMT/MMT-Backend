import logging

import clamd
import magic
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from generate_transcript.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE
from users.models import MMTUser

# Create your models here.
logger = logging.getLogger()


class InquiryFAQ(StatusModel, TimeStampedModel):
    STATUS = Choices('Active', 'Inactive')
    id = models.BigAutoField(primary_key=True)
    issue = models.TextField(help_text="Set issue text", validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    response = models.TextField(help_text="Set response text", validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
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
                              help_text="Set owner email", validators=[
                                  RegexValidator(
                                      regex=REGEX_CHECK,
                                      message=REGEX_ERROR_MESSAGE),
                              ])
    name = models.CharField(max_length=200, blank=True,
                            help_text="Set owner name", validators=[
                                RegexValidator(regex=REGEX_CHECK,
                                               message=REGEX_ERROR_MESSAGE),
                            ])
    subject = models.CharField(max_length=200, help_text="Set inquiry title",
                               validators=[
                                   RegexValidator(
                                       regex=REGEX_CHECK,
                                       message=REGEX_ERROR_MESSAGE),
                               ])
    assigned = models.ForeignKey(MMTUser, related_name='assigned_inquiries',
                                 on_delete=models.SET_NULL, blank=True,
                                 null=True, help_text="Select assigned user")
    description = models.TextField(help_text="Set inquiry description",
                                   validators=[
                                       RegexValidator(
                                           regex=REGEX_CHECK,
                                           message=REGEX_ERROR_MESSAGE),
                                   ])
    inquiry_type = models.ForeignKey(InquiryFAQ, related_name='inquiry',
                                     on_delete=models.SET_NULL, blank=True,
                                     null=True,
                                     help_text="Select inquiry type")
    file = models.FileField(blank=True, null=True, upload_to='inquiries/',
                            help_text="Upload necessary files")
    default_assigned = models.ForeignKey(
        Group, related_name='assigned_group', on_delete=models.SET_NULL,
        blank=True, null=True, help_text="Select default assigned group")

    def clean(self):
        if self.file:
            # scan file for malicious payloads
            cd = clamd.ClamdNetworkSocket(
                host="clamd.clamav", port=3310, timeout=10)
            json_file = self.file
            scan_results = cd.instream(json_file)['stream']

            if 'OK' not in scan_results:
                for issue_type, issue in [scan_results, ]:
                    logger.error(
                        '%s %s in file from %s',
                        issue_type, issue, self.owner
                    )
                    raise ValidationError(
                        f'{issue_type} {issue} in file from {self.owner}')
            # only save file if no issues found
            # rewind buffer
            json_file.seek(0)

            # use magic to check file type
            mime_type = magic.from_buffer(json_file.read(), mime=True)
            # log issue if file isn't image
            if 'image' not in mime_type.lower():
                logger.error('Invalid file type detected. Expected image, found %s', mime_type)  # noqa: E501
                raise ValidationError('Invalid file type detected. '
                                      f'Expected image, found {mime_type}')
            # rewind buffer
            json_file.seek(0)


class InquiryComment(TimeStampedModel):
    comment = models.TextField(help_text="Set comment text", validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
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
