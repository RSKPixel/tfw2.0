from django.urls import path
from . import views

urlpatterns = [
    path("trading-models/", views.trading_models, name="trading_models"),
    path("trading-signals/", views.trading_signals, name="trading_signals"),
]
