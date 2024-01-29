# Generated by Django 3.2.23 on 2024-01-29 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MOS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Set MOS code', max_length=100)),
                ('name', models.CharField(help_text='Set MOS name', max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='mmtuser',
            name='eso_default',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mmtuser',
            name='location',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mmtuser',
            name='position',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mmtuser',
            name='rank',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mmtuser',
            name='sector',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]