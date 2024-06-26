# Generated by Django 3.2.24 on 2024-02-08 17:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('inquiry', '0002_alter_inquirycomment_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquiry',
            name='default_assigned',
            field=models.ForeignKey(blank=True, help_text='Select default assigned group', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_group', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='inquirycomment',
            name='comment',
            field=models.TextField(help_text='Set comment text'),
        ),
    ]
