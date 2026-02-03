from django.db import models
from django.forms import ValidationError

# Create your models here.


class MMTConfig(models.Model):
    """Model for managing MMT Configuration"""
    elrr_services_api = models.CharField(
        help_text='Enter the host url for the ELRR Services to use.',
        max_length=200)
    elrr_api_key = models.TextField(
        help_text='Enter the API Key to use for communicating with ELRR '
        'Services.')
    xis_api = models.CharField(
        help_text='Enter the host url for the XIS to use.', max_length=200)

    def save(self, *args, **kwargs):
        if not self.pk and MMTConfig.objects.exists():
            raise ValidationError('MMTConfig model already exists')
        return super(MMTConfig, self).save(*args, **kwargs)
