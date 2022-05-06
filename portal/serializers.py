from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *
from django.contrib.auth.hashers import make_password
from typing import Union

"""
Custome validator
"""


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ["id", "username", "avatar"]


class DatabaseSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseSubject
        fields = "__all__"


class DatabaseSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseSource
        fields = "__all__"


class DatabaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseCategory
        fields = "__all__"


class AnnouncementTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementTag
        fields = "__all__"


class DatabaseGeneralSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()
    category = DatabaseCategorySerializer()
    source = DatabaseSourceSerializer()
    subject = DatabaseSubjectSerializer(many=True)

    class Meta:
        model = Database
        exclude = ('content',)

    def to_representation(self, instance: Database):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = DatabaseVisit.objects.filter(database=instance).count()
        return serialized_data


class DatabaseShortSerializer(serializers.ModelSerializer):
    """
    对于序列化，只包含id,名字，发布者的信息
    对于反序列化，只要求有id
    """
    publisher = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
     )
    class Meta:
        model = Database
        fields = ('id', 'publisher', 'name')
        extra_kwargs = {
            'name': {'read_only': True},
        }


class DatabaseSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()
    category = DatabaseCategorySerializer()
    source = DatabaseSourceSerializer()
    subject = DatabaseSubjectSerializer(many=True)

    class Meta:
        model = Database
        fields = "__all__"
        # extra_kwargs = {'visit': {'read_only': True}, 'files': {'read_only': True}, 'imgs': {'read_only': True}}

    def to_representation(self, instance: Database):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = DatabaseVisit.objects.filter(database=instance).count()
        files = File.objects.filter(content_type=CONTENTTYPE_ANNOUNCEMENT_ID, object_id=instance.id)
        serialized_data["files"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="file")]
        serialized_data["images"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="image")]
        return serialized_data


class DatabaseVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseVisit
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class AnnouncementListSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()

    # visits = serializers.IntegerField(read_only=True)
    class Meta:
        model = Announcement
        fields = "__all__"
        extra_kwargs = {'visit': {'read_only': True}, 'files': {'read_only': True}, 'imgs': {'read_only': True}}

    def to_representation(self, instance: Announcement):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = AnnouncementVisit.objects.filter(announcement=instance).count()
        # 返回详细的数据库内容
        if serialized_data["database"] is not None:
            serialized_data["database"] = DatabaseShortSerializer(Database.objects.get(id=serialized_data["database"])).data
        return serialized_data


class AnnouncementSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()

    # visits = serializers.IntegerField(read_only=True)
    class Meta:
        model = Announcement
        fields = "__all__"
        extra_kwargs = {'visit': {'read_only': True}, 'files': {'read_only': True}, 'imgs': {'read_only': True}}

    def to_representation(self, instance: Announcement):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = AnnouncementVisit.objects.filter(announcement=instance).count()
        files = File.objects.filter(content_type=CONTENTTYPE_ANNOUNCEMENT_ID, object_id=instance.id)
        serialized_data["files"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="file")]
        serialized_data["images"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="image")]
        # 返回详细的数据库内容
        if serialized_data["database"] is not None:
            serialized_data["database"] = DatabaseShortSerializer(Database.objects.get(id=serialized_data["database"])).data
        return serialized_data


class AnnouncementVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementVisit
        fields = "__all__"


"""
For admin
"""


class UserSerializer(serializers.ModelSerializer):
    MAX_AVATAR_SIZE = 4194304  # 4MB
    avatar = serializers.ImageField()

    def validate_avatar(self, image):
        if image.size > self.MAX_AVATAR_SIZE:
            raise ValidationError("File size too big(limit 4MB)")
        return image

    def to_representation(self, instance):
        response = super(UserSerializer, self).to_representation(instance)
        if instance.avatar:
            response['avatar'] = instance.avatar.url
        return response

    def update(self, instance: MyUser, validated_data):
        if instance.avatar:
            try:
                os.remove(instance.avatar.path)
            except Exception:
                pass
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = MyUser
        fields = ("id", "username", "is_superuser", "first_name", "last_name", "email", "is_active", "avatar")


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8)

    class Meta:
        model = MyUser
        fields = ("username", "password",)

    def save(self, **kwargs):
        self.validated_data["password"] = make_password(self.validated_data["password"])
        return super(UserCreateSerializer, self).save(**kwargs)


class AnnouncementAdminSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(many=True, allow_empty=True, write_only=True, read_only=False,
                                               queryset=File.objects.all())
    images = serializers.PrimaryKeyRelatedField(many=True, allow_empty=True, write_only=True, read_only=False,
                                                queryset=File.objects.all())
    publisher = serializers.HiddenField(default=serializers.CurrentUserDefault())
    def validate(self, data):
        self.context["files"] = []
        if "files" in data and isinstance(data["files"], list):
            self.context["files"].extend(data["files"])
            data.pop("files")
        if "images" in data and isinstance(data["images"], list):
            self.context["files"].extend(data["images"])
            data.pop("images")
        return data

    def save(self, **kwargs):
        item: Announcement = super().save(**kwargs)
        if "files" in self.context:
            l = []
            for file in self.context["files"]:
                file.content_object = item
                l.append(file)
            File.objects.filter(is_static=False).bulk_update(l, ("object_id", "content_type"))

    def to_representation(self, instance: Announcement):
        res = super().to_representation(instance)
        files = File.objects.filter(content_type=CONTENTTYPE_ANNOUNCEMENT_ID, object_id=instance.id)
        res["files"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="file", is_static=False)]
        res["images"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="image", is_static=False)]

        # 返回详细的数据库内容
        if res["database"] is not None:
            res["database"] = DatabaseShortSerializer(Database.objects.get(id=res["database"])).data
        return res

    class Meta:
        model = Announcement
        fields = "__all__"


class DatabaseAdminSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(many=True, allow_empty=True, write_only=True, read_only=False,
                                               queryset=File.objects.all())
    images = serializers.PrimaryKeyRelatedField(many=True, allow_empty=True, write_only=True, read_only=False,
                                                queryset=File.objects.all())
    publisher = serializers.HiddenField(default=serializers.CurrentUserDefault())
    def validate(self, data):
        self.context["files"] = []
        if "files" in data and isinstance(data["files"], list):
            self.context["files"].extend(data["files"])
            data.pop("files")
        if "images" in data and isinstance(data["images"], list):
            self.context["files"].extend(data["images"])
            data.pop("images")
        return data

    def save(self, **kwargs):
        item: Database = super().save(**kwargs)
        if "files" in self.context:
            l = []
            for file in self.context["files"]:
                file.content_object = item
                l.append(file)
            File.objects.filter(is_static=False).bulk_update(l, ("object_id", "content_type"))

    def to_representation(self, instance: Database):
        res = super().to_representation(instance)
        files = File.objects.filter(content_type=CONTENTTYPE_DATABASE_ID, object_id=instance.id)
        res["files"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="file", is_static=False)]
        res["images"] = [{
            "id": file.id,
            "name": file.name,
            "url": file.file.url,
        } for file in files.filter(type="image", is_static=False)]
        return res

    class Meta:
        model = Database
        fields = "__all__"


class UploadSerializer(serializers.ModelSerializer):
    MAX_FILE_SIZE = 52428800
    MAX_IMAGE_SIZE = 20971520

    # id = serializers.IntegerField()
    # obj = serializers.ChoiceField(("db", "an",))

    def validate(self, data):
        if data["type"] == "image" and data["file"].size > self.MAX_IMAGE_SIZE \
                or data["type"] == "file" and data["file"].size > self.MAX_FILE_SIZE:
            raise ValidationError(f"size too big")
        return data

    def to_representation(self, instance: File):
        return {
            "id": instance.id,
            "url": instance.file.url,
            "type": instance.type
        }

    class Meta:
        model = File
        fields = ("name", "file", "type", "is_static")


class FileSerializer(serializers.Serializer):
    def to_representation(self, instance: File):
        return {
            "id": instance.id,
            "name": instance.name,
            "file": instance.file.path,
            "url": instance.file.url,
            "size": instance.file.size,
            "type": instance.type,
            "class": instance.content_type.name if instance.content_type else None,
            "obj_id": instance.object_id if instance.content_type else None,
        }
