from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .admin_view import *
from .router import DeleteListRouter
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'database', DatabaseListViewset)
router.register(r'database/detail', DatabaseRetrieveViewset)
router.register(r'announcement', AnnouncementViewset)
router.register(r'announcement/detail', AnnouncementRetrieveViewset)
router.register(r'admin/user',UserViewset)
router.register(r'admin/subject',DatabaseSubjectAdminViewset)
router.register(r'admin/source',DatabaseSourceAdminViewset)
router.register(r'admin/category',DatabaseCategoryAdminViewset)
router.register(r'admin/database',DatabaseAdminViewset)
router.register(r'admin/databaseVist',DatabaseVisitAdminViewset)
router.register(r'admin/feedback',FeedbackAdminViewset)
router.register(r'admin/announcement',AnnouncementAdminViewset)
router.register(r'admin/anTag',AnnouncementTagViewset)
router.register(r'admin/announcementVisit',AnnouncementVisitAdminViewset)
router2 = DeleteListRouter()
router2.register(r'admin/media',FileManagement)

# router.register(r'admin/media/file',File)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(router2.urls)),
    path('feedback',FeedbackView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]