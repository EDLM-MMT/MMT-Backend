import logging

from rest_framework import mixins, viewsets
from rest_framework.response import Response
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

    def partial_update(self, request, *args, **kwargs):
        """
        Add a user without removing others
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        sm = serializer.data['members']
        rm = request.data['members']
        new_members = {'members': sm + rm}
        serializer = self.get_serializer(
            instance, data=new_members, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
