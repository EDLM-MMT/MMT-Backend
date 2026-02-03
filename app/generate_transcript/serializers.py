import logging

from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from academic_institute.models import AcademicInstitute
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        ACEIdentifier, AreasAndHour, Degree,
                                        MilitaryCourse, MilitaryCourse_User,
                                        MilitaryExperience, Transcript,
                                        TranscriptStatus)

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

    def create(self, validated_data):
        ace_id = validated_data.get('ace_identifier')
        obj, created = ACEIdentifier.objects.get_or_create(
            ace_identifier=ace_id)
        if created:
            logger.info('Created ACEIdentifier: %s', obj)
        else:
            logger.info('ACEIdentifier already exists: %s', obj)
        return obj


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
                  'instruction', 'service',
                  'skill_level']


class MilitaryCourseSerializer(serializers.ModelSerializer):

    skill_level = serializers.CharField(write_only=True,
                                        required=False, allow_null=True,
                                        allow_blank=True)
    version = serializers.CharField(required=False, allow_null=True,
                                    allow_blank=True)

    class Meta:
        model = MilitaryCourse
        fields = ['experience_id', 'experience_name',
                  'description',
                  'instruction', 'service', 'version', 'skill_level']

    def create(self, validated_data):
        experience_id = validated_data.get('experience_id')
        experience_name = validated_data.get('experience_name')
        skill_level = validated_data.get('skill_level', '') or ''
        validated_data['skill_level'] = skill_level  # Ensure it's never None
        if validated_data.get('version'):
            obj, created = MilitaryCourse.objects.get_or_create(
                experience_id=experience_id, defaults=validated_data)
            if created:
                logger.info('Created MilitaryCourse: %s', obj)
            else:
                logger.info('MilitaryCourse already exists: %s', obj)
            return obj
        validated_data.pop('version', '')
        obj, created = MilitaryExperience.objects.get_or_create(
            experience_name=experience_name,
            skill_level=skill_level or '',
            defaults=validated_data
        )
        if created:
            logger.info('Created MilitaryExperience: %s', obj)
        else:
            logger.info('MilitaryExperience already exists: %s', obj)
        return obj

    def update(self, instance, validated_data):
        def update_instance_fields(inst, data):
            for attr, value in data.items():
                setattr(inst, attr, value)
            inst.save()
            return inst

        experience_id = validated_data.get('experience_id')
        version = validated_data.get('version', '')
        experience_name = validated_data.get('experience_name')
        skill_level = validated_data.get('skill_level', '') or ''

        if version:
            if instance.experience_id == experience_id:
                updated = update_instance_fields(instance, validated_data)
                logger.info('Updated MilitaryCourse: %s', updated)
            else:
                logger.warning('MilitaryCourse experience_id mismatch: %s',
                               experience_id)
            return instance

        validated_data.pop('version', None)
        if hasattr(instance, 'experience_name') and \
                instance.experience_name == experience_name:
            if hasattr(instance, 'skill_level') and \
                    instance.skill_level == skill_level:
                updated = update_instance_fields(instance, validated_data)
                logger.info('Updated MilitaryExperience: %s', updated)
                return updated
            if not hasattr(instance, 'skill_level'):
                updated = update_instance_fields(instance, validated_data)
                logger.info('Updated MilitaryExperience with '
                            'no skill level: %s', updated)
                return updated
            logger.warning('MilitaryExperience skill_level mismatch: %s',
                           skill_level)
        else:
            logger.warning('MilitaryExperience experience_name mismatch: %s',
                           experience_name)
        return instance


class AreasAndHourSerializer(serializers.ModelSerializer):
    academic_course_area = AcademicCourseAreaSerializer()
    military_course = serializers.CharField()
    military_name = serializers.CharField(write_only=True,
                                          required=False, allow_null=True)
    skill_level = serializers.CharField(write_only=True,
                                        required=False, allow_null=True,
                                        allow_blank=True)
    ace_identifier = serializers.CharField()
    version = serializers.CharField(required=False, allow_null=True,
                                    allow_blank=True)

    class Meta:
        model = AreasAndHour
        fields = ['hours', 'level', 'academic_course_area',
                  'military_course', 'ace_identifier',
                  'start_date', 'end_date', 'last_updated_on',
                  'version', 'military_name', 'skill_level']

    def create(self, validated_data):

        area_data = validated_data.pop('academic_course_area')
        military_id = validated_data.pop('military_course', None)
        military_name = validated_data.pop('military_name', None)
        skill_level = validated_data.pop('skill_level', '') or ''
        ace_id = validated_data.pop('ace_identifier')
        ace_identifier, created_1 = ACEIdentifier.objects.get_or_create(
            ace_identifier=ace_id)
        if created_1:
            logger.info('Created ACEIdentifier: %s', ace_identifier)
        area, created_a = AcademicCourseArea.objects.get_or_create(**area_data)
        if created_a:
            logger.info('Created Academic Course Area: %s', area)
        else:
            logger.info('Academic Course Area already exists: %s', area)
        if validated_data.get('version'):
            military, created_2 = MilitaryCourse.objects.get_or_create(
                experience_id=military_id)
        else:
            military, created_2 = MilitaryExperience.objects.get_or_create(
                experience_name=military_name, skill_level=skill_level or '')
        if created_2:
            logger.info('Created Military Experience: %s', military)
        if validated_data.get('version') is None:
            validated_data['version'] = ''
        validated_data['academic_course_area'] = area
        validated_data['military_course'] = military
        validated_data['ace_identifier'] = ace_identifier
        instance = AreasAndHour.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):

        if instance['last_updated_on'] > validated_data['last_updated_on']:
            area_data = validated_data.pop('academic_course_area')
            military_id = validated_data.pop('military_course', None)
            military_name = validated_data.get('military_name', None)
            skill_level = validated_data.get('skill_level', '') or ''
            ace_id = validated_data.pop('ace_identifier')
            ace_identifier = ACEIdentifier.objects.get(
                ace_identifier=ace_id)
            area, created_a = AcademicCourseArea.objects.\
                get_or_create(**area_data)
            if created_a:
                logger.info('Created Academic Course Area: %s', area)
            else:
                logger.info('Academic Course Area already exists: %s', area)
            if validated_data.get('version'):
                military, created_2 = MilitaryCourse.objects.get_or_create(
                    experience_id=military_id)
            else:
                military, created_2 = MilitaryExperience.objects.get_or_create(
                    experience_name=military_name,
                    skill_level=skill_level or '')
            if created_2:
                logger.info('Created Military Experience : %s', military)
            validated_data['academic_course_area'] = area
            validated_data['military_course'] = military
            validated_data['ace_identifier'] = ace_identifier
            instance = AreasAndHour.objects.update(**validated_data)
            return instance
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
        if c:
            logger.info('Created TranscriptStatus: %s', transcriptStatus)
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


class MilitaryCourseUserSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='course_id')
    experience_type = serializers.CharField(
        source='course_id.determine_experience_type')

    class Meta:
        model = MilitaryCourse_User
        fields = ['course', 'experience_type', 'start_date',
                  'end_date', 'created', 'modified',]
