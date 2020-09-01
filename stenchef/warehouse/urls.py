from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "warehouse"

urlpatterns = [
    path("warehouse/", lambda request: redirect("w/", permanent=True)),
    path(
        "w/",
        include(
            [
                path("", views.home, name="home"),
                path("w/about/", views.about, name="about"),
            ]
        ),
    ),
]

