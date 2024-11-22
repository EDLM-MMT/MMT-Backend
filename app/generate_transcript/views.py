import logging
import random
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


class RandomPDFView(PDFView):
    """Randomly generates PDFs to test behavior"""
    template_name = 'modernizedTranscript.html'
    download_name = 'resume'
    # prompt_download = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        # num = random.randint(50, 100)
        # for i in range(num):
        #     context['items'].append(
        #         {'first': '1', 'second': 'two', 'third': i})
        context = kwargs['context']
        context['image'] = "/static/EducationLogo1.png"
        context['experiences'] = []
        context['experiences']
        

        # logger.error(kwargs['transcript'].subject.militarycourse_set.all())        

        for military_obj in kwargs['transcript'].subject.militarycourse_set.all():
            # military_user_obj = list(military_obj.militarycourse_user.all())
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

            context['experiences'].append({'start_date': course_details.start_date.strftime('%d %^b %Y'),
                                           'end_date': course_details.end_date.strftime('%d %^b %Y'),
                                           'ACE_identifier': military_obj.ACE_identifier,
                                           'course_id': military_obj.course_id,
                                           'course_name': military_obj.course_name,
                                           'areas' : area,
                                           'hours': hours,
                                           'level': level})

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
    context['image'] = "/static/EducationLogo.png"

    return render(request=request, template_name='modernizedTranscript.html', context=context)


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

        user = MMTUser.objects.get(email=request.user)

        # logger.error(transcript)
        # logger.error(user)

        recipient_status_obj = TranscriptStatus.objects.filter(transcript=transcript, recipient=user).first()

        # logger.error(recipient_status_obj)

        if recipient_status_obj:
            logger.error("here")
            recipient_status_obj.status = TranscriptStatus.STATUS.Opened
            recipient_status_obj.save()

        group_list = list(user.groups.all())

        for group in group_list:
            for academic_institute in group.academic_institutes.all():
                group_status_obj = TranscriptStatus.objects.filter(transcript=transcript, academic_institute=academic_institute).first()
                if group_status_obj:
                    group_status_obj.status = TranscriptStatus.STATUS.Opened
                    group_status_obj.save()
            # logger.error(group.academic_institutes.all())

        # Create a PDF view
        pdf_view = RandomPDFView.as_view()

        context = {'name': transcript.subject.name,
                   'dob': transcript.subject.dob.strftime('%d %^b %Y'),
                   'ssn': transcript.subject.ssn,
                   'rank': transcript.subject.rank,
                   'status': transcript.subject.status,
                   'date': datetime.today().strftime('%d %^b %Y'),
                   'branch': transcript.subject.branch}

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
