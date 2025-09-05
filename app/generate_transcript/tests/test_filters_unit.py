from datetime import datetime, timedelta, timezone
from django.test import TestCase
from django.test import tag

from generate_transcript.filters import (
    RecentFilter,
    StatusFilter,
    BranchFilter,
    UserExperiencesFilter
)
from generate_transcript.models import TranscriptStatus


class DummyQuerySet:
    """
    A minimal stand-in for a Django QuerySet that records filter
    kwargs and supports none().
    """
    def __init__(self):
        self.filters = None

    def filter(self, **kwargs):
        self.filters = kwargs
        return self

    def none(self):
        return 'EMPTY'


class DummyUser:
    """Stand-in user with an optional user_record attribute."""
    def __init__(self, user_record=None):
        self.user_record = user_record


class DummyRequest:
    """Stand-in request carrying query_params and a user."""
    def __init__(self, query_params=None, user=None):
        self.query_params = query_params or {}
        self.user = user


@tag('unit')
class FilterTests(TestCase):
    def test_recent_filter_without_recent_param(self):
        """
        If 'recent' is not in query_params, RecentFilter should
        return the original queryset unmodified.
        """
        rf = RecentFilter()
        qs = DummyQuerySet()
        request = DummyRequest(query_params={})
        result = rf.filter_queryset(request, qs, view=None)

        self.assertIs(result, qs)
        self.assertIsNone(qs.filters)

    def test_recent_filter_with_recent_param(self):
        """
        If 'recent' is in query_params, RecentFilter should apply
        a filter on 'created__gt' within the past ~31 days.
        """
        rf = RecentFilter()
        qs = DummyQuerySet()
        request = DummyRequest(query_params={'recent': 'true'})
        result = rf.filter_queryset(request, qs, view=None)

        self.assertIs(result, qs)
        self.assertIn('created__gt', qs.filters)

        dt_value = qs.filters['created__gt']

        # Make now timezone-aware to match RecentFilter
        now = datetime.now(timezone.utc)
        expected_min = now - timedelta(days=32)
        expected_max = now - timedelta(days=30)

        # Convert both to UTC-aware (if dt_value might be naive)
        if dt_value.tzinfo is None:
            dt_value = dt_value.replace(tzinfo=timezone.utc)

        self.assertTrue(expected_min <= dt_value <= expected_max,
                        f"Filter date {dt_value} not within expected range")

    def test_status_filter_attributes_and_search_fields(self):
        """
        Verify StatusFilter metadata and that get_search_fields
        returns ['=status'].
        """
        sf = StatusFilter()
        self.assertEqual(sf.search_param, 'status')
        self.assertEqual(sf.search_title, 'Search Status')
        # Ensure description mentions the set of STATUS codes
        status_codes = {i[0] for i in TranscriptStatus.STATUS}
        self.assertIn(str(status_codes), sf.search_description)
        self.assertEqual(sf.get_search_fields(view=None, request=None),
                         ['=status'])

    def test_branch_filter_attributes_and_search_fields(self):
        """
        Verify BranchFilter metadata and that get_search_fields
        returns the correct lookup for transcript__subject__branch.
        """
        bf = BranchFilter()
        self.assertEqual(bf.search_param, 'branch')
        self.assertEqual(bf.search_title, 'Search Branch')
        self.assertEqual(
            bf.get_search_fields(view=None, request=None),
            ['=transcript__subject__branch']
        )

    def test_user_experiences_filter_with_user_record(self):
        """
        If request.user.user_record is truthy, filter_queryset should
        pass that record into user_id.
        """
        uf = UserExperiencesFilter()
        qs = DummyQuerySet()
        user = DummyUser(user_record=123)
        request = DummyRequest(user=user)

        result = uf.filter_queryset(request, qs, view=None)

        self.assertIs(result, qs)
        self.assertEqual(qs.filters, {'user_id': 123})

    def test_user_experiences_filter_without_user_record(self):
        """
        If request.user.user_record is falsy, filter_queryset should
        return qs.none().
        """
        uf = UserExperiencesFilter()
        qs = DummyQuerySet()
        user = DummyUser(user_record=None)
        request = DummyRequest(user=user)

        result = uf.filter_queryset(request, qs, view=None)

        self.assertEqual(result, 'EMPTY')
