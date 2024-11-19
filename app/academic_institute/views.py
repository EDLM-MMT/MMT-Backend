import logging

from rest_framework import viewsets

from academic_institute.models import AcademicInstitute
from academic_institute.serializers import AcademicInstituteSerializer

logger = logging.getLogger(__name__)


class AcademicInstituteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve available Academic Institutes
    """
    queryset = AcademicInstitute.objects.all().order_by('institute')
    serializer_class = AcademicInstituteSerializer
