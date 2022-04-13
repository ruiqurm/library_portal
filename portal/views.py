from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from datetime import date

from .serializers import *


class DatabaseListFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__name", lookup_expr="iexact", label="分类名")
    source = filters.CharFilter(field_name="source__name", lookup_expr="iexact", label="来源")
    subject = filters.CharFilter(field_name="subject__name", lookup_expr='iexact', label="学科")
    first_letter = filters.CharFilter(method="filter_by_first_letter", label='第一个字母')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains', label='标题')
    content = filters.CharFilter(field_name="content", lookup_expr='icontains', label='内容')

    def filter_by_first_letter(self, queryset, name, value, *args, **kwargs):
        if len(value) == 1 and value.isalpha():
            return queryset.filter(name__istartswith=value)
        else:
            return queryset

    class Meta:
        model = Database
        fields = ['is_Chinese', 'is_on_trial']


class DatabaseListViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Database.objects.filter(is_available=True)
    serializer_class = DatabaseGeneralSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DatabaseListFilter
    pagination_class = LimitOffsetPagination
    schema = AutoSchema(
        tags=['Database'],
        operation_id_base='DatabaseGeneral',
    )

    def list(self, request, *args, **kwargs):
        """
        获取数据库的概要的列表（除数据库的内容外的字段）

        支持分页和筛选
        """
        return super(DatabaseListViewset, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        获取数据库id=?的概要
        """
        return super(DatabaseListViewset, self).retrieve(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="choice")
    def get_chocie(self, request, *args, **kwarg):
        """
        获取对应的选项。

        subject对应的是所有学科的列表，source是来源列表，category是种类列表
        """
        return Response({
            "subject": DatabaseSubjectSerializer(DatabaseSubject.objects.all(), many=True).data,
            "source": DatabaseSourceSerializer(DatabaseSource.objects.all(), many=True).data,
            "category": DatabaseCategorySerializer(DatabaseCategory.objects.all(), many=True).data
        })

    @action(methods=["GET"], detail=False, url_path="search")
    def search_database(self, request, *args, **kwarg):
        """
        搜索指定内容。会同时检索中文标题，英文标题，中文内容和英文内容。
        """
        queryset = self.filter_queryset(self.get_queryset())
        key = request.query_params.get("key", "")
        # if key is None:
        #     return Response({})
        results = queryset.filter(
            Q(name__icontains=key) | Q(name__icontains=key) | Q(content__icontains=key) | Q(
                content__icontains=key)).all()
        return Response(DatabaseGeneralSerializer(results, many=True).data)


class DatabaseRetrieveViewset(GenericViewSet, RetrieveModelMixin):
    queryset = Database.objects.filter(is_available=True)
    serializer_class = DatabaseSerializer
    lookup_field = "id"
    schema = AutoSchema(
        tags=['Database'],
        operation_id_base='databaseRetrieve',
    )

    def retrieve(self, request, *args, **kwargs):
        """
        获取数据库id=?的详情
        """
        return super(DatabaseRetrieveViewset, self).retrieve(request, *args, **kwargs)

    @action(methods=["GET"], detail=True, url_path="visit")
    def visit_database(self, request, id, **kwarg):
        """
        标记访问了该数据库

        每个ip只能标记一次，第二次访问会返回400
        """
        ip = request.META.get("REMOTE_ADDR")
        data = {"ip": ip, "database": id}
        # today = date.today()
        if DatabaseVisit.objects.filter(ip=ip).count() > 0:
            return Response({"msg": "You have visited the page"}, status=400)
        save_data = DatabaseVisitSerializer(data=data)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        return Response()




class FeedbackView(APIView):
    schema = AutoSchema(
        tags=['Feedback'],
        operation_id_base='FeedbackCreate',
    )

    def post(request: Request):
        """
        新建一个反馈

        每个ip每天可以新建2个反馈
        """
        data = dict(request.data)
        ip = request.META.get("REMOTE_ADDR")
        data["ip"] = ip
        today = date.today()
        if Feedback.objects.filter(create_time__year=today.year, create_time__month=today.month,
                                   create_time__day=today.day,
                                   ip=ip).count() > 2:
            return Response({"msg": "You can feedback at largest 3 times a day"}, status=403)
        save_data = FeedbackSerializer(data=data)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        return Response(save_data.data, status=201)


class AnnouncementFilter(filters.FilterSet):
    has_database = filters.CharFilter(method='_has_database', label="是否关联数据库")
    database_id = filters.CharFilter(method='_database_id', label="数据库id")
    search = filters.CharFilter(method='_search', label="搜索数据库")

    def _has_database(self, queryset: Announcement.objects.all(), name, value: str, *args, **kwargs):
        if value.lower() == "true":
            return queryset.filter(database__isnull=False)
        elif value.lower() == "false":
            return queryset.filter(database__isnull=True)
        else:
            return queryset

    def _search(self, queryset: Announcement.objects.all(), name, value: str, *args, **kwargs):
        if value is not None and value != "":
            return queryset.filter(
                Q(title__icontains=value) | Q(title__icontains=value) | Q(content__icontains=value) | Q(
                    content__icontains=value)).all()
        else:
            return queryset

    def _database_id(self, queryset: Announcement.objects.all(), name, value: str, *args, **kwargs):
        if value.isdigit():
            return queryset.filter(database_id=value)
        else:
            return queryset


class AnnouncementViewset(GenericViewSet, ListModelMixin,RetrieveModelMixin):
    queryset = Announcement.objects.filter(is_available=True)
    serializer_class = AnnouncementListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AnnouncementFilter
    pagination_class = LimitOffsetPagination
    schema = AutoSchema(
        tags=['Announcement'],
        operation_id_base='AnnouncementGeneral',
    )

    def list(self, request, *args, **kwargs):
        """
        获取公告的列表

        支持分页和筛选。每页限制最大为20

        过滤选项可以填null或者数字，数字表示数据库的id，null表示未连接数据库
        """
        return super(AnnouncementViewset, self).list(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="search")
    def search_announcement(self, request, *args, **kwarg):
        """
        搜索公告。搜中英文内容和标题。
        """


class AnnouncementRetrieveViewset(GenericViewSet, RetrieveModelMixin):
    queryset = Announcement.objects.filter(is_available=True)
    serializer_class = AnnouncementSerializer
    lookup_field = "id"
    schema = AutoSchema(
        tags=['Announcement'],
    )

    def retrieve(self, request, *args, **kwargs):
        """
        获取id=?的公告
        """
        return super(AnnouncementRetrieveViewset, self).retrieve(request, *args, **kwargs)

    @action(methods=["GET"], detail=True, url_path="visit")
    def visit_database(self, request, id, **kwarg):
        """
        标记访问了该数据库

        每个ip只能标记一次，第二次访问会返回400
        """
        ip = request.META.get("REMOTE_ADDR")
        data = {"ip": ip, "announcement": id}
        if AnnouncementVisit.objects.filter(ip=ip).count() > 0:
            return Response({"msg": "You have visited the page"}, status=400)
        save_data = AnnouncementVisitSerializer(data=data)
        save_data.is_valid(raise_exception=True)
        save_data.save()
        return Response()
