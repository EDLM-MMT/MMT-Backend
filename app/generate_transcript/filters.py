from datetime import datetime, timedelta

from rest_framework import filters

from generate_transcript.models import TranscriptStatus


class RecentFilter(filters.BaseFilterBackend):
    """
    Filter that limits queryset to objects that have been created in
    the past 30 days
    """

    def filter_queryset(self, request, queryset, view):
        if 'recent' in request.query_params:
            return queryset.filter(
                created__gt=datetime.utcnow() - timedelta(days=31))
        return queryset


class StatusFilter(filters.SearchFilter):
    """
    Search the status field on Transcript Status
    """
    search_param = 'status'
    search_title = 'Search Status'
    search_description = 'A status of: ' + \
        str({i[0] for i in TranscriptStatus.STATUS})

    def get_search_fields(self, view, request):
        return ['=status', ]


class BranchFilter(filters.SearchFilter):
    """
    Search the branch of an associated Transcript Status
    """
    search_param = 'branch'
    search_title = 'Search Branch'
    search_description = 'The service branch of a user'

    def get_search_fields(self, view, request):
        return ['=transcript__subject__branch', ]


class UserExperiencesFilter(filters.BaseFilterBackend):
    """
    Filter that limits queryset to objects associated with the user's
    user record or limits it to no objects
    """

    def filter_queryset(self, request, queryset, view):
        if request.user.user_record:
            return queryset.filter(user_id=request.user.user_record)
        return queryset.none()
