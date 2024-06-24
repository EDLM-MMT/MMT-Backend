from django.contrib.auth.models import Group
from rest_framework import serializers

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, AreasAndHour,
                                        Degree, MilitaryCourse, Transcript)


class AcademicCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCourse
        fields = ['course_area', 'name', 'code',]


class AcademicCourseAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCourseArea
        fields = ['course_area',]


class AcademicInstituteSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='name', queryset=Group.objects.all(), required=False)

    class Meta:
        model = AcademicInstitute
        fields = ['institute', 'group',]


class DegreeSerializer(serializers.ModelSerializer):
    institute = serializers.SlugRelatedField(
        slug_field='institute', queryset=AcademicInstitute.objects.all())

    class Meta:
        model = Degree
        fields = ['institute', 'degree',]


class MilitaryCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryCourse
        fields = ['course_id',]


class AreasAndHourSerializer(serializers.ModelSerializer):
    academic_course_area = AcademicCourseAreaSerializer()
    degree = DegreeSerializer()
    military_course = MilitaryCourseSerializer()

    class Meta:
        model = AreasAndHour
        fields = ['hours', 'name', 'code',]


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'
