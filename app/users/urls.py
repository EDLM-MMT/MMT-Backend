from django.urls import path
from knox.views import LogoutAllView, LogoutView
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()

app_name = 'auth'

urlpatterns = [
    path('generate-key/',
         views.GenerateAPIKeyFromOtherAuthMethod.as_view(), name='gen-key'),
    path('delete-key/', LogoutView.as_view(), name='delete-key'),
    path('delete-all-keys/', LogoutAllView.as_view(),
         name='delete-all-keys'),
    path('validate', views.ValidateSession.as_view(), name='validate'),
]
