from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .admin_view import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'database', DatabaseListViewset)
router.register(r'database/detail', DatabaseRetrieveViewset)
router.register(r'announcement', AnnouncementViewset)
router.register(r'announcement/detail', AnnouncementRetrieveViewset)
router.register(r'admin/user',UserViewset)
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('feedback',create_feedback),
    # path('register')
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]