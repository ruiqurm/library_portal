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
        exclude = ('id',)


class DatabaseSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseSource
        exclude = ('id',)


class DatabaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseCategory
        exclude = ('id',)


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


class DatabaseSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()
    category = DatabaseCategorySerializer()
    source = DatabaseSourceSerializer()
    subject = DatabaseSubjectSerializer(many=True)

    class Meta:
        model = Database
        fields = "__all__"

    def to_representation(self, instance: Database):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = DatabaseVisit.objects.filter(database=instance).count()
        return serialized_data


class DatabaseVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseVisit
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):
    publisher = MyUserSerializer()

    # visits = serializers.IntegerField(read_only=True)
    class Meta:
        model = Announcement
        fields = "__all__"
        extra_kwargs = {'visit': {'read_only': True}}

    def to_representation(self, instance: Announcement):
        """
        查一下访问量
        """
        serialized_data = super().to_representation(instance)
        serialized_data["visit"] = AnnouncementVisit.objects.filter(announcement=instance).count()
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
    class Meta:
        model = Announcement
        fields = "__all__"


class DatabaseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = "__all__"


class UploadSerializer(serializers.Serializer):
    MAX_SIZE = 1024
    id = serializers.IntegerField()
    obj = serializers.ChoiceField(("db", "an",))
    def validate(self, data):
        if data["file"].size > self.MAX_SIZE:
            raise ValidationError(f"size too big(limit {self.MAX_SIZE} Byte)")
        return data
    def to_representation(self, instance:Union[File,Image]):
        return {
            "id":instance.id,
            "url":instance.file.url
        }

    def to_internal_value(self, data):
        obj = None
        if int(data["id"]) <0:
            raise Exception(f"id >= 0")
        try:
            if data["obj"] == "db":
                obj = Database.objects.get(id=data["id"])
            elif data["obj"] == "an":
                obj = Announcement.objects.get(id=data["id"])
            else:
                raise Exception("Type not exist")
        except(Database.DoesNotExist,Announcement.DoesNotExist):
            raise ValidationError("does not exist object")
        return {"content_object": obj, "file": data["file"]}
    class Meta:
        fields = ("file","id","obj")

class UploadFileSerializer(UploadSerializer,serializers.ModelSerializer):
    MAX_SIZE = 52428800

    class Meta:
        model = File
        fields = UploadSerializer.Meta.fields


class UploadImageSerializer(UploadSerializer,serializers.ModelSerializer):
    MAX_SIZE = 20971520

    class Meta:
        model = File
        fields = UploadSerializer.Meta.fields

class FileSerializer(serializers.Serializer):
    def to_representation(self, instance:Image):
        if instance.content_type.name == "数据库":
            obj_name = "db"
        elif instance.content_type.name == "公告":
            obj_name = "an"
        else:
            obj_name = "unknow"
        return {
            "id":instance.id,
            "file":instance.file.path,
            "url":instance.file.url,
            "size":instance.file.size,
            "obj":obj_name,
            "obj_id":instance.object_id
        }