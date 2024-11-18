from django.contrib.auth.models import Group
from users.models import MMTUser
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, AreasAndHour,
                                        Degree, MilitaryCourse, Transcript,
                                        TranscriptStatus)
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


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


class TranscriptStatusSerializer(ObjectPermissionsAssignmentMixin,
                                 serializers.ModelSerializer):
    recipient = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all())
    transcript = serializers.PrimaryKeyRelatedField(
        queryset=Transcript.objects.all())

    class Meta:
        model = TranscriptStatus
        fields = ['transcript', 'recipient', 'status', 'academic_institute']

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            transcript_obj = Transcript.objects.get(id=self.context['request'].data['transcript'])
            if self.context['request'].user == transcript_obj.subject.user_profile:
                transcript_subject = transcript_obj.subject.user_profile
                transcript_recipient = self.instance.recipient
                perms = {
                    'view_transcriptstatus': [transcript_subject, transcript_recipient],
                    'change_transcriptstatus': [transcript_subject],
                    # 'delete_transcriptstatus': [transcript_subject, transcript_recipient]
                }

        return perms
    
    def create(self, validated_data):
        if 'status' in validated_data and validated_data['status']:
            transcript_obj = Transcript.objects.get(id=self.context['request'].data['transcript'])
            if self.context['request'].user == transcript_obj.subject.user_profile:
                validated_data['status'] = TranscriptStatus.STATUS.Delivered
            else:
                validated_data['status'] = TranscriptStatus.STATUS.Pending
        transcriptStatus = TranscriptStatus.objects.create(**validated_data)
        return transcriptStatus
