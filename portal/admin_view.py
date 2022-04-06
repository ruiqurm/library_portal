import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView as _TokenObtainPairView,
    TokenRefreshView as _TokenRefreshView,
    TokenVerifyView as _TokenVerifyView
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *


class TokenObtainPairView(_TokenObtainPairView):
    """
    获取一个token
    需要username 和 password
    返回一个token和一个refresh。后者用来刷新

    使用时，在header上设置{Authorization:Bearer [token]}
    """
    pass


class TokenRefreshView(_TokenRefreshView):
    """
    刷新token。

    需要提供refresh token.

    返回一组新的token
    """
    pass


class UserViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = (
        'is_superuser',
        'is_active',
        "username",
    )
    authentication_classes = (JWTAuthentication,)
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
        需要的字段：username,password

        密码最小长度为8，最大长度为128
        目前只能由管理员创建。
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
        密码最小长度为8，最大长度为128
        """
        user: MyUser = request.user
        password = str(request.data.get("password"))
        if len(password) > 128:
            raise ValidationError("密码太长")
        elif len(password) < 8:
            raise ValidationError("密码太短")
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

    @action(methods=["POST","UPDATE"], detail=False, url_path="edit", permission_classes=(IsAuthenticated,))
    def edit(self, request, *args, **kwargs):
        """
        更新用户自己的信息
        不能改密码。
        对`is_superuser`,`username`,`password`,`is_active`的修改无效
        `头像`大小小于4MB
        """
        user: MyUser = request.user
        data = dict(request.data)
        data.pop("password", None)
        data.pop("username", None)
        data.pop("is_active", None)
        data.pop("is_superuser", None)
        if "avatar" in data and isinstance(data["avatar"],list):
            data["avatar"] = data["avatar"][0]
        serializer = self.get_serializer(user, data=data, partial=True)
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
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Databasesubject'],
    )


class DatabaseSourceAdminViewset(ModelViewSet):
    queryset = DatabaseSource.objects.all()
    serializer_class = DatabaseSourceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-DatabaseSource'],
    )


class DatabaseCategoryAdminViewset(ModelViewSet):
    queryset = DatabaseCategory.objects.all()
    serializer_class = DatabaseCategorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    pagination_class = LimitOffsetPagination
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-DatabaseCategory'],
    )


class DatabaseAdminViewset(ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseAdminSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Database'],
    )


class DatabaseVisitAdminViewset(ModelViewSet):
    queryset = DatabaseVisit.objects.all()
    serializer_class = DatabaseVisitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-DatabaseVisit'],
    )


class FeedbackAdminViewset(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Feedback'],
    )


class AnnouncementAdminViewset(ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementAdminSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Announcement'],
        operation_id_base='announcementAdmin',
    )


class AnnouncementVisitAdminViewset(ModelViewSet):
    queryset = AnnouncementVisit.objects.all()
    serializer_class = AnnouncementVisitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = "__all__"
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-AnnouncementVisit'],
    )

from rest_framework.parsers import MultiPartParser,FormParser

class UploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = AutoSchema(
        tags=['Admin-Upload'],
    )
    def post(self,request:Request):
        """
        需要提供class,id和文件
        obj : `db` 或者 `an`
        id : 对应的数据库或者公告id
        file: 文件。对于图片，大小不超过20M，文件大小不超过50M
        type: `img`,`file`
        """
        if request.data:
            if "type" not in request.data:
                raise ValidationError("缺少type")
            if request.data["type"] == "img":
                serializer = UploadImageSerializer(data=request.data)
            elif request.data["type"] == "file":
                serializer = UploadFileSerializer(data=request.data)
            else:
                raise ValidationError("Unknow type")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            raise ValidationError("Not supported")

class ImageManagement(GenericViewSet, ListModelMixin, RetrieveModelMixin,DestroyModelMixin):
    queryset = Image.objects.all()
    serializer_class = FileSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("content_type","object_id")
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Upload'],
    )
class FileManagement(GenericViewSet, ListModelMixin, RetrieveModelMixin,DestroyModelMixin):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("content_type","object_id")
    authentication_classes = (JWTAuthentication,)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUser,)
    schema = AutoSchema(
        tags=['Admin-Upload'],
    )