import logging
import random
import re
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django_renderpdf.views import PDFView
from guardian.shortcuts import (assign_perm, get_objects_for_group,
                                get_objects_for_user, get_perms)
from academic_institute.models import AcademicInstitute
from notifications.signals import notify
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework_guardian import filters

from generate_transcript.models import (AreasAndHour, MilitaryCourse_User, Transcript,
                                        TranscriptStatus)
from generate_transcript.serializers import (TranscriptSerializer,
                                             TranscriptStatusSerializer)
from users.models import MMTUser

logger = logging.getLogger(__name__)


class TranscriptPDFView(PDFView):
    """ Generates PDFs for Transcripts"""

    download_name = 'resume'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context = kwargs['context']
        context['image'] = "/static/EducationLogo1.png"
        context['experiences'] = []
        context['experiences']

        for military_obj in kwargs['transcript'].subject.militaryexperience_set.all():
            course_details = MilitaryCourse_User.objects.get(course_id=military_obj.id,
                                                             user_id=kwargs['transcript'].subject)

            area = []
            hours = []
            level = []

            area_hour_details = AreasAndHour.objects.filter(military_course=military_obj.id)
            for areas_hours_obj in area_hour_details:
                area.append(areas_hours_obj.academic_course_area.course_area)
                hours.append(areas_hours_obj.hours)
                level.append(areas_hours_obj.level)
            course_name = ""

            if hasattr(military_obj, 'militarycourse'):
                course_name=military_obj.militarycourse.course_name

            context['experiences'].append({'start_date': course_details.start_date.strftime('%d %^b %Y'),
                                           'end_date': course_details.end_date.strftime('%d %^b %Y'),
                                           'ACE_identifier': military_obj.ACE_identifier,
                                           'rank': military_obj.rank,
                                           'rank_level': military_obj.rank_level,
                                           'course_id': military_obj.experience_id,
                                           'course_name': course_name,
                                           'occupation_name': military_obj.experience_name,
                                           'description': military_obj.description,
                                           'areas' : area,
                                           'hours': hours,
                                           'level': level})

        return context


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

        # version = self.kwargs['version']

        transcript = get_object_or_404(self.queryset, pk=pk)

        if not request.user.has_perm('generate_transcript.view_transcript',
                                     transcript):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        # Create a PDF view
        # if re.search("legacy", version, re.IGNORECASE):
        #     pdf_view = TranscriptPDFView.as_view(template_name='legacyTranscript.html')
        # else:
        pdf_view = TranscriptPDFView.as_view(template_name='modernizedTranscript.html')

        user = MMTUser.objects.get(email=request.user)
        recipient_status_obj = TranscriptStatus.objects.filter(transcript=transcript, recipient=user).first()
        receiver=user.last_name + ", " + user.first_name

        if recipient_status_obj:
            recipient_status_obj.status = TranscriptStatus.STATUS.Opened
            recipient_status_obj.save()

        group_list = list(user.groups.all())

        for group in group_list:
            academic_group = (group.academic_institutes.all().first() 
                              if group.academic_institutes.all().first() 
                              else group.managing.all().first())
            group_status_obj = TranscriptStatus.objects.filter(transcript=transcript, academic_institute=academic_group).first()
            if group_status_obj:
                group_status_obj.status = TranscriptStatus.STATUS.Opened
                group_status_obj.save()

        context = {'first_name': transcript.subject.first_name,
                   'last_name': transcript.subject.last_name,
                   'dob': transcript.subject.dob.strftime('%d %^b %Y'),
                   'ssn': transcript.subject.ssn,
                   'rank': transcript.subject.rank,
                   'status': transcript.subject.status,
                   'date': datetime.today().strftime('%d %^b %Y'),
                   'branch': transcript.subject.branch,
                   'receiver' : receiver}

        return pdf_view(request, context=context, transcript=transcript)


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
                recipient_user = get_object_or_404(MMTUser, id=recipient_pk)

            elif ai_pk:
                recipient_user = (get_object_or_404(AcademicInstitute, id=ai_pk)).group

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
