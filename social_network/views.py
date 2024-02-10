from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from social_network.models import User
from social_network.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_network.serializers import UserSerializer


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
