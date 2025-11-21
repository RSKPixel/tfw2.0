from django.urls import path
from .views import profile, fetch_positions

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("positions/", fetch_positions, name="positions"),
]
