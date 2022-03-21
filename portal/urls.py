from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'database', DatabaseListViewset)
router.register(r'database/detail', DatabaseRetrieveViewset)
router.register(r'announcement', AnnouncementViewset)
router.register(r'announcement/detail', AnnouncementRetrieveViewset)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('feedback',create_feedback)
]