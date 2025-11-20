from django.urls import path
from .views import get_instruments, get_eod_data, fetch_n_save

urlpatterns = [
    path("instruments/", get_instruments, name="instruments"),
    path("eod/", get_eod_data, name="eod_data"),
    path("fetch-n-save/", fetch_n_save, name="fetch_n_save"),
]
