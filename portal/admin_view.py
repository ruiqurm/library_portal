from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from .models import *
from .serializers import *
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet


class UserViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = (
        'is_superuser',
        'is_active',
        "username",
    )
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-User'],
    )

    def list(self, request, *args, **kwargs):
        """
        获取所有用户

        支持分页和筛选
        """
        return super(UserViewset, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        获取id=?的用户
        """
        return super(UserViewset, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        更新id=?的用户的信息

        如果是局部更改，需要传入partial=True
        """
        return super(UserViewset, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        销毁一个用户
        """
        return super(UserViewset, self).destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        创建一个用户
        """
        data = dict(request.data)
        data["is_stuff"] = True
        data["is_active"] = True

        save_data = UserCreateSerializer(data=data)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        return Response(status=201)

    @action(methods=["POST"], detail=False, url_path="change_password", permission_classes=(IsAuthenticated,))
    def change_password(self, request, *args, **kwargs):
        """
        修改密码
        """
        user: MyUser = request.user
        password = str(request.data.get("password"))
        if len(password) > 128:
            raise ValidationError("密码太长")
        user.password = make_password(password)
        user.save()
        return Response()

    @action(methods=["GET"], detail=False, url_path="me", permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """
        查看用户自己的信息
        """
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    # @action(methods=["POST"], detail=False, url_path="edit",permission_classes=(IsAuthenticated,))
    # def upload_avatar(self,request,*args,**kwargs):
    #     """
    #     上传头像
    #     """
    #     pass
    @action(methods=["POST"], detail=False, url_path="edit", permission_classes=(IsAuthenticated,))
    def edit(self, request, *args, **kwargs):
        """
        更新用户自己的信息
        """
        user: MyUser = request.user
        data = dict(request.data)
        data.pop("password", None)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(user, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            user._prefetched_objects_cache = {}

        return Response(serializer.data)


class DatabaseSubjectAdminViewset(ModelViewSet):
    queryset = DatabaseSubject.objects.all()
    serializer_class = DatabaseSubjectSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class DatabaseSourceAdminViewset(ModelViewSet):
    queryset = DatabaseSource.objects.all()
    serializer_class = DatabaseSourceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class DatabaseCategoryAdminViewset(ModelViewSet):
    queryset = DatabaseCategory.objects.all()
    serializer_class = DatabaseCategorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class DatabaseAdminViewset(ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class DatabaseVisitAdminViewset(ModelViewSet):
    queryset = DatabaseVisit.objects.all()
    serializer_class = DatabaseVisitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class FeedbackAdminViewset(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class AnnouncementAdminViewset(ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )

class AnnouncementVisitAdminViewset(ModelViewSet):
    queryset = AnnouncementVisit.objects.all()
    serializer_class = AnnouncementVisitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin'],
    )