from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from social_network.models import Post, PostImage, Commentary


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id", "first_name", "last_name", "email", "password", "is_staff",
            "followed_users", "profile_picture", "bio",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image")


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id", "owner", "title", "content", "created_time", "tags",
            "images", "published", "publish_time",
        )
        read_only_fields = ("id", "owner", "likes",)

    def validate(self, data):
        if not data.get("published") and data.get("publish_time") is None:
            raise ValidationError
        return data


class CommentarySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Commentary
        fields = ("id", "owner", "created_time", "content")
        read_only_fields = ("created_time",)
