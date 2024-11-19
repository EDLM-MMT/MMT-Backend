import logging

from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from academic_institute.models import AcademicInstitute
from users.models import MMTUser

logger = logging.getLogger(__name__)


class AcademicInstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicInstitute
        fields = ['institute', 'id']
