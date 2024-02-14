from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from counseling.models import CareerPlan, Comment, CoursePlan, ESONote
from generate_transcript.models import (AcademicCourseArea, AcademicInstitute,
                                        Degree)
from generate_transcript.serializers import DegreeSerializer
from users.models import MMTUser, UserRecord


class CommentSerializer(ObjectPermissionsAssignmentMixin,
                        serializers.ModelSerializer):
    poster = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all(),
        default=serializers.CurrentUserDefault())
    plan = serializers.PrimaryKeyRelatedField(
        queryset=CareerPlan.objects.all())

    class Meta:
        model = Comment
        fields = ['comment', 'poster', 'created', 'plan',]

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            plan_owner = self.instance.plan.owner.user_profile
            eso_group, _ = Group.objects.get_or_create(name__iexact='ESO')
            eso = self.instance.plan.eso
            perms = {
                'view_comment': [plan_owner, eso, eso_group],
            }

        return perms

    def create(self, validated_data):
        validated_data['poster'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return instance


class ListCommentSerializer(serializers.ModelSerializer):
    poster = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ['comment', 'poster', 'created',]


class ESONoteSerializer(ObjectPermissionsAssignmentMixin,
                        serializers.ModelSerializer):
    poster = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all(),
        default=serializers.CurrentUserDefault())
    plan = serializers.PrimaryKeyRelatedField(
        queryset=CareerPlan.objects.all())

    class Meta:
        model = ESONote
        fields = ['purpose', 'note', 'poster', 'plan', 'created',]

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            eso_group, _ = Group.objects.get_or_create(name__iexact='ESO')
            eso = self.instance.plan.eso
            perms = {
                'view_esonote': [eso, eso_group],
            }

        return perms

    def create(self, validated_data):
        validated_data['poster'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return instance


class ListESONoteSerializer(serializers.ModelSerializer):
    poster = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = ESONote
        fields = ['purpose', 'note', 'poster', 'created',]


class CoursePlanSerializer(ObjectPermissionsAssignmentMixin,
                           serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=AcademicCourseArea.objects.all())
    plan = serializers.PrimaryKeyRelatedField(
        queryset=CareerPlan.objects.all())

    class Meta:
        model = CoursePlan
        fields = ['id', 'course', 'hours', 'required',
                  'approved', 'expected_semester', 'plan',]

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            plan_owner = self.instance.plan.owner.user_profile
            eso_group, _ = Group.objects.get_or_create(name__iexact='ESO')
            eso = self.instance.plan.eso
            perms = {
                'view_courseplan': [plan_owner, eso, eso_group],
                'change_courseplan': [plan_owner, eso, eso_group],
                'delete_courseplan': [plan_owner, eso, eso_group],
            }

        return perms


class ListCoursePlanSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()

    class Meta:
        model = CoursePlan
        fields = ['id', 'course', 'hours', 'required',
                  'approved', 'expected_semester',]


class CareerPlanSerializer(ObjectPermissionsAssignmentMixin,
                           serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        slug_field='email', queryset=UserRecord.objects.all())
    eso = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all())
    degree = DegreeSerializer()
    academic_institute = serializers.SlugRelatedField(
        slug_field='institute', queryset=AcademicInstitute.objects.all())
    comments = ListCommentSerializer(many=True, read_only=True)
    eso_notes = ListESONoteSerializer(many=True, read_only=True)
    courses = ListCoursePlanSerializer(many=True, read_only=True)

    class Meta:
        model = CareerPlan
        fields = ['id', 'owner', 'eso', 'degree', 'academic_institute',
                  'degree_start_date', 'expected_graduation_date', 'comments',
                  'eso_notes', 'courses']

    def get_permissions_map(self, created):
        plan_owner = self.instance.owner.user_profile
        eso_group, _ = Group.objects.get_or_create(name__iexact='ESO')
        eso = self.instance.eso
        perms = {
            'view_careerplan': [plan_owner, eso, eso_group],
            'change_careerplan': [plan_owner, eso, eso_group],
        }

        return perms

    def create(self, validated_data):
        if 'degree' in validated_data:
            degree_dict = validated_data.pop('degree')
            degree = Degree.objects.get(degree=degree_dict.get(
                'degree'),
                institute__institute=validated_data.get('academic_institute'))
            career_plan = super().create(validated_data)
            career_plan.degree = degree
            career_plan.save()
            return career_plan
        return super().create(validated_data)

    def update(self, instance, validated_data):
        do_not_update = {'owner', 'eso', 'degree', 'academic_institute',
                         'degree_start_date', }
        keys = validated_data.keys()
        keys.difference_update(do_not_update)
        for i in keys:
            validated_data.pop(i)
        return super().update(instance, validated_data)
