import logging

from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from academic_institute.models import AcademicInstitute
from generate_transcript.models import (ACEIdentifier,
                                        AcademicCourse,
                                        AcademicCourseArea,
                                        AreasAndHour,
                                        Degree, MilitaryCourse,
                                        MilitaryExperience,
                                        Transcript, TranscriptStatus)

logger = logging.getLogger(__name__)


class AcademicCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCourse
        fields = ['course_area', 'name', 'code',]


class AcademicCourseAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCourseArea
        fields = ['course_area',]


class ACEIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACEIdentifier
        fields = ['ace_identifier',]


class DegreeSerializer(serializers.ModelSerializer):
    institute = serializers.SlugRelatedField(
        slug_field='institute',
        queryset=AcademicInstitute.objects.all())

    class Meta:
        model = Degree
        fields = ['institute', 'degree',]


class MilitaryExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = MilitaryExperience
        fields = ['experience_id', 'experience_name',
                  'description',
                  'instruction', 'service', 'rank']


class MilitaryCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = MilitaryCourse
        fields = ['experience_id', 'experience_name',
                  'description',
                  'instruction', 'service']


class AreasAndHourSerializer(serializers.ModelSerializer):
    academic_course_area = AcademicCourseAreaSerializer()

    class Meta:
        model = AreasAndHour
        fields = ['hours', 'level', 'academic_course_area',
                  'military_course', 'ace_identifier',
                  'start_date', 'end_date', 'last_updated_on',
                  'version']

    def create(self, validated_data):

        area_data = validated_data.pop('academic_course_area')
        area = AcademicCourseArea.objects.create(**area_data)
        validated_data['academic_course_area'] = area
        instance = AreasAndHour.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):

        if instance['last_updated_on'] > validated_data['last_updated_on']:

            area_data = validated_data.pop('academic_course_area')
            area = AcademicCourseArea.objects.update(**area_data)
            validated_data['academic_course_area'] = area
            instance = AreasAndHour.objects.update(**validated_data)
            return instance


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'


class TranscriptStatusSerializer(ObjectPermissionsAssignmentMixin,
                                 serializers.ModelSerializer):
    class Meta:
        model = TranscriptStatus
        fields = ['transcript', 'recipient',
                  'status', 'academic_institute']

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            transcript_obj = (
                Transcript.objects.get(id=self.context['request'].
                                       data['transcript']))

            transcript_subject = transcript_obj.subject.user_profile
            if self.instance.recipient:
                transcript_recipient = self.instance.recipient
            else:
                transcript_recipient = (self.instance.
                                        academic_institute.group)
            perms = {
                'view_transcriptstatus': [transcript_subject,
                                          transcript_recipient],
                'change_transcriptstatus': [transcript_subject,
                                            transcript_recipient]
            }

        return perms

    def create(self, validated_data):
        if 'status' in validated_data and validated_data['status']:
            transcript_obj = Transcript.objects.get(id=self.
                                                    context['request'].
                                                    data['transcript'])
            if (self.context['request'].user ==
                    transcript_obj.subject.user_profile):
                validated_data['status'] = TranscriptStatus.STATUS.Delivered
            else:
                validated_data['status'] = TranscriptStatus.STATUS.Pending
        transcriptStatus, c = TranscriptStatus.objects.update_or_create(
            **validated_data)
        return transcriptStatus

    def to_representation(self, instance):
        return {
            'pk': instance.pk,
            'transcript': {
                "dob": instance.transcript.subject.dob,
                "first_name": instance.transcript.subject.first_name,
                "last_name": instance.transcript.subject.last_name,
                "pk": instance.transcript.pk
            },
            'status': instance.status,
            'academic_institute': instance.academic_institute.institute,
            'modified': instance.modified,
            'created': instance.created
        }
