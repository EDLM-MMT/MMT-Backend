# Generated by Django 3.2.23 on 2024-02-02 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inquiry', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inquirycomment',
            options={'ordering': ['-created']},
        ),
    ]