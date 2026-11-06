from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("api/generate", views.generate),
    path("api/solve", views.solve),
    path("api/batch", views.batch),
    path("api/detect", views.detect),
    path("api/verify", views.verify),
    path("api/stats/", views.get_stats),
]