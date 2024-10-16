from counseling.models import CareerPlan, Comment, CoursePlan, ESONote
from counseling.serializers import (CareerPlanSerializer, CommentSerializer,
                                    CoursePlanSerializer, ESONoteSerializer)
from django.db.models import Prefetch
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework_guardian import filters


# Create your views here.
class CareerPlanViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin,
                        mixins.UpdateModelMixin):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = CareerPlan.objects.all()
    serializer_class = CareerPlanSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def get_queryset(self):
        """Restrict access to ESO Notes"""
        return super().get_queryset().prefetch_related(
            Prefetch('eso_notes',
                     filters.ObjectPermissionsFilter().filter_queryset(
                         self.request, ESONote.objects.all(), self)))

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.email
        request.data['eso'] = request.user.eso_default.email
        return super().create(request, *args, **kwargs)


class CommentViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def create(self, request, *args, **kwargs):
        plan_pk = request.data.get('plan')
        plan = CareerPlan.objects.get(pk=plan_pk)
        if not request.user.has_perm('counseling.change_careerplan', plan):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class ESONoteViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = ESONote.objects.all()
    serializer_class = ESONoteSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def create(self, request, *args, **kwargs):
        plan_pk = request.data.get('plan')
        plan = CareerPlan.objects.get(pk=plan_pk)
        if not request.user.has_perm('counseling.change_careerplan', plan) or\
                request.user == plan.owner.user_profile:
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class CoursePlanViewSet(viewsets.ModelViewSet):
    """
    Viewset that only lists events if user has 'view' permissions, and only
    allows operations on individual events if user has appropriate 'view',
    'add', 'change' or 'delete' permissions.
    """
    queryset = CoursePlan.objects.all()
    serializer_class = CoursePlanSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def create(self, request, *args, **kwargs):
        plan_pk = request.data.get('plan')
        plan = CareerPlan.objects.get(pk=plan_pk)
        if not request.user.has_perm('counseling.change_careerplan', plan):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)
        if request.user == plan.owner.user_profile:
            request.data['approved'] = False
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        plan = instance.plan
        if request.user == plan.owner.user_profile:
            request.data['approved'] = instance.approved
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        plan = instance.plan
        if request.user == plan.owner.user_profile and\
                'approved' in request.data:
            request.data['approved'] = instance.approved
        return super().partial_update(request, *args, **kwargs)
