from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from social_network.models import User, Post
from social_network.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_network.serializers import UserSerializer, PostSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
            queryset = queryset.filter(
                first_name__icontains=first_name
            )

        if last_name:
            queryset = queryset.filter(
                last_name__icontains=last_name
            )

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
        posts = user.posts.all()

        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        followed_posts = Post.objects.filter(
            owner__in=user.followed_users.all()
        )

        return followed_posts
