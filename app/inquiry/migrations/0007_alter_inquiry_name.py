# Generated by Django 3.2.24 on 2024-02-20 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inquiry', '0006_rename_title_inquiry_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquiry',
            name='name',
            field=models.CharField(blank=True, help_text='Set owner name', max_length=200),
        ),
    ]
