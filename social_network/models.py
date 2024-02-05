import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


def user_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    followed_users = models.ManyToManyField(
        "self",
        blank=True,
        null=True,
        symmetrical=False,
        related_name="followed_by"
    )
    profile_picture = models.ImageField(
        null=True, blank=True, upload_to=user_image_file_path
    )
    bio = models.TextField()

    class Meta:
        ordering = ["username"]


class Post(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="post_like")

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        return f"{self.title}"

    def number_of_likes(self):
        return self.likes.count()


class Commentary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commentaries"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="commentaries"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    class Meta:
        ordering = ["-created_time"]
        verbose_name_plural = "commentaries"

    def __str__(self):
        return f"{self.user} {self.created_time}"
