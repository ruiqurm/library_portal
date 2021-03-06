from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from uuid import uuid4
import os

"""
用户拓展
"""

if not os.path.exists("media"):
    from pathlib import Path

    Path("media").mkdir(parents=True, exist_ok=True)


def rename_file(instance, filename):
    # upload_to = 'media'
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid4().hex, ext)
    return filename


class File(models.Model):
    name = models.TextField(verbose_name="文件名")
    file = models.FileField(upload_to=rename_file, verbose_name="文件")
    type = models.CharField(choices=(("image","图片"), ("file","文件")), verbose_name="类型",max_length=8)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_static = models.BooleanField(verbose_name="是否不与其他对象绑定",default=False)
    def __str__(self):
        return self.name


# class Image(models.Model):
#     file = models.ImageField(upload_to=rename_file)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#
#     def __str__(self):
#         return self.file.name


class MyUser(AbstractUser):
    avatar = models.ImageField(verbose_name="头像", blank=True, null=True, upload_to=rename_file)
    def __str__(self):
        return f"{self.username}"


class DatabaseSubject(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")

    class Meta:
        verbose_name = "数据库学科"
        verbose_name_plural = verbose_name
        unique_together = ("name",)

    def __str__(self):
        return f"{self.name}"


class DatabaseSource(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")

    class Meta:
        verbose_name = "数据库来源"
        verbose_name_plural = verbose_name
        unique_together = ("name",)

    def __str__(self):
        return f"{self.name}"


class DatabaseCategory(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")

    class Meta:
        verbose_name = "数据库分类"
        verbose_name_plural = verbose_name
        unique_together = ("name",)

    def __str__(self):
        return f"{self.name}"


class Database(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(verbose_name="资源名称")
    category = models.ForeignKey(DatabaseCategory, verbose_name="类别", on_delete=models.SET_NULL, null=True,blank=True)
    source = models.ForeignKey(DatabaseSource, verbose_name="来源", on_delete=models.SET_NULL, null=True,blank=True)
    subject = models.ManyToManyField(DatabaseSubject, verbose_name="学科",null=True,blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # visits = models.IntegerField(verbose_name="总访问量", default=0)
    publisher = models.ForeignKey(MyUser, verbose_name="发布者", on_delete=models.SET_NULL, null=True)
    is_Chinese = models.BooleanField(verbose_name="是否为中文数据库")
    is_available = models.BooleanField(verbose_name="是否可见")
    is_on_trial = models.BooleanField(verbose_name="是否在试用期")
    on_trial = models.DateTimeField(verbose_name="试用期", blank=True, null=True)
    content = models.TextField(verbose_name="内容", blank=True)

    class Meta:
        verbose_name = "数据库"
        verbose_name_plural = verbose_name
        ordering = ['-update_time', '-create_time']
        unique_together = ("name",)

    def __str__(self):
        return f"{self.name} "


class DatabaseVisit(models.Model):
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    date = models.DateField(verbose_name="日期", auto_now=True)
    database = models.ForeignKey(Database, verbose_name="关联数据库", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "数据库访问IP记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.date.strftime('%Y-%m-%d, %H:%M:%S')}]{self.ip} 访问{self.database.name}"


class Feedback(models.Model):
    nickname = models.CharField(verbose_name="用户名", max_length=64)
    email = models.EmailField(verbose_name="邮件")
    message = models.TextField(verbose_name="反馈")
    create_time = models.DateTimeField(verbose_name="发送时间", auto_now_add=True)
    ip = models.GenericIPAddressField(verbose_name="IP地址")

    class Meta:
        verbose_name = "反馈"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.ip} 内容:{self.message[:30]}"
class AnnouncementTag(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")

    class Meta:
        verbose_name = "公告分类"
        verbose_name_plural = verbose_name
        unique_together = ("name",)

    def __str__(self):
        return f"{self.name}"

class Announcement(models.Model):
    title = models.TextField(verbose_name="标题")
    publisher = models.ForeignKey(MyUser, verbose_name="发布者", null=True, on_delete=models.SET_NULL)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    content = models.TextField(verbose_name="内容", blank=True)
    database = models.ForeignKey(Database, verbose_name="关联数据库", on_delete=models.CASCADE, null=True, blank=True)
    is_available = models.BooleanField(verbose_name="是否有效")
    stick = models.BooleanField(default=False,verbose_name="置顶")
    contact = models.TextField(default="",blank=True,verbose_name="联系方式")
    tags = models.ForeignKey(AnnouncementTag,on_delete=models.SET_NULL,verbose_name="分类",null=True,blank=True)
    class Meta:
        ordering = ['-update_time', '-create_time']
        verbose_name = "公告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.publisher.username} {self.title}"


class AnnouncementVisit(models.Model):
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    date = models.DateField(verbose_name="日期", auto_now=True)
    announcement = models.ForeignKey(Announcement, verbose_name="关联公告", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "公告访问IP记录"
        verbose_name_plural = verbose_name

CONTENTTYPE_DATABASE_ID = 8
CONTENTTYPE_ANNOUNCEMENT_ID = 7

# CONTENTTYPE_DATABASE_ID = ContentType.objects.get(model='database').id
# CONTENTTYPE_ANNOUNCEMENT_ID = ContentType.objects.get(model='announcement').id