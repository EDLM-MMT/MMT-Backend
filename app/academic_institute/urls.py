from django.urls import include, path
from rest_framework.routers import DefaultRouter

from academic_institute import views

app_name = 'academic_institute'
router = DefaultRouter()
router.register(r'academic-institutes', views.AcademicInstituteViewSet,
                basename='academic-institute')
router.register(r'manage-academic-institutes',
                views.ManageAcademicInstituteViewSet,
                basename='manage-academic-institute')
urlpatterns = [
    path('', include(router.urls)),
]
