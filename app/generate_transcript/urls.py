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

urlpatterns = [
    path('', include(router.urls)),
]
