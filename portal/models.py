from django.db import models
from django.contrib.auth.models import AbstractUser
from tinymce.models import HTMLField

"""
用户拓展
"""


class MyUser(AbstractUser):
    avatar = models.ImageField(verbose_name="头像", null=True)

    def __str__(self):
        return f"{self.username}"


class DatabaseSubject(models.Model):
    cn_name = models.CharField(max_length=128, verbose_name="中文名称")
    en_name = models.CharField(max_length=128, verbose_name="英文名称")

    class Meta:
        verbose_name = "数据库学科"
        verbose_name_plural = verbose_name
        unique_together = ("cn_name","en_name")

    def __str__(self):
        return f"{self.cn_name}  {self.en_name}"


class DatabaseSource(models.Model):
    cn_name = models.CharField(max_length=128, verbose_name="中文名称")
    en_name = models.CharField(max_length=128, verbose_name="英文名称")

    class Meta:
        verbose_name = "数据库来源"
        verbose_name_plural = verbose_name
        unique_together = ("cn_name","en_name")

    def __str__(self):
        return f"{self.cn_name}  {self.en_name}"


class DatabaseCategory(models.Model):
    cn_name = models.CharField(max_length=128, verbose_name="中文名称")
    en_name = models.CharField(max_length=128, verbose_name="英文名称")

    class Meta:
        verbose_name = "数据库分类"
        verbose_name_plural = verbose_name
        unique_together = ("cn_name","en_name")

    def __str__(self):
        return f"{self.cn_name}  {self.en_name}"


class Database(models.Model):
    id = models.AutoField(primary_key=True)
    cn_name = models.TextField(verbose_name="资源中文名称")
    en_name = models.TextField(verbose_name="资源英文名称")
    category = models.ForeignKey(DatabaseCategory, verbose_name="类别", on_delete=models.SET_NULL, null=True)
    source = models.ForeignKey(DatabaseSource, verbose_name="来源", on_delete=models.SET_NULL, null=True)
    subject = models.ManyToManyField(DatabaseSubject, verbose_name="学科", null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # visits = models.IntegerField(verbose_name="总访问量", default=0)
    publisher = models.ForeignKey(MyUser, verbose_name="发布者", on_delete=models.SET_NULL, null=True)
    is_Chinese = models.BooleanField(verbose_name="是否为中文数据库")
    is_available = models.BooleanField(verbose_name="是否可见")
    is_on_trial = models.BooleanField(verbose_name="是否在试用期")
    on_trial = models.DateTimeField(verbose_name="试用期", blank=True, null=True)
    cn_content = HTMLField(verbose_name="中文内容")
    en_content = HTMLField(verbose_name="英文内容")

    class Meta:
        verbose_name = "数据库"
        verbose_name_plural = verbose_name
        ordering = ['-update_time', '-create_time']
        unique_together = ("cn_name","en_name")

    def __str__(self):
        return f"{self.cn_name}  {self.en_name}"


class DatabaseVisit(models.Model):
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    date = models.DateField(verbose_name="日期", auto_now=True)
    database = models.ForeignKey(Database, verbose_name="关联数据库", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "数据库访问IP记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.date.strftime('%Y-%m-%d, %H:%M:%S')}]{self.ip} 访问{self.database.cn_name}  {self.database.cn_name}"


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


class Announcement(models.Model):
    cn_title = models.TextField(verbose_name="中文标题")
    en_title = models.TextField(verbose_name="英文标题")
    publisher = models.ForeignKey(MyUser, verbose_name="发布者", null=True, on_delete=models.SET_NULL)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # visits = models.IntegerField(verbose_name="访问量", default=0)
    cn_content = HTMLField(verbose_name="中文内容")
    en_content = HTMLField(verbose_name="英文内容")
    database = models.ForeignKey(Database, verbose_name="关联数据库", on_delete=models.CASCADE, null=True, blank=True)
    is_available = models.BooleanField(verbose_name="是否有效")

    class Meta:
        ordering = ['-update_time', '-create_time']
        verbose_name = "公告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.publisher.username} {self.cn_title}"


class AnnouncementVisit(models.Model):
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    date = models.DateField(verbose_name="日期", auto_now=True)
    announcement = models.ForeignKey(Announcement, verbose_name="关联公告", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "公告访问IP记录"
        verbose_name_plural = verbose_name
