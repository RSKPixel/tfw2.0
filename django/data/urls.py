from django.urls import path
from .views import get_instruments

urlpatterns = [
    path("instruments/", get_instruments, name="instruments"),
]
