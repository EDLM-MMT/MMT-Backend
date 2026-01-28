from datetime import datetime, timedelta

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from guardian.admin import GuardedModelAdmin

from academic_institute.models import AcademicInstitute
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        ACEIdentifier, AreasAndHour, Degree,
                                        MetricEvent, MilitaryCourse,
                                        MilitaryCourse_User,
                                        MilitaryExperience, MilitaryTestResult,
                                        Transcript, TranscriptMetrics,
                                        TranscriptStatus)
from users.models import UserRecord

# Register your models here.


@admin.register(MetricEvent)
class MetricEventAdmin(admin.ModelAdmin):
    list_display = ('initiator', 'event', 'transcript')
    search_fields = ('initiator__first_name',
                     'initiator__last_name', 'event',
                     'transcript__subject__first_name',
                     'transcript__subject__last_name')
    list_filter = ('event', 'created',)
    raw_id_fields = ['initiator', 'transcript',]


@admin.register(TranscriptMetrics)
class TranscriptMetricsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/generate_transcript/transcriptmetrics/transcript_metrics.html'
    TIMEFRAMES = [timedelta(days=30), timedelta(days=180), timedelta(days=365)]

    def context(self, request):
        # if have general override (or super user) don't filter
        if request.user.has_perm('generate_transcript.view_transcript_metric_override'):
            t_query = Transcript.objects.all()
            ts_query = TranscriptStatus.objects.all()
            ai_query = AcademicInstitute.objects.all()
            me_query = MetricEvent.objects.all()
            services = UserRecord.objects.order_by('branch').distinct('branch')
        # elif have service override filter by service
        elif request.user.has_perm('generate_transcript.view_service_transcript_metric_override')\
                and hasattr(request.user, 'user_record') and request.user.user_record.branch:
            t_query = Transcript.objects.filter(
                subject__branch__iexact=request.user.user_record.branch)
            ts_query = TranscriptStatus.objects.filter(
                transcript__subject__branch__iexact=request.user.user_record.branch)
            ai_query = AcademicInstitute.objects.filter(
                transcript_status__transcript__subject__branch__iexact=request.user.user_record.branch)
            me_query = MetricEvent.objects.filter(
                transcript__subject__branch__iexact=request.user.user_record.branch)
            services = [request.user.user_record,]
        # else show nothing
        else:
            t_query = Transcript.objects.none()
            ts_query = TranscriptStatus.objects.none()
            ai_query = AcademicInstitute.objects.none()
            me_query = MetricEvent.objects.none()
            services = []

        context = {
            'all_transcripts': t_query.count(),
            'unique_shared_transcripts': t_query.filter(
                transcriptstatus__isnull=False).distinct().count(),
            'shared_transcripts': ts_query.count(),
            'service_member_transcripts': ts_query.filter(
                transcript__subject__status__iexact='active').count(),
            'veteran_transcripts': ts_query.exclude(
                transcript__subject__status__iexact='active').count(),
            'ai_shares': ai_query.annotate(
                Count("transcript_status")
            ).order_by("-transcript_status__count").filter(transcript_status__count__gt=0),
            'services': {},
            'transcript_events': {}
        }

        # calculations for branches
        for ur in services:
            context['services'][ur.branch] = [ts_query.filter(
                transcript__subject__branch__iexact=ur.branch).count(),]
            context['services'][ur.branch].append(
                f"{context['services'][ur.branch][0] / context['shared_transcripts']*100:2.1f}" if context[
                    'shared_transcripts'] != 0 else "0.0")

        # calculations for Academic Institutes
        for ai in context['ai_shares']:
            ai.transcript_status__count_percent = \
                f"{ai.transcript_status__count / context['shared_transcripts']*100:2.1f}" if context[
                    'shared_transcripts'] != 0 else "0.0"

        # calculations for veteran, or not
        context['service_member_transcripts_percent'] = \
            f"{context['service_member_transcripts'] / context['shared_transcripts']*100:2.1f}" if context['shared_transcripts'] != 0 else "0.0"
        context['veteran_transcripts_percent'] = \
            f"{context['veteran_transcripts'] / context['shared_transcripts']*100:2.1f}" if context['shared_transcripts'] != 0 else "0.0"

        # transcript events (access specific versions of the transcript)
        self._events(me_query, services, context)

        return context

    def _events(self, me_query, services, context):
        for delta in self.TIMEFRAMES:
            me_time_query = me_query.filter(
                created__date__gt=datetime.today()-delta)
            context['transcript_events'][delta.days] = {}

            # for branches
            for ur in services:
                branch = ur.branch
                context['transcript_events'][delta.days][branch] = {}
                context['transcript_events'][delta.days][branch]['legacy'] = [me_time_query.filter(
                    transcript__subject__branch__iexact=branch,
                    event=MetricEvent.Events.LEGACY_ACCESSED).count(),]
                context['transcript_events'][delta.days][branch]['modern'] = [me_time_query.filter(
                    transcript__subject__branch__iexact=branch,
                    event=MetricEvent.Events.MMT_ACCESSED).count(),]
                context['transcript_events'][delta.days][branch]['vmet'] = [me_time_query.filter(
                    transcript__subject__branch__iexact=branch,
                    event=MetricEvent.Events.VMET_ACCESSED).count(),]
                format_sum = context['transcript_events'][delta.days][branch]['legacy'][0] + \
                    context['transcript_events'][delta.days][branch]['modern'][0] + \
                    context['transcript_events'][delta.days][branch]['vmet'][0]
                context['transcript_events'][delta.days][branch]['legacy'].append(
                    f"{context['transcript_events'][delta.days][branch]['legacy'][0] / format_sum*100:2.1f}" if format_sum != 0 else "0.0")
                context['transcript_events'][delta.days][branch]['modern'].append(
                    f"{context['transcript_events'][delta.days][branch]['modern'][0] / format_sum*100:2.1f}" if format_sum != 0 else "0.0")
                context['transcript_events'][delta.days][branch]['vmet'].append(
                    f"{context['transcript_events'][delta.days][branch]['vmet'][0] / format_sum*100:2.1f}" if format_sum != 0 else "0.0")

    def changelist_view(self, request, **kwargs):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        extra_context = kwargs['extra_context'] if 'extra_context' in\
            kwargs else {}
        extra_context.update(self.context(request))
        kwargs['extra_context'] = extra_context

        return super().changelist_view(request, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request).none()


class DegreeInline(admin.TabularInline):
    model = Degree
    fields = ('degree', 'mos',)
    extra = 3


class AreasAndHourInline(admin.TabularInline):
    model = AreasAndHour
    fields = ('degree', 'academic_course_area', 'ace_identifier',
              'hours', 'level', 'start_date', 'end_date')
    extra = 3
    raw_id_fields = ['degree', 'academic_course_area', 'ace_identifier',]


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(academiccourse=None)


@admin.register(ACEIdentifier)
class ACEIdentifierAdmin(admin.ModelAdmin):
    list_display = ('id', 'ace_identifier', )
    search_fields = ['ace_identifier',]


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course_area')


@admin.register(AreasAndHour)
class AreasAndHourAdmin(admin.ModelAdmin):
    list_display = ('academic_course_area', 'ace_identifier',
                    'military_course', 'hours', 'level',
                    'version')
    search_fields = ['academic_course_area__course_area',
                     'ace_identifier__ace_identifier']
    list_filter = ['ace_identifier__ace_identifier',]
    raw_id_fields = ['academic_course_area', 'ace_identifier',
                     'military_course', 'degree',]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "hours", "level", "version"
                )
            },
        ),
        (
            "Connections",
            {
                # on the same line
                "fields": (
                    "ace_identifier",
                    "academic_course_area",
                    "degree",
                    "military_course",
                )
            },
        ),
        (
            "Dates",
            {
                # on the same line
                "fields": (
                    "start_date",
                    "end_date",
                    "last_updated_on",
                )
            },
        ),
    )


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institute')
    list_filter = (('institute', admin.RelatedOnlyFieldListFilter),)
    inlines = [AreasAndHourInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "degree",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "institute",
                    "mos",
                )
            }
        ),
    )
    filter_horizontal = ("mos",)


@admin.register(MilitaryExperience)
class MilitaryExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id', 'experience_name', 'skill_level')
    search_fields = ('experience_name', 'experience_id',)
    inlines = [AreasAndHourInline,]

    filter_horizontal = ("user_id",)

    def get_queryset(self, request):
        """
        Only list Experiences, not subclasses
        """
        return super().get_queryset(request).filter(militarycourse__isnull=True)


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id', 'experience_name',
                    'skill_level', 'version')
    search_fields = ('experience_name', 'experience_id',)
    inlines = [AreasAndHourInline,]

    filter_horizontal = ("user_id",)

    def get_queryset(self, request):
        """
        Only list Courses, not subclasses
        """
        return super().get_queryset(request).filter(militarytestresult__isnull=True)


@admin.register(MilitaryTestResult)
class MilitaryTestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id', 'experience_name',
                    'skill_level', 'version', 'test_type',)
    search_fields = ('experience_name',)
    list_filter = ('test_type',)
    inlines = [AreasAndHourInline,]


@admin.register(Transcript)
class TranscriptAdmin(GuardedModelAdmin):
    list_display = ('subject', )
    fields = ['subject', ]

    def get_queryset(self, request):
        """
        Add filter based on permissions
        """
        from_super = super().get_queryset(request)
        # if have general override (or super user) don't filter
        if request.user.has_perm('generate_transcript.view_transcript_override'):
            return from_super
        # if has service override filter based on service
        if request.user.has_perm('generate_transcript.view_service_transcript_override'):
            if hasattr(request.user, 'user_record') and request.user.user_record.branch:
                return from_super.filter(subject__branch=request.user.user_record.branch)
        # otherwise return nothing
        return from_super.none()

    def has_module_permission(self, request):
        """
        Limit access to module
        """
        return request.user.has_perm('generate_transcript.view_transcript_override') or\
            request.user.has_perm(
                'generate_transcript.view_service_transcript_override')


@admin.register(TranscriptStatus)
class TranscriptStatusAdmin(GuardedModelAdmin):
    search_fields = ('transcript__subject__first_name',
                     'transcript__subject__last_name',
                     'recipient__first_name', 'recipient__last_name',
                     'academic_institute__institute', 'status')
    list_display = ('transcript', 'recipient', 'academic_institute', 'status')
    list_filter = ('status', 'modified', 'academic_institute')

    def get_queryset(self, request):
        """
        Add filter based on permissions
        """
        from_super = super().get_queryset(request)
        # if have general override (or super user) don't filter
        if request.user.has_perm('generate_transcript.view_transcript_status_override'):
            return from_super
        # if has service override filter based on service
        if request.user.has_perm('generate_transcript.view_service_transcript_status_override'):
            if hasattr(request.user, 'user_record') and request.user.user_record.branch:
                return from_super.filter(transcript__subject__branch=request.user.user_record.branch)
        # otherwise return nothing
        return from_super.none()

    def has_module_permission(self, request):
        """
        Limit access to module
        """
        return request.user.has_perm('generate_transcript.view_transcript_status_override') or\
            request.user.has_perm(
                'generate_transcript.view_service_transcript_status_override')


@admin.register(MilitaryCourse_User)
class MilitaryCourse_UserAdmin(GuardedModelAdmin):
    list_display = ('start_date', 'end_date', 'course_id', 'user_id',)
    list_filter = ('course_id', 'user_id',)
    raw_id_fields = ['course_id', 'user_id',]
