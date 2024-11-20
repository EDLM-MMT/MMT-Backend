from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse


# Create your models here.
class AcademicInstitute(models.Model):
    """Model to store degree offerings"""
    id = models.BigAutoField(primary_key=True)
    institute = models.CharField(max_length=500, unique=True)
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
    # Groups - for tracking who has access

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.institute}'

    def get_absolute_url(self):
        return reverse("academic_institute:academic-institute-detail",
                       kwargs={"pk": self.pk})
