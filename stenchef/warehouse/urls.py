from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "warehouse"

containers = [
    path("create/", views.ContainerCreateView.as_view(), name="ccreate",),
    # path("delete/", views.ContainerDeleteView, name="cdelete",),
    path("type/create/", views.ContainerTypeCreateView.as_view(), name="ctcreate",),
    # path("type/delete/", views.ContainerTypeDeleteView, name="ctdelete",),
]

urlpatterns = [
    path("", lambda request: redirect("w/", permanent=True)),
    path("warehouse/", lambda request: redirect("w/", permanent=True)),
    path(
        "w/",
        include(
            [
                path("", views.HomePageView.as_view(), name="home"),
                path("about/", views.AboutPageView.as_view(), name="about"),
                path("container/", include(containers)),
            ]
        ),
    ),
]
