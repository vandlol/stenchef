from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "meta"
urlpatterns = [
    path("m/", views.home, name="meta-home"),
]
