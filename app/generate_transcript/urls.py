from django.urls import include, path
from generate_transcript import views
from rest_framework.routers import DefaultRouter

# Create a router and register our ViewSets with it.
router = DefaultRouter()

app_name = 'generate_transcript'
router.register(r'transcript-status', views.TranscriptStatusViewSet,
                basename='transcript-status')
router.register(r'transcript', views.TranscriptViewSet,
                basename='transcript')
urlpatterns = [
    path('', include(router.urls)),
    path('html-test', views.transcript_html_view, name='html-ver'),
    path('test', views.RandomPDFView.as_view(), name='pdf-ver'),
]
