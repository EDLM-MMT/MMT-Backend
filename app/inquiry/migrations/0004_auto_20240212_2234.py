# Generated by Django 3.2.24 on 2024-02-12 22:34

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inquiry', '0003_auto_20240208_1745'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inquiry',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='inquiry',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='inquiryfaq',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='inquiryfaq',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='description',
            field=models.TextField(help_text='Set inquiry description'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='subject',
            field=models.CharField(help_text='Set inquiry subject', max_length=200),
        ),
        migrations.AlterField(
            model_name='inquiryfaq',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
