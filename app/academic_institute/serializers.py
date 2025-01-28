import logging

from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from academic_institute.models import AcademicInstitute
from users.models import MMTUser

logger = logging.getLogger(__name__)


class MMTUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = MMTUser
        fields = ['email', 'first_name', 'last_name', 'position',]

        def validate_email(attrs):
            return attrs
        extra_kwargs = {
            'email': {'validators': [validate_email]},
            'position': {'default': ''}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        inst = MMTUser.objects.filter(email=attrs['email'])
        if inst.exists():
            self.instance = inst.get()
        return attrs

    def create(self, validated_data):
        return None


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
    members = MMTUserSerializer(many=True, source='group.user_set.all')
    administrators = serializers.ListField(
        child=serializers.EmailField(), source='admins.user_set.all',
        read_only=True)

    class Meta:
        model = AcademicInstitute
        fields = ['id', 'institute', 'members', 'administrators']

    def update(self, instance, validated_data):
        members = validated_data.pop('group', {'user_set': {'all': []}})[
            'user_set']['all']
        email_keys = {member['email']: member['position']
                      for member in members}
        instance.group.user_set.set(MMTUser.objects.filter(
            email__in=list(email_keys.keys())))
        for user in instance.group.user_set.all():
            if user.position != email_keys[user.email]:
                user.position = email_keys[user.email]
                user.save()

        return instance
