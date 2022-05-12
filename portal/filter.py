from django_filters import rest_framework as filters
from .models import Database,Announcement
from django.db.models import Q

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

class AnnouncementFilter(filters.FilterSet):
    has_database = filters.CharFilter(method='_has_database', label="是否关联数据库")
    database_id = filters.CharFilter(method='_database_id', label="数据库id")
    search = filters.CharFilter(method='_search', label="搜索数据库")
    stick = filters.BooleanFilter(method="_stick",label="置顶")
    tag = filters.CharFilter(field_name="tags__name", lookup_expr='iexact', label="分类")
    def _stick(self, queryset: Announcement.objects.all(), name, value: bool, *args, **kwargs):
        if value:
            return queryset.order_by("-stick")
        return queryset
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