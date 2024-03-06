import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from social_network.models import Post
from social_network.serializers import PostSerializer


class UnauthenticatedPostApiTests(TestCase):
    def test_auth_required(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test1@test.com",
            "testpass",
        )

        post = Post.objects.create(
            owner=self.user,
            title="First_post",
            content="Some text",
        )

        url = reverse("social_network:post-detail", args=[post.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="bart_simpson@test.com",
            password="testpass",
            first_name="Bart",
            last_name="Simpson",
        )
        self.client.force_authenticate(self.user)

        self.post = Post.objects.create(
            owner=self.user, title="Test post", content="Test content"
        )

    def test_create_post(self):
        payload = {
            "owner": self.user.id,
            "title": "Test post",
            "content": "Test content",
            "published": True,
            "tags": [],
        }
        create_url = reverse("social_network:post-list")
        res = self.client.post(create_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(id=res.data["id"])
        self.assertEqual(payload["title"], post.title)
        self.assertEqual(payload["owner"], post.owner.id)

    def test_get_post(self):
        user_url = reverse("social_network:post-detail", args=[self.post.id])
        res = self.client.get(user_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_own_and_followed_users_posts_only(self):
        followed_user = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
            first_name="Brian",
            last_name="Griffin",
        )
        non_followed_user = get_user_model().objects.create_user(
            email="Lisa_Simpson@@test.com",
            password="testpass",
            first_name="Lisa",
            last_name="Simpson",
        )
        self.user.followed_users.add(followed_user)

        followed_user_post = Post.objects.create(
            owner=followed_user, title="Followed user's post", content="Test content"
        )
        non_followed_user_post = Post.objects.create(
            owner=non_followed_user,
            title="Non-followed user's post",
            content="Test content",
        )

        url = reverse("social_network:post-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        target_posts = [followed_user_post, self.post]
        target_posts_serializer = PostSerializer(target_posts, many=True)
        expected_data = target_posts_serializer.data

        self.assertEqual(res.data, expected_data)

        post_ids_in_res = [post["id"] for post in res.data]

        self.assertNotIn(non_followed_user_post.id, post_ids_in_res)

    def test_filter_by_tag(self):
        target_post = Post.objects.create(
            title="Target post",
            content="Test content",
            owner=self.user,
        )
        target_post.tags.add("family")

        url = reverse("social_network:post-list")
        res = self.client.get(url, {"tag_slug": "family"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        post_ids_in_res = [post["id"] for post in res.data]
        self.assertNotIn(self.post.id, post_ids_in_res)

        expected_tags = [tag.slug for tag in target_post.tags.all()]
        self.assertEqual(res.data[0]["tags"], expected_tags)

    def test_like_post_if_not_liked(self):
        followed_user = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
        )
        post = Post.objects.create(
            title="Test post",
            content="Test content",
            owner=followed_user,
        )
        self.user.followed_users.add(followed_user)
        res = self.client.post(
            reverse("social_network:post-detail", args=[post.id]) + f"like-unlike/"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, post.likes.all())

    def test_unlike_post_if_liked(self):
        followed_user = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
        )
        post = Post.objects.create(
            title="Test post",
            content="Test content",
            owner=followed_user,
        )
        self.user.followed_users.add(followed_user)
        post.likes.add(self.user)

        res = self.client.post(
            reverse("social_network:post-detail", args=[post.id]) + f"like-unlike/"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user, post.likes.all())

    def test_upload_image(self):
        """Test uploading an image to post"""
        url = (
            reverse("social_network:post-detail", args=[self.post.id])
            + f"upload-image/"
        )

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        for image in self.post.images.all():
            self.assertTrue(os.path.exists(image.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = (
            reverse("social_network:post-detail", args=[self.post.id])
            + f"upload-image/"
        )
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_post_detail(self):
        url = (
            reverse("social_network:post-detail", args=[self.post.id])
            + f"upload-image/"
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("image", res.data.keys())

    def test_update_post(self):
        payload = {"content": "New content text", "published": True}

        res = self.client.patch(
            reverse("social_network:post-detail", args=[self.post.id]),
            data=payload,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_post = Post.objects.get(id=self.post.id)

        self.assertEqual(updated_post.content, payload["content"])

    def test_delete_user(self):
        res = self.client.delete(
            reverse("social_network:user-detail", args=[self.post.id]),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
