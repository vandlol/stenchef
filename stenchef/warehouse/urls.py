from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "warehouse"

urlpatterns = [
    path("", lambda request: redirect("w/", permanent=True)),
    path("warehouse/", lambda request: redirect("w/", permanent=True)),
    path(
        "w/",
        include(
            [
                path("", views.HomePageView.as_view(), name="home"),
                path("about/", views.AboutPageView.as_view(), name="about"),
            ]
        ),
    ),
]

