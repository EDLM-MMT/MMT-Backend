# Generated by Django 3.2.23 on 2024-01-31 19:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('generate_transcript', '0001_initial'), ('generate_transcript', '0002_initial'), ('generate_transcript', '0003_auto_20240129_2147'), ('generate_transcript', '0004_alter_areasandhour_hours'), ('generate_transcript', '0005_auto_20240131_1724'), ('generate_transcript', '0006_auto_20240131_1922')]

    initial = True

    dependencies = [
        ('users', '0002_auto_20240129_2147'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicCourseArea',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course_area', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.userrecord')),
            ],
        ),
        migrations.CreateModel(
            name='MilitaryCourse',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course_id', models.CharField(max_length=250)),
                ('user_id', models.ManyToManyField(blank=True, max_length=250, related_name='military_course', to='users.UserRecord')),
            ],
        ),
        migrations.CreateModel(
            name='ACEMapping',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('academic_course_area', models.ForeignKey(help_text='Choose an academic area from academic course area', on_delete=django.db.models.deletion.CASCADE, related_name='ace_area', to='generate_transcript.academiccoursearea')),
                ('military_courses', models.ManyToManyField(help_text='Choose military courses related to the academic area', related_name='ace_military', to='generate_transcript.MilitaryCourse')),
            ],
        ),
        migrations.CreateModel(
            name='AcademicInstitute',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('institute', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('degree', models.CharField(max_length=500)),
                ('mos', models.ManyToManyField(help_text='Select valid MOS', related_name='degrees', to='users.MOS')),
                ('institute', models.ForeignKey(default=1, help_text='Choose the affiliated Academic Institute', on_delete=django.db.models.deletion.CASCADE, related_name='degrees', to='generate_transcript.academicinstitute')),
            ],
        ),
        migrations.CreateModel(
            name='AcademicCourse',
            fields=[
                ('code', models.CharField(default='', help_text='Set course code', max_length=200)),
                ('name', models.CharField(default='', help_text='Set course name', max_length=500)),
                ('academiccoursearea_ptr', models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='generate_transcript.academiccoursearea')),
            ],
        ),
        migrations.CreateModel(
            name='AreasAndHour',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('hours', models.PositiveIntegerField()),
                ('academic_course_area', models.ForeignKey(help_text='Choose an academic area from academic course area', on_delete=django.db.models.deletion.CASCADE, related_name='areas_and_hours', to='generate_transcript.academiccoursearea')),
                ('degree', models.ForeignKey(blank=True, help_text='Choose the relevant degree', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='areas_and_hours', to='generate_transcript.degree')),
            ],
        ),
        migrations.AddField(
            model_name='degree',
            name='areas',
            field=models.ManyToManyField(related_name='degrees', through='generate_transcript.AreasAndHour', to='generate_transcript.AcademicCourseArea'),
        ),
    ]
