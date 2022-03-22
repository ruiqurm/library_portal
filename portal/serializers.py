from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ["id","username","avatar"]

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
        exclude = ('cn_content', 'en_content')

    def to_representation(self, instance:Database):
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
    subject = DatabaseSubjectSerializer()
    class Meta:
        model = Database
        fields = "__all__"
    def to_representation(self, instance:Database):
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
    def to_representation(self, instance:Announcement):
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
    avatar = serializers.ImageField(read_only=True)
    class Meta:
        model = MyUser
        fields = ("id","username","is_superuser","first_name","last_name","email","is_active","avatar")

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ("username","password",)

    def save(self, **kwargs):
        self.validated_data["password"] = make_password(self.validated_data["password"])
        return super(UserCreateSerializer,self).save(**kwargs)


