from django.contrib.auth.models import Group
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from model_utils import FieldTracker

from generate_transcript.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE


# Create your models here.
class AcademicInstitute(models.Model):
    """Model to store degree offerings"""
    id = models.BigAutoField(primary_key=True)
    institute = models.CharField(max_length=500, unique=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    group = models.ForeignKey(Group, related_name='academic_institutes',
                              on_delete=models.SET_NULL,
                              null=True, blank=True,
                              help_text="Select the group that will manage "
                              "requests for this Institute")
    admins = models.ForeignKey(Group, related_name='managing',
                               on_delete=models.SET_NULL,
                               null=True, blank=True,
                               help_text="Select the group that will manage "
                               "this Institute")
    managed_by_import = models.BooleanField(default=True)

    tracker = FieldTracker(fields=['group', 'admins',])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.institute}'

    def get_absolute_url(self):
        return reverse("academic_institute:academic-institute-detail",
                       kwargs={"pk": self.pk})
