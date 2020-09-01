from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "meta"
urlpatterns = [
    path("meta/", lambda request: redirect("m/", permanent=True)),
    path("m/", views.home, name="meta-home"),
]
