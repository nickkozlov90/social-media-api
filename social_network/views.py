from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from taggit.models import Tag

from social_network.models import User, Post, Commentary
from social_network.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_network.serializers import (
    UserSerializer,
    PostSerializer,
    PostImageSerializer,
    CommentarySerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)
    queryset = User.objects.all()

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow-unfollow-user",
        permission_classes=[IsAuthenticated],
    )
    def follow_unfollow_user(self, request, pk=None):
        """Endpoint for following specific user"""
        following = self.get_object()
        follower = self.request.user
        if following not in follower.followed_users.all():
            follower.followed_users.add(following)
        else:
            follower.followed_users.remove(following)

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="followings",
        permission_classes=[IsAuthenticated],
    )
    def followings(self, request, pk):
        """Endpoint to retrieve followings of the user"""
        user = User.objects.get(id=pk)
        followings = user.followed_users.all()

        serializer = UserSerializer(followings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="followers",
        permission_classes=[IsAuthenticated],
    )
    def followers(self, request, pk):
        """Endpoint to retrieve followers of the user"""
        user = User.objects.get(id=pk)
        followers = user.followed_by.all()

        serializer = UserSerializer(followers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="posts",
        permission_classes=[IsAuthenticated],
    )
    def posts(self, request, pk):
        """Endpoint to retrieve post of the user"""
        user = User.objects.get(id=pk)
        posts = user.posts.filter(published=True)

        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="liked-posts",
        permission_classes=[IsAuthenticated],
    )
    def liked_posts(self, request, pk):
        """Endpoint to retrieve post that current user liked"""
        user = self.request.user
        liked_posts = user.post_like.all()

        serializer = PostSerializer(liked_posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # For documentation purposes only
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by user first name (ex. ?first_name=Bart)"
            ),
            OpenApiParameter(
                "last_name",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by user last name (ex. ?last_name=Simpson)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrIfAuthenticatedReadOnly,
    )
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(
            owner__in=[*user.followed_users.all(), user]
        ).filter(published=True)

        tag_slugs = self.request.query_params.getlist("tag_slug")

        if tag_slugs:
            tags = Tag.objects.filter(slug__in=tag_slugs)
            queryset = self.queryset.filter(tags__in=tags)
            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return PostImageSerializer

        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="like-unlike",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        """Endpoint for liking-unliking specific post"""
        post = self.get_object()
        serializer = PostSerializer(post)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        post.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific post"""
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(post_id=post.id)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # For documentation purposes only
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "tag_slugs",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by tags "
                            "(ex. ?tag_slug=simpsons&tag_slug=family)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentaryViewSet(ModelViewSet):
    serializer_class = CommentarySerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)
    queryset = Commentary.objects.all()

    def get_queryset(self):
        queryset = Commentary.objects.all()
        if self.action in ["retrieve", "list"]:
            post_id = self.request.query_params.get("post_id")
            queryset = queryset.filter(post__id=post_id)

            return queryset

        return queryset

    def perform_create(self, serializer):
        post_id = self.request.query_params.get("post_id")
        serializer.save(
            owner=self.request.user, post=Post.objects.get(id=post_id)
        )

    # For documentation purposes only
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "tag_id",
                type={"type": "number"},
                description="Filter by particular post (ex. ?post_id=1)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
