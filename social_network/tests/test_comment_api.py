from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from social_network.models import Post, Commentary
from social_network.serializers import CommentarySerializer


class UnauthenticatedCommentaryApiTests(TestCase):
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

        commentary = Commentary.objects.create(
            owner=self.user,
            post=post,
            content="Some comment text"
        )

        url = reverse("social_network:commentary-detail", args=[commentary.id])
        res = self.client.get(url, {"post_id": post.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCommentaryApiTests(TestCase):
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
            owner=self.user,
            title="Test post",
            content="Test post content"
        )

    def test_create_commentary(self):
        payload = {
            "content": "Some commentary text",
        }
        create_url = reverse("social_network:commentary-list") + f"?post_id={self.post.id}"
        res = self.client.post(create_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        commentary = Commentary.objects.get(id=res.data["id"])
        self.assertEqual(payload["content"], commentary.content)

    def test_get_commentary(self):
        comment_num = 3
        for num in range(comment_num):
            Commentary.objects.create(
                content=f"Commentary #{num}",
                post=self.post,
                owner=self.user,
            )
        commentaries_url = reverse("social_network:commentary-list")
        res = self.client.get(commentaries_url, {"post_id": {self.post.id}})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), comment_num)

    def test_get_commentary_list(self):
        comment_num = 3
        for num in range(comment_num):
            Commentary.objects.create(
                content=f"Commentary #{num}",
                post=self.post,
                owner=self.user,
            )
        commentaries_url = reverse("social_network:commentary-list")
        res = self.client.get(commentaries_url, {"post_id": {self.post.id}})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), comment_num)

        commentaries = Commentary.objects.all()
        serializer = CommentarySerializer(commentaries, many=True)
        expected_data = serializer.data

        self.assertEqual(res.data, expected_data)

    def test_update_commentary(self):
        commentary = Commentary.objects.create(
            content=f"Initial content",
            post=self.post,
            owner=self.user,
        )
        payload = {
            "content": "Changes content text",
        }

        res = self.client.patch(
            reverse(
                "social_network:commentary-detail", args=[commentary.id]
            ),
            data=payload,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_commentary = Commentary.objects.get(id=commentary.id)

        self.assertEqual(updated_commentary.content, payload["content"])

    def test_delete_user(self):
        commentary = Commentary.objects.create(
            content=f"Initial content",
            post=self.post,
            owner=self.user,
        )
        res = self.client.delete(
            reverse(
                "social_network:commentary-detail", args=[commentary.id]
            ),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
