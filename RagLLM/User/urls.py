from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

app_name = "User"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("folders/", CreateFolderView.as_view(), name="create_folder"),
    path("folders/<int:id>/", ModifyFolderView.as_view(), name="update_folder"),
]
