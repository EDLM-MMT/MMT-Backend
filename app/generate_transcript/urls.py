from django.urls import path
from rest_framework.routers import DefaultRouter

from generate_transcript import views

router = DefaultRouter()

app_name = 'generate_transcript'
urlpatterns = [
    path('html-test', views.html_view, name='html-ver'),
    path('test', views.RandomPDFView.as_view(), name='pdf-ver'),
]
