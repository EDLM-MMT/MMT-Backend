# Generated by Django 3.2.24 on 2024-02-16 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inquiry', '0005_auto_20240216_2016'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inquiry',
            old_name='title',
            new_name='subject',
        ),
    ]