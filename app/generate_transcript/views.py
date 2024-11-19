import logging
import random
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django_renderpdf.views import PDFView
from guardian.shortcuts import (assign_perm, get_objects_for_group,
                                get_objects_for_user, get_perms)
from notifications.signals import notify
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework_guardian import filters

from academic_institute.models import AcademicInstitute
from generate_transcript.models import Transcript, TranscriptStatus
from generate_transcript.serializers import (TranscriptSerializer,
                                             TranscriptStatusSerializer)
from users.models import MMTUser

logger = logging.getLogger(__name__)


class RandomPDFView(PDFView):
    """Randomly generates PDFs to test behavior"""
    template_name = 'modernizedTranscript.html'
    download_name = 'resume'
    # prompt_download = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # context['items'] = []
        # num = random.randint(50, 100)
        # for i in range(num):
        #     context['items'].append(
        #         {'first': '1', 'second': 'two', 'third': i})
        context = kwargs['context']
        return context

# @permission_required("generate_transcript.view_transcript")
def transcript_html_view(request):
    context = {}
    context['items'] = []

    transcript_obj = get_objects_for_user(request.user,
                                          "generate_transcript.view_transcript",
                                          klass=Transcript)

    # num = random.randint(50, 100)
    # for i in range(num):
    #     context['items'].append(
    #         {'first': 'one', 'second': 'two', 'third': i})

    for obj in transcript_obj:
        context['items'].append(
            {'first': obj.subject})

    return render(request=request, template_name='test.html', context=context)


class TranscriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def retrieve(self, request, pk=None, *args, **kwargs):
        transcript = get_object_or_404(self.queryset, pk=pk)

        if not request.user.has_perm('generate_transcript.view_transcript',
                                     transcript):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        # Create a PDF view
        pdf_view = RandomPDFView.as_view()

        context = {'name': transcript.subject.name,
                   'dob': transcript.subject.dob.strftime('%d %^b %Y'),
                   'ssn': transcript.subject.ssn,
                   'rank': transcript.subject.rank,
                   'status': transcript.subject.status,
                   'date': datetime.today().strftime('%d %^b %Y'),
                   'branch': transcript.subject.branch}

        return pdf_view(request, context=context)


class TranscriptStatusViewSet(viewsets.ModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = TranscriptStatus.objects.all()
    serializer_class = TranscriptStatusSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def create(self, request, *args, **kwargs):
        transcript_pk = request.data.get('transcript')
        recipient_pk = request.data.get('recipient')
        ai_pk = request.data.get('academic_institute')
        transcript = Transcript.objects.get(pk=transcript_pk)
        # if not request.user.has_perm('generate_transcript.view_transcript', transcript):
        #     return Response({'detail': 'You do not have permission'
        #                      ' to perform this action'},
        #                     status=status.HTTP_403_FORBIDDEN)
        if request.user == transcript.subject.user_profile:
            if recipient_pk:
                recipient_user = MMTUser.objects.filter(email=recipient_pk)

            if ai_pk:
                recipient_user = (
                    AcademicInstitute.objects.get(id=ai_pk)).group

            try:
                assign_perm("generate_transcript.view_transcript",
                            recipient_user,
                            transcript)
            except IntegrityError as e:
                # Handle the duplicate entry exception
                if 'duplicate key value violates unique constraint' in str(e):
                    # Specific handling for duplicate entry
                    logger.error("Duplicate entry detected!")
                    return Response({'detail': "Permission Already Assigned"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Handle other IntegrityError cases
                    logger.error("Other IntegrityError occurred:", e)
                    return Response({'detail': "Other IntegrityError occurred, " +
                                     "check logs for details"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return super().create(request, *args, **kwargs)
