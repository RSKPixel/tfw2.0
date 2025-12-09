from django.urls import path
from . import views

urlpatterns = [
    path("trading-models/", views.trading_models, name="trading_models"),
]