from rest_framework import generics, status, mixins
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
