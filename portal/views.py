from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from .models import *
from .serializers import *
from rest_framework.decorators import action, api_view
from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.schemas.openapi import AutoSchema


class DatabaseListFilter(filters.FilterSet):
    cn_category = filters.CharFilter(field_name="category__cn_name", lookup_expr="iexact", label="分类名（中文）")
    cn_source = filters.CharFilter(field_name="source__cn_name", lookup_expr="iexact", label="来源（中文）")
    cn_subject = filters.CharFilter(field_name="subject__cn_name", lookup_expr='iexact', label="学科（中文）")
    en_category = filters.CharFilter(field_name="category__en_name", lookup_expr="iexact", label="分类名（英文）")
    en_source = filters.CharFilter(field_name="source__en_name", lookup_expr="iexact", label="来源（英文）")
    en_subject = filters.CharFilter(field_name="subject__en_name", lookup_expr='iexact', label="学科（英文）")
    first_letter = filters.CharFilter(method="filter_by_first_letter", label='第一个字母')

    def filter_by_first_letter(self, queryset, name, value, *args, **kwargs):
        if len(value) == 1 and value.isalpha():
            return queryset.filter(en_name__istartswith=value)
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
            Q(cn_name__icontains=key) | Q(en_name__icontains=key) | Q(en_content__icontains=key) | Q(
                cn_content__icontains=key)).all()
        return Response(DatabaseGeneralSerializer(results, many=True).data)


class DatabaseRetrieveViewset(GenericViewSet, RetrieveModelMixin):
    queryset = Database.objects.filter(is_available=True)
    serializer_class = DatabaseSerializer
    lookup_field = "id"
    schema = AutoSchema(
        tags=['Database'],
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


from datetime import date


@api_view(['POST'])
def create_feedback(request: Request):
    """
    新建一个反馈

    每个ip每天可以新建2个反馈
    """
    data = dict(request.data)
    ip = request.META.get("REMOTE_ADDR")
    data["ip"] = ip
    today = date.today()
    if Feedback.objects.filter(create_time__year=today.year, create_time__month=today.month, create_time__day=today.day,
                               ip=ip).count() > 2:
        return Response({"msg": "You can feedback at largest 3 times a day"}, status=403)
    save_data = FeedbackSerializer(data=data)
    save_data.is_valid(raise_exception=True)
    save_data.save()
    return Response(save_data.data, status=201)


class AnnouncementFilter(filters.FilterSet):
    has_database = filters.CharFilter(method='has_database',label="是否关联数据库")

    def has_database(self, queryset: Announcement.objects.all(), name, value, *args, **kwargs):
        check = False
        if value.strip().lower() == "true":
            check = True
        return queryset.filter(database_isnull=check)


class AnnouncementViewset(GenericViewSet, ListModelMixin):
    queryset = Announcement.objects.filter(is_available=True)
    serializer_class = AnnouncementSerializer
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
        """
        return super(AnnouncementViewset, self).list(request, *args, **kwargs)


    @action(methods=["GET"], detail=False, url_path="search")
    def search_announcement(self, request, *args, **kwarg):
        """
        搜索公告。搜中英文内容和标题。
        """
        queryset = self.filter_queryset(self.get_queryset())
        key = request.query_params.get("key", "")
        results = queryset.filter(
            Q(cn_title__icontains=key) | Q(en_title__icontains=key) | Q(en_content__icontains=key) | Q(
                cn_content__icontains=key)).all()
        return Response(AnnouncementSerializer(results, many=True).data)


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