# Generated by Django 3.2.23 on 2024-01-25 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicCourse',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='AcademicCourseArea',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course_area', models.CharField(max_length=500)),
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
            name='ACEMapping',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='AreasAndHour',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('hours', models.DecimalField(decimal_places=2, help_text='Enter value in hours', max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('degree', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='MilitaryCourse',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course_id', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]
