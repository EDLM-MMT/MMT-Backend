import logging
import os
import re
from datetime import datetime

import boto3
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_renderpdf.views import PDFView
from guardian.shortcuts import assign_perm
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_guardian import filters

from academic_institute.models import AcademicInstitute
from generate_transcript.filters import (BranchFilter, RecentFilter,
                                         StatusFilter, UserExperiencesFilter)
from generate_transcript.models import (AreasAndHour, MetricEvent,
                                        MilitaryCourse_User, Transcript,
                                        TranscriptStatus)
from generate_transcript.serializers import (AreasAndHourSerializer,
                                             MilitaryCourseUserSerializer,
                                             TranscriptSerializer,
                                             TranscriptStatusSerializer)
from users.models import MMTUser

logger = logging.getLogger(__name__)

DATE_TIME = '%d-%^b-%Y'


def set_areas_hours(area_hour_details, course_details, area, hours, level):
    """ Set areas, hours, level based on date range """
    ace_id = area_hour_details.first().ace_identifier \
        if area_hour_details.exists() else None

    for areas_hours_obj in area_hour_details:

        check_date_range_flag = True

        if areas_hours_obj.start_date and \
            course_details.start_date and \
            course_details.start_date < \
                areas_hours_obj.start_date:
            check_date_range_flag = False
        if areas_hours_obj.end_date and \
            course_details.end_date and \
            areas_hours_obj.end_date and \
            course_details.end_date > \
                areas_hours_obj.end_date:
            check_date_range_flag = False

        if check_date_range_flag:
            area.append(areas_hours_obj.academic_course_area)
            hours.append(areas_hours_obj.hours)
            level.append(areas_hours_obj.level)

    return area, hours, level, ace_id


class AreasAndHourViewSet(viewsets.ReadOnlyModelViewSet,
                          mixins.CreateModelMixin):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = AreasAndHour.objects.all()
    serializer_class = AreasAndHourSerializer

    def list(self, request, *args, **kwargs):
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if bucket_name:
            s3 = boto3.resource('s3')
            try:
                objects = list(s3.Bucket(bucket_name).objects.all())
                print("Downloading objects in bucket:")
                for obj in objects:
                    print(f"- {obj.key}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error accessing bucket: {e}")
        return super().list(request, *args, **kwargs)


class TranscriptPDFView(PDFView):
    """ Generates PDFs for Transcripts"""

    download_name = 'resume'

    def get_context_data(self, *args, **kwargs):
        context = kwargs['context']
        context['experiences'] = []
        context['tests'] = []

        for course_details in kwargs['transcript']. \
                subject.militarycourse_user.all().order_by("-end_date",
                                                           "-start_date"):
            military_obj = course_details.course_id

            if hasattr(military_obj, 'militarycourse') and \
                    hasattr(military_obj.militarycourse, 'militarytestresult'):
                result = military_obj.militarycourse.militarytestresult
                if course_details.score and \
                        course_details.score >= result.passing:
                    context['tests'].append({
                        'date':
                        course_details.start_date.strftime('%d-%^b-%Y'),
                        'name': result.experience_name,
                        'credit': result.hours,
                        'ace_score': result.passing,
                        'actual_score': course_details.score,
                        'type': result.test_type
                    })
                continue

            area = []
            hours = []
            level = []

            area_hour_details = AreasAndHour.objects.filter(
                military_course=military_obj.id)

            area, hours, level, ace_id = \
                set_areas_hours(area_hour_details, course_details,
                                area, hours, level)

            context['experiences'].append(
                {'start_date': course_details.start_date.strftime(DATE_TIME)
                 if course_details.start_date else "-",
                 'end_date':
                 course_details.end_date.strftime(
                     DATE_TIME) if course_details.end_date else "PRESENT",
                 'ACE_identifier': ace_id.ace_identifier if ace_id else
                    "None Assigned",
                 'rank': military_obj.rank,
                 'rank_level': military_obj.rank_level,
                 'course_id': military_obj.experience_id,
                 'course': hasattr(military_obj, 'militarycourse'),
                 'occupation_name': military_obj.
                 experience_name,
                 'description': military_obj.description,
                 'areas': area,
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

    def retrieve(self, request, pk=None):

        basename = self.basename

        transcript = get_object_or_404(self.queryset, pk=pk)

        # if user does not:
        # have the general override
        # or have direct access
        # or have a service override for the correct branch
        # then return 403
        if not (
                request.user.has_perm('generate_transcript.view_transcript_override') or
            request.user.has_perm('generate_transcript.view_transcript', transcript) or
            (
                request.user.has_perm(
                    'generate_transcript.view_service_transcript_override')
                and not request.user.is_superuser and
                hasattr(request.user, 'user_record') and
                transcript.subject.branch == request.user.user_record.branch
                )):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        # Create a PDF view
        if re.search("transcript-legacy", basename, re.IGNORECASE):
            pdf_view = TranscriptPDFView.as_view(
                template_name='legacyTranscript.html')
            MetricEvent.objects.create(event=MetricEvent.Events.LEGACY_ACCESSED,
                                       initiator=request.user,
                                       transcript=transcript)
        elif re.search("transcript-vmet", basename, re.IGNORECASE):
            pdf_view = TranscriptPDFView.as_view(
                template_name='vmetTranscript.html')
            MetricEvent.objects.create(event=MetricEvent.Events.VMET_ACCESSED,
                                       initiator=request.user,
                                       transcript=transcript)
        else:
            pdf_view = TranscriptPDFView.as_view(
                template_name='modernizedTranscript.html')
            MetricEvent.objects.create(event=MetricEvent.Events.MMT_ACCESSED,
                                       initiator=request.user,
                                       transcript=transcript)

        recipient_status_obj = TranscriptStatus.objects.filter(
            transcript=transcript, recipient=request.user).first()
        receiver = request.user.last_name + ", " + request.user.first_name

        if recipient_status_obj:
            recipient_status_obj.status = TranscriptStatus.STATUS.Opened
            recipient_status_obj.save()

        group_list = list(request.user.groups.all())

        for group in group_list:
            academic_group = (group.academic_institutes.all().first()
                              if group.academic_institutes.all().first()
                              else group.managing.all().first())
            group_status_obj = TranscriptStatus.objects.filter(
                transcript=transcript,
                academic_institute=academic_group).first()
            if group_status_obj:
                group_status_obj.status = TranscriptStatus.STATUS.Opened
                group_status_obj.save()

        # setting SSN Value
        ssn = str(transcript.subject.ssn)[-4:]
        ssn = "***-**-"+ssn

        context = {'first_name': transcript.subject.first_name,
                   'last_name': transcript.subject.last_name,
                   'dob': transcript.subject.dob.strftime(DATE_TIME),
                   'ssn': ssn,
                   'rank': transcript.subject.rank,
                   'status': transcript.subject.status,
                   'date': datetime.today(),
                   'branch': transcript.subject.branch,
                   'receiver': receiver,
                   'transcript_type': "UNOFFICIAL" if
                   transcript.subject.user_profile == request.user
                   else "OFFICIAL"}

        return pdf_view(request, context=context, transcript=transcript)


class TranscriptStatusViewSet(viewsets.ModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = TranscriptStatus.objects.all().order_by('-created')
    serializer_class = TranscriptStatusSerializer
    filter_backends = [filters.ObjectPermissionsFilter,
                       StatusFilter, BranchFilter, RecentFilter]

    def create(self, request, *args, **kwargs):
        ssn = request.data.get('ssn')
        recipient_pk = request.data.get('recipient')
        ai_pk = request.data.get('academic_institute')

        if ssn:
            transcript = get_object_or_404(Transcript, subject__ssn=ssn)
        else:
            transcript = Transcript.objects.filter(
                subject__user_profile=request.user).first()

        request.data["transcript"] = transcript.id

        if request.user == transcript.subject.user_profile:
            if recipient_pk:
                recipient_user = get_object_or_404(MMTUser, email=recipient_pk)

            elif ai_pk:
                recipient_user = (get_object_or_404(
                    AcademicInstitute, id=ai_pk)).group

            else:
                return Response({'detail': "No target set"},
                                status=status.HTTP_400_BAD_REQUEST)

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
                # Handle other IntegrityError cases
                logger.error("Other IntegrityError occurred: %s", e)
                return Response({'detail': "Other IntegrityError, " +
                                 "check logs for details"},
                                status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class OccupationUpdatesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions
    """
    queryset = MilitaryCourse_User.objects.all().filter(
        course_id__militarycourse=None).order_by('-created')
    serializer_class = MilitaryCourseUserSerializer
    filter_backends = [UserExperiencesFilter, RecentFilter]


class CourseUpdatesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions
    """
    queryset = MilitaryCourse_User.objects.all().exclude(
        course_id__militarycourse=None).filter(
        course_id__militarycourse__militarytestresult=None).order_by(
            '-created')
    serializer_class = MilitaryCourseUserSerializer
    filter_backends = [UserExperiencesFilter, RecentFilter]


class AdditionalUpdatesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions
    """
    queryset = MilitaryCourse_User.objects.all().exclude(
        course_id__militarycourse=None).exclude(
        course_id__militarycourse__militarytestresult=None).order_by(
            '-created')
    serializer_class = MilitaryCourseUserSerializer
    filter_backends = [UserExperiencesFilter, RecentFilter]


class TriggerACETaskView(viewsets.ViewSet):
    """
    View to trigger ACE indexing task
    """

    # Override to use simple permissions
    permission_classes = [IsAuthenticated]

    def list(self, request):
        from generate_transcript.tasks import ace_data_workflow
        ace_data_workflow.delay()
        return Response({'detail': 'ACE Indexing Task Triggered'},
                        status=status.HTTP_200_OK)
