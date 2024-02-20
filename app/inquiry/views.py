import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as filter
from rest_framework import mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_guardian import filters

from inquiry.serializer import (InquiryCommentSerializer, InquiryFAQSerializer,
                                InquirySerializer)

from .models import Inquiry, InquiryComment, InquiryFAQ

logger = logging.getLogger(__name__)


# Create your views here.


class InquiryPagination(PageNumberPagination):
    page_size = 5


class InquiryFAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InquiryFAQ.objects.filter(status='Active')
    serializer_class = InquiryFAQSerializer
    filter_backends = [filter.SearchFilter, filter.OrderingFilter]
    search_fields = ['issue', 'response']
    ordering_fields = ['created']


class InquiryCommentViewSet(viewsets.ReadOnlyModelViewSet,
                            mixins.CreateModelMixin):
    queryset = InquiryComment.objects.all()
    serializer_class = InquiryCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.ObjectPermissionsFilter,
                       filter.SearchFilter, filter.OrderingFilter]
    filterset_fields = ['poster', ]
    search_fields = ['inquiry', 'comment']
    ordering_fields = ['-created']

    def create(self, request, *args, **kwargs):
        inquiry_pk = request.data.get('inquiry')
        inquiry = Inquiry.objects.get(pk=inquiry_pk)
        if not (request.user.has_perm('inquiry.change_inquiry', inquiry)):
            return Response({'detail': 'You do not have permission'
                            ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class InquiryViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    pagination_class = InquiryPagination
    filter_backends = [DjangoFilterBackend, filters.ObjectPermissionsFilter,
                       filter.SearchFilter, filter.OrderingFilter]
    filterset_fields = ['id', 'status', 'inquiry_type']
    search_fields = ['subject', 'description']
    ordering_fields = ['created']

    def update(self, request, *args, **kwargs):
        inquiry_pk = request.data.get('id')
        inquiry = Inquiry.objects.get(pk=inquiry_pk)
        if not (request.user.has_perm('inquiry.change_inquiry', inquiry)):
            return Response({'detail': 'You do not have permission'
                            ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        inquiry_pk = request.data.get('id')
        inquiry = Inquiry.objects.get(pk=inquiry_pk)
        if not (request.user.has_perm('inquiry.change_inquiry', inquiry)):
            return Response({'detail': 'You do not have permission'
                            ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)
