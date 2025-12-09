from django.urls import path, include

urlpatterns = [
    path("signals/", include("signals.urls")),
    path("data/", include("data.urls")),
    path("zerodha/", include("zerodha.urls")),
    path("users/", include("users.urls")),
]
