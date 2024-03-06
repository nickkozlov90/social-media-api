from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from social_network.models import Post
from social_network.serializers import UserSerializer, PostSerializer


class UnauthenticatedUserApiTests(TestCase):
    def test_auth_required(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test1@test.com",
            "testpass",
        )

        user_url = reverse("social_network:user-detail", args=[self.user.id])
        res = self.client.get(user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user(self):
        payload = {
            "email": "test1@test.com",
            "password": "testpass",
            "bio": "Test text for bio",
        }
        create_url = reverse("social_network:create")
        res = self.client.post(create_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=res.data["id"])
        for key in payload.keys():
            if key != "password":
                self.assertEqual(payload[key], getattr(user, key))


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="bart_simpson@test.com",
            password="testpass",
            first_name="Bart",
            last_name="Simpson",
        )
        self.client.force_authenticate(self.user)

    def test_get_user(self):
        user_url = reverse("social_network:user-detail", args=[self.user.id])
        res = self.client.get(user_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_search_user_by_first_name(self):
        target_user = get_user_model().objects.get(first_name="Bart")
        res = self.client.get(reverse("social_network:user-list"), {"first_name": target_user.first_name})
        self.assertIn(res.data[0]["first_name"], target_user.first_name)

    def test_search_user_by_last_name(self):
        target_user = get_user_model().objects.get(last_name="Simpson")
        res = self.client.get(reverse("social_network:user-list"), {"last_name": target_user.last_name})
        self.assertIn(res.data[0]["last_name"], target_user.last_name)

    def test_add_user_to_following_if_not_followed(self):
        followed_user = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
            first_name="Brian",
            last_name="Griffin",
        )

        res = self.client.post(reverse("social_network:user-detail", args=[followed_user.id]) + f"follow-unfollow-user/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.followed_users.filter(id=followed_user.id).exists())

    def test_remove_user_from_following_if_followed(self):
        followed_user = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
            first_name="Brian",
            last_name="Griffin",
        )
        self.user.followed_users.add(followed_user)

        res = self.client.post(
            reverse(
                "social_network:user-detail", args=[followed_user.id]
            ) + f"follow-unfollow-user/"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.followed_users.filter(id=followed_user.id).exists())

    def test_list_followings(self):
        brian_griffin = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
            first_name="Brian",
            last_name="Griffin",
        )

        lisa_simpson = get_user_model().objects.create_user(
            email="Lisa_Simpson@@test.com",
            password="testpass",
            first_name="Lisa",
            last_name="Simpson",
        )

        brian_griffin.followed_users.add(self.user)
        lisa_simpson.followed_users.add(self.user)

        res = self.client.get(
            reverse(
                "social_network:user-detail", args=[self.user.id]
            ) + f"followers/"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = UserSerializer(self.user.followed_by.all(), many=True)
        expected_data = serializer.data

        self.assertEqual(res.data, expected_data)

    def test_liked_posts_list(self):
        brian_griffin = get_user_model().objects.create_user(
            email="Brian_Griffin@test.com",
            password="testpass",
            first_name="Brian",
            last_name="Griffin",
        )

        first_post = Post.objects.create(
            owner=brian_griffin,
            title="First_post",
            content="Some text",
        )
        second_post = Post.objects.create(
            owner=brian_griffin,
            title="Second_post",
            content="Another text",
        )
        first_post.likes.add(self.user)
        second_post.likes.add(self.user)

        res = self.client.get(
            reverse(
                "social_network:user-detail", args=[self.user.id]
            ) + f"liked-posts/"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = PostSerializer(self.user.post_like.all(), many=True)
        expected_data = serializer.data

        self.assertEqual(res.data, expected_data)

    def test_update_user(self):
        payload = {
            "email": "lisa_simpson@test.com",
            "first_name": "Lisa"
        }

        res = self.client.patch(
            reverse(
                "social_network:user-detail", args=[self.user.id]
            ),
            data=payload,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_user = get_user_model().objects.get(id=self.user.id)

        self.assertEqual(updated_user.email, payload["email"])
        self.assertEqual(updated_user.first_name, payload["first_name"])

    def test_delete_user(self):
        res = self.client.delete(
            reverse(
                "social_network:user-detail", args=[self.user.id]
            ),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
