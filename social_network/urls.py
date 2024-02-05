from django.urls import path

from social_network.views import CreateUserView

app_name = "social_network"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
]
