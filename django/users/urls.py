from django.urls import path
from .views import user_profile, user_login

urlpatterns = [
    path("profile/", user_profile, name="profile"),
    path("login/", user_login, name="login"),
]
