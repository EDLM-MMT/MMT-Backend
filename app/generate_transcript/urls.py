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
router.register(r'AreasAndHour',
                views.AreasAndHourViewSet,
                basename='areasandhours')
router.register(r'AcademicCourseArea',
                views.AcademicCourseAreaViewSet,
                basename='academiccoursearea')
router.register(r'MilitaryCourse',
                views.MilitaryCourseViewSet,
                basename='militarycourse')
urlpatterns = [
    path('', include(router.urls)),
]
