# Generated by Django 3.2.23 on 2024-01-31 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counseling', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(help_text='Set comment text'),
        ),
    ]
