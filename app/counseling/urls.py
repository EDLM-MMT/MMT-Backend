from counseling import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'career-plan', views.CareerPlanViewSet,
                basename='career-plan')
router.register(r'comment', views.CommentViewSet,
                basename='comment')
router.register(r'eso-note', views.ESONoteViewSet,
                basename='eso-note')
router.register(r'course-plan', views.CoursePlanViewSet,
                basename='course-plan')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
