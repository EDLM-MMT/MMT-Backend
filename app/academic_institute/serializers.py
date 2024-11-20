import logging

from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from academic_institute.models import AcademicInstitute
from users.models import MMTUser

logger = logging.getLogger(__name__)


class AcademicInstituteSerializer(serializers.ModelSerializer,
                                  ObjectPermissionsAssignmentMixin):
    class Meta:
        model = AcademicInstitute
        fields = ['id', 'institute']

    def get_permissions_map(self, created):
        perms = {}

        admins = self.instance.admins
        if admins is not None:
            perms = {
                'change_academicinstitute': [admins,]
            }

        return perms


class ManageAcademicInstituteSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.EmailField(), source='group.user_set.all')
    administrators = serializers.ListField(
        child=serializers.EmailField(), source='admins.user_set.all',
        read_only=True)

    class Meta:
        model = AcademicInstitute
        fields = ['id', 'institute', 'members', 'administrators']

    def update(self, instance, validated_data):
        instance.group.user_set.set(MMTUser.objects.filter(
            email__in=validated_data['group']['user_set']['all']))

        return instance
