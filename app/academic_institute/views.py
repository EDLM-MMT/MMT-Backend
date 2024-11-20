import logging

from rest_framework import mixins, viewsets
from rest_framework_guardian import filters

from academic_institute.models import AcademicInstitute
from academic_institute.serializers import (AcademicInstituteSerializer,
                                            ManageAcademicInstituteSerializer)

logger = logging.getLogger(__name__)


class AcademicInstituteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve available Academic Institutes
    """
    queryset = AcademicInstitute.objects.all().order_by('institute')
    serializer_class = AcademicInstituteSerializer


class ManageAcademicInstituteViewSet(mixins.RetrieveModelMixin,
                                     mixins.UpdateModelMixin,
                                     mixins.ListModelMixin,
                                     viewsets.GenericViewSet):
    """
    Manage applicable Academic Institutes
    """
    queryset = AcademicInstitute.objects.all().order_by('institute')
    serializer_class = ManageAcademicInstituteSerializer
    filter_backends = [filters.ObjectPermissionsFilter]
