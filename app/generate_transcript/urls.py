from django.urls import include, path
from rest_framework.routers import DefaultRouter

from generate_transcript import views

app_name = 'generate_transcript'
router = DefaultRouter()

router.register(r'transcript-status', views.TranscriptStatusViewSet,
                basename='transcript-status')
router.register("transcript/legacy",
                views.TranscriptViewSet,
                basename='transcript-legacy')
router.register(r'transcript',
                views.TranscriptViewSet,
                basename='transcript')
router.register(r'occupation-updates', views.OccupationUpdatesViewSet,
                basename='occupation-updates')
router.register(r'course-updates', views.CourseUpdatesViewSet,
                basename='course-updates')
router.register(r'additional-updates', views.AdditionalUpdatesViewSet,
                basename='additional-updates')

urlpatterns = [
    path('', include(router.urls)),
]
