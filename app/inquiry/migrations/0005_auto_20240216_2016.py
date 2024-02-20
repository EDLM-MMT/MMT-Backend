# Generated by Django 3.2.24 on 2024-02-16 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inquiry', '0004_auto_20240212_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inquiry',
            name='subject',
        ),
        migrations.AddField(
            model_name='inquiry',
            name='name',
            field=models.CharField(blank=True, help_text='Set owners name', max_length=200),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='title',
            field=models.CharField(help_text='Set inquiry title', max_length=200),
        ),
    ]
