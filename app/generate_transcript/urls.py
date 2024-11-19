from django.urls import include, path
from rest_framework.routers import DefaultRouter

from generate_transcript import views

app_name = 'generate_transcript'
router = DefaultRouter()

router.register(r'transcript-status', views.TranscriptStatusViewSet,
                basename='transcript-status')
router.register(r'transcript', views.TranscriptViewSet,
                basename='transcript')
urlpatterns = [
    path('', include(router.urls)),
    path('html-test', views.transcript_html_view, name='html-ver'),
    path('test', views.RandomPDFView.as_view(), name='pdf-ver'),
]
