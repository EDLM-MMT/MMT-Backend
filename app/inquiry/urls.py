from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inquiry import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'inquiry', views.InquiryViewSet,
                basename='inquiry')
router.register(r'inquiryComment', views.InquiryCommentViewSet,
                basename='inquiryComment')
router.register(r'inquiryFAQ', views.InquiryFAQViewSet,
                basename='inquiryFAQ')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
